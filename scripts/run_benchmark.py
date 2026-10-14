#!/usr/bin/env python3
"""Run one five-repeat RoleBench subset/model/MLX quantization combination."""

import argparse
import json
import statistics
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load
from rouge_score.rouge_scorer import RougeScorer


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
BENCHMARK_DIRS = {
    "rolebench_generalization": "rolebench-generalization",
    "rolebench_role_specific": "rolebench-role-specific",
}
SEED_BASE = 42000
SYSTEM_TEMPLATE = (
    "You are {role}, your description is: {description}. Now please answer some questions to accurately "
    "show your personality traits! Your speaking style should fully imitate the personality role assigned "
    "to you! Please do not expose that you are an artificial intelligence model or a language model, you "
    "must always remember that you are only assigned one personality role. Don’t be verbose or too formal "
    "or polite when speaking."
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--benchmark", choices=BENCHMARK_DIRS, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--max-tokens", type=int, default=512)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_dir = ROOT / "models" / f"{model_info['slug']}-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}; run scripts/convert_model.py first.")
    dataset_dir = ROOT / "data" / BENCHMARK_DIRS[args.benchmark]
    data_path = dataset_dir / "rolebench.jsonl"
    if not data_path.is_file():
        raise SystemExit(f"Missing benchmark data: {data_path}; run scripts/prepare_rolebench_subset.py first.")
    rows = read_jsonl(data_path)
    if len(rows) != 10:
        raise SystemExit(f"Expected the pinned 10-item subset; found {len(rows)} rows.")

    output_stem = f"{args.model}_{args.benchmark}_mlx_{args.bits}bit"
    output_path = ROOT / "results" / f"{output_stem}.jsonl"
    run_summary_path = ROOT / "results" / f"{output_stem}_runs.jsonl"
    if output_path.exists() or run_summary_path.exists():
        raise SystemExit(f"Results already exist for {output_stem}; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=1.0, top_p=0.95, top_k=64)
    scorer = RougeScorer(["rougeL"], use_stemmer=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model_size_gib = sum(path.stat().st_size for path in model_dir.rglob("*") if path.is_file()) / (1024**3)

    first_row = rows[0]
    warmup_messages = [
        {
            "role": "system",
            "content": SYSTEM_TEMPLATE.format(role=first_row["role"], description=first_row["description"]),
        },
        {"role": "user", "content": first_row["question"]},
    ]
    warmup_prompt = tokenizer.apply_chat_template(
        warmup_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(model, tokenizer, warmup_prompt, max_tokens=min(args.max_tokens, 32), sampler=sampler):
        pass
    print("Warm-up complete (excluded from measured runs).", flush=True)

    with output_path.open("w", encoding="utf-8") as raw_file, run_summary_path.open("w", encoding="utf-8") as summary_file:
        for repetition in range(1, args.repetitions + 1):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            scores = []
            for index, row in enumerate(rows, start=1):
                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_TEMPLATE.format(role=row["role"], description=row["description"]),
                    },
                    {"role": "user", "content": row["question"]},
                ]
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
                fragments = []
                last = None
                started = time.perf_counter()
                for last in stream_generate(
                    model,
                    tokenizer,
                    prompt,
                    max_tokens=args.max_tokens,
                    sampler=sampler,
                ):
                    fragments.append(last.text)
                elapsed = time.perf_counter() - started
                if last is None:
                    raise RuntimeError(f"Generation returned no tokens for item {row['id']}.")
                response = "".join(fragments).strip()
                rouge_l_f1 = scorer.score(row["reference"], response)["rougeL"].fmeasure
                scores.append(rouge_l_f1)

                item_result = {
                    "benchmark": args.benchmark,
                    "dataset_revision": "a57ed54f9613921e4a5f1b63601a558cd5acf971",
                    "model_key": args.model,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "runtime": "mlx-lm",
                    "runtime_version": "0.32.0",
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                    "repetition": repetition,
                    "seed": seed,
                    "item_id": row["id"],
                    "role": row["role"],
                    "question": row["question"],
                    "reference": row["reference"],
                    "response": response,
                    "rouge_l_f1": rouge_l_f1,
                    "prompt_tokens": last.prompt_tokens,
                    "generation_tokens": last.generation_tokens,
                    "decode_tps": last.generation_tps,
                    "latency_seconds_including_prefill": elapsed,
                    "peak_memory_gib": last.peak_memory,
                    "model_size_gib": model_size_gib,
                    "max_new_tokens": args.max_tokens,
                    "temperature": 1.0,
                    "top_p": 0.95,
                    "top_k": 64,
                    "thinking": False,
                }
                raw_file.write(json.dumps(item_result, ensure_ascii=False, separators=(",", ":")) + "\n")
                raw_file.flush()
                print(
                    f"{args.model} {args.bits}-bit {args.benchmark} run {repetition}/{args.repetitions}, "
                    f"item {index}/{len(rows)}: ROUGE-L={rouge_l_f1:.4f}, "
                    f"{last.generation_tps:.1f} tok/s, {elapsed:.2f}s",
                    flush=True,
                )

            run_summary = {
                "benchmark": args.benchmark,
                "model_key": args.model,
                "model_id": model_info["model_id"],
                "model_revision": model_info["revision"],
                "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                "repetition": repetition,
                "seed": seed,
                "n_examples": len(scores),
                "macro_rouge_l_f1": statistics.mean(scores),
            }
            summary_file.write(json.dumps(run_summary, ensure_ascii=False, separators=(",", ":")) + "\n")
            summary_file.flush()
            print(f"Completed {args.model} {args.bits}-bit run {repetition}: macro ROUGE-L={run_summary['macro_rouge_l_f1']:.4f}", flush=True)

    print(f"Wrote {output_path.relative_to(ROOT)} and {run_summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
