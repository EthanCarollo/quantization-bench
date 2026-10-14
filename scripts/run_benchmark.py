#!/usr/bin/env python3
"""Run the fixed RoleBench mini subset five times for one MLX quantization."""

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
MODEL_ID = "google/gemma-4-E2B-it"
MODEL_REVISION = "3e22461f65e89153144f8adb70e3b8c2cc9845a7"
GROUP_SIZE = 64
SEED_BASE = 42000
SYSTEM_TEMPLATE = (
    "You are {role}, your description is: {description}. Now please answer some questions to accurately "
    "show your personality traits! Your speaking style should fully imitate the personality role assigned "
    "to you! Please do not expose that you are an artificial intelligence model or a language model, you "
    "must always remember that you are only assigned one personality role. Don’t be verbose or too formal "
    "or polite when speaking."
)


def model_size_bytes(path: Path) -> int:
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def load_data(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--max-tokens", type=int, default=512)
    args = parser.parse_args()

    model_dir = ROOT / "models" / f"gemma-4-e2b-it-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}; run scripts/convert_model.py first.")
    data_path = ROOT / "data" / "rolebench-mini" / "rolebench_mini.jsonl"
    rows = load_data(data_path)
    if len(rows) != 10:
        raise SystemExit(f"Expected the pinned 10-item subset; found {len(rows)} rows.")

    output_path = ROOT / "results" / f"gemma4_e2b_it_mlx_{args.bits}bit.jsonl"
    run_summary_path = ROOT / "results" / f"gemma4_e2b_it_mlx_{args.bits}bit_runs.jsonl"
    if output_path.exists() or run_summary_path.exists():
        raise SystemExit(f"Results already exist for {args.bits}-bit; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=1.0, top_p=0.95, top_k=64)
    scorer = RougeScorer(["rougeL"], use_stemmer=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model_size_gib = model_size_bytes(model_dir) / (1024**3)

    warmup_row = rows[0]
    warmup_messages = [
        {"role": "system", "content": SYSTEM_TEMPLATE.format(role=warmup_row["role"], description=warmup_row["description"])},
        {"role": "user", "content": warmup_row["question"]},
    ]
    warmup_prompt = tokenizer.apply_chat_template(
        warmup_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(
        model,
        tokenizer,
        warmup_prompt,
        max_tokens=min(args.max_tokens, 32),
        sampler=sampler,
    ):
        pass
    print("Warm-up complete (excluded from measured runs).", flush=True)

    with output_path.open("w", encoding="utf-8") as raw_file, run_summary_path.open("w", encoding="utf-8") as summary_file:
        for repetition in range(1, args.repetitions + 1):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            scores = []
            for index, row in enumerate(rows, start=1):
                messages = [
                    {"role": "system", "content": SYSTEM_TEMPLATE.format(role=row["role"], description=row["description"])},
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
                rouge_l = scorer.score(row["reference"], response)["rougeL"].fmeasure
                scores.append(rouge_l)
                item_result = {
                    "benchmark": "RoleBench-mini-role-generalization-en",
                    "dataset_revision": "a57ed54f9613921e4a5f1b63601a558cd5acf971",
                    "model_id": MODEL_ID,
                    "model_revision": MODEL_REVISION,
                    "runtime": "mlx-lm",
                    "runtime_version": "0.32.0",
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": GROUP_SIZE},
                    "repetition": repetition,
                    "seed": seed,
                    "item_id": row["id"],
                    "role": row["role"],
                    "question": row["question"],
                    "reference": row["reference"],
                    "response": response,
                    "rouge_l_f1": rouge_l,
                    "prompt_tokens": last.prompt_tokens,
                    "generation_tokens": last.generation_tokens,
                    "prompt_tps": last.prompt_tps,
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
                    f"{args.bits}-bit run {repetition}/{args.repetitions}, item {index}/{len(rows)}: "
                    f"ROUGE-L={rouge_l:.4f}, {last.generation_tps:.1f} decode tok/s, {elapsed:.2f}s",
                    flush=True,
                )

            run_summary = {
                "model_id": MODEL_ID,
                "model_revision": MODEL_REVISION,
                "runtime": "mlx-lm",
                "runtime_version": "0.32.0",
                "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": GROUP_SIZE},
                "repetition": repetition,
                "seed": seed,
                "n_examples": len(scores),
                "macro_rouge_l_f1": statistics.mean(scores),
            }
            summary_file.write(json.dumps(run_summary, ensure_ascii=False, separators=(",", ":")) + "\n")
            summary_file.flush()
            print(f"Completed {args.bits}-bit run {repetition}: macro ROUGE-L={run_summary['macro_rouge_l_f1']:.4f}", flush=True)

    print(f"Wrote {output_path.relative_to(ROOT)} and {run_summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
