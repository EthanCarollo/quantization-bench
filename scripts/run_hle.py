#!/usr/bin/env python3
"""Generate five text-only HLE runs for one MLX model variant."""

import argparse
import json
import math
import os
import time
from pathlib import Path

import mlx.core as mx
from datasets import load_dataset
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "data" / "hle" / "source.json").read_text(encoding="utf-8"))
SYSTEM_PROMPT = (
    "Your response should be in the following format:\n"
    "Explanation: {your explanation for your answer choice}\n"
    "Answer: {your chosen answer}\n"
    "Confidence: {your confidence score between 0% and 100% for your answer}"
)
SEED_BASE = 48000


def has_image(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, float) and math.isnan(value):
        return False
    return True


def text_only_questions():
    token = os.environ.get("HF_TOKEN") or True
    dataset = load_dataset(
        SOURCE["dataset_repository"],
        split=SOURCE["dataset_split"],
        revision=SOURCE["dataset_revision"],
        token=token,
        cache_dir=ROOT / "hf-cache" / "hle",
    )
    rows = [dict(row) for row in dataset if not has_image(row.get("image"))]
    if not rows or any(not row.get("id") or not row.get("question") or not row.get("answer") for row in rows):
        raise RuntimeError("Pinned HLE split returned no usable text-only rows or is missing required fields.")
    if len({row["id"] for row in rows}) != len(rows):
        raise RuntimeError("Pinned HLE text-only questions do not have unique ids.")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--max-tokens", type=int, default=8192)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_dir = ROOT / "models" / f"{model_info['slug']}-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}; run scripts/convert_model.py first.")

    try:
        rows = text_only_questions()
    except Exception as exc:
        raise SystemExit(
            f"Could not load the pinned HLE test split ({type(exc).__name__}: {exc}). "
            "The dataset is gated; accept its access terms and set HF_TOKEN."
        ) from exc

    stem = f"{args.model}_hle_mlx_{args.bits}bit"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    if output_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=0.0)
    model_size_gib = sum(path.stat().st_size for path in model_dir.rglob("*") if path.is_file()) / (1024**3)

    warmup = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": rows[0]["question"]},
        ],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(model, tokenizer, warmup, max_tokens=32, sampler=sampler):
        pass
    print(f"Warm-up complete; HLE text-only rows: {len(rows)}.", flush=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output:
        for repetition in range(1, 6):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            for position, row in enumerate(rows, start=1):
                prompt = tokenizer.apply_chat_template(
                    [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": row["question"]},
                    ],
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
                    raise RuntimeError(f"Generation returned no tokens for HLE item {row['id']}.")
                record = {
                    "benchmark": "hle",
                    "dataset_revision": SOURCE["dataset_revision"],
                    "verifier_revision": SOURCE["official_repository_revision"],
                    "model_key": args.model,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                    "repetition": repetition,
                    "seed": seed,
                    "question_id": row["id"],
                    "response": "".join(fragments).strip(),
                    "prompt_tokens": last.prompt_tokens,
                    "generation_tokens": last.generation_tokens,
                    "decode_tps": last.generation_tps,
                    "latency_seconds_including_prefill": elapsed,
                    "model_size_gib": model_size_gib,
                    "max_new_tokens": args.max_tokens,
                    "temperature": 0.0,
                    "thinking": False,
                }
                output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                output.flush()
                print(
                    f"{args.model} {args.bits}-bit HLE run {repetition}/5, item {position}/{len(rows)}: "
                    f"{last.generation_tps:.1f} tok/s, {elapsed:.2f}s",
                    flush=True,
                )
    print(f"Wrote {output_path.relative_to(ROOT)} with {len(rows) * 5} generations.")


if __name__ == "__main__":
    main()
