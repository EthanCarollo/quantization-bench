#!/usr/bin/env python3
"""Run the pinned IFBench test split five times on one MLX model variant."""

import argparse
import json
import statistics
import time
from pathlib import Path

import mlx.core as mx
from ifbench import instructions_registry
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
DATA_PATH = ROOT / "data" / "ifbench" / "IFBench_test.jsonl"
DATASET_REVISION = "2e8a48de45ff3bf41242f927254ca81b59ca3ae2"
SOURCE_REVISION = "1c40f0c10d9b5c5c2f10a175a28007ebb64f7f4d"
SEED_BASE = 44000


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def loose_following(row: dict, response: str) -> list[bool]:
    """Mirror the authors' prompt-level loose verifier variants."""
    lines = response.split("\n")
    response_remove_first = "\n".join(lines[1:]).strip()
    response_remove_last = "\n".join(lines[:-1]).strip()
    response_remove_both = "\n".join(lines[1:-1]).strip()
    candidates = [
        response,
        response.replace("*", ""),
        response_remove_first,
        response_remove_last,
        response_remove_both,
        response_remove_first.replace("*", ""),
        response_remove_last.replace("*", ""),
        response_remove_both.replace("*", ""),
    ]
    checks = []
    for index, instruction_id in enumerate(row["instruction_id_list"]):
        instruction_class = instructions_registry.INSTRUCTION_DICT[instruction_id]
        instruction = instruction_class(instruction_id)
        # HF's parquet conversion pads each kwargs object with null-valued keys for
        # unrelated verifier types. The verifier defaults are also None, so dropping
        # those keys preserves their meaning and avoids unexpected-keyword failures.
        verifier_kwargs = {key: value for key, value in row["kwargs"][index].items() if value is not None}
        instruction.build_description(**verifier_kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=row["prompt"])
        checks.append(
            any(candidate.strip() and instruction.check_following(candidate) for candidate in candidates)
        )
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--repetitions", type=int, choices=(5,), default=5)
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_dir = ROOT / "models" / f"{model_info['slug']}-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}; run scripts/convert_model.py first.")
    if not DATA_PATH.is_file():
        raise SystemExit(f"Missing IFBench data: {DATA_PATH}")
    rows = read_jsonl(DATA_PATH)
    if len(rows) != 300 or len({row["key"] for row in rows}) != 300:
        raise SystemExit(f"Expected 300 unique rows in the pinned IFBench test split; found {len(rows)}.")

    stem = f"{args.model}_ifbench_mlx_{args.bits}bit"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    run_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if output_path.exists() or run_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=0.0)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model_size_gib = sum(path.stat().st_size for path in model_dir.rglob("*") if path.is_file()) / (1024**3)

    warmup = tokenizer.apply_chat_template(
        [{"role": "user", "content": rows[0]["prompt"]}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(model, tokenizer, warmup, max_tokens=32, sampler=sampler):
        pass
    print("Warm-up complete (excluded from measured runs).", flush=True)

    with output_path.open("w", encoding="utf-8") as raw_file, run_path.open("w", encoding="utf-8") as summary_file:
        for repetition in range(1, args.repetitions + 1):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            prompt_scores = []
            instruction_scores = []
            for index, row in enumerate(rows, start=1):
                prompt = tokenizer.apply_chat_template(
                    [{"role": "user", "content": row["prompt"]}],
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
                fragments = []
                last = None
                started = time.perf_counter()
                for last in stream_generate(model, tokenizer, prompt, max_tokens=args.max_tokens, sampler=sampler):
                    fragments.append(last.text)
                elapsed = time.perf_counter() - started
                if last is None:
                    raise RuntimeError(f"Generation returned no tokens for IFBench item {row['key']}.")
                response = "".join(fragments).strip()
                checks = loose_following(row, response)
                prompt_score = float(all(checks))
                prompt_scores.append(prompt_score)
                instruction_scores.extend(checks)
                result = {
                    "benchmark": "ifbench",
                    "dataset_revision": DATASET_REVISION,
                    "verifier_revision": SOURCE_REVISION,
                    "model_key": args.model,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "runtime": "mlx-lm",
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                    "repetition": repetition,
                    "seed": seed,
                    "item_id": row["key"],
                    "prompt": row["prompt"],
                    "instruction_id_list": row["instruction_id_list"],
                    "response": response,
                    "follow_instruction_list": checks,
                    "follow_all_instructions": bool(all(checks)),
                    "prompt_loose_accuracy_100": prompt_score * 100.0,
                    "prompt_tokens": last.prompt_tokens,
                    "generation_tokens": last.generation_tokens,
                    "decode_tps": last.generation_tps,
                    "latency_seconds_including_prefill": elapsed,
                    "model_size_gib": model_size_gib,
                    "max_new_tokens": args.max_tokens,
                    "temperature": 0.0,
                    "thinking": False,
                }
                raw_file.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                raw_file.flush()
                print(
                    f"{args.model} {args.bits}-bit IFBench run {repetition}/{args.repetitions}, "
                    f"item {index}/{len(rows)}: loose={prompt_score:.0f}, "
                    f"{last.generation_tps:.1f} tok/s, {elapsed:.2f}s",
                    flush=True,
                )

            run_summary = {
                "benchmark": "ifbench",
                "model_key": args.model,
                "model_id": model_info["model_id"],
                "model_revision": model_info["revision"],
                "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                "repetition": repetition,
                "seed": seed,
                "n_examples": len(rows),
                "prompt_loose_accuracy_100": statistics.mean(prompt_scores) * 100.0,
                "instruction_loose_accuracy_100": statistics.mean(instruction_scores) * 100.0,
            }
            summary_file.write(json.dumps(run_summary, ensure_ascii=False, separators=(",", ":")) + "\n")
            summary_file.flush()
            print(
                f"Completed {args.model} {args.bits}-bit IFBench run {repetition}: "
                f"loose prompt accuracy={run_summary['prompt_loose_accuracy_100']:.2f}%",
                flush=True,
            )

    print(f"Wrote {output_path.relative_to(ROOT)} and {run_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
