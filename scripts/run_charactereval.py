#!/usr/bin/env python3
"""Generate five MLX runs for the fixed CharacterEval subset."""

import argparse
import json
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "data" / "charactereval-mini"
SEED_BASE = 43000
MAX_NEW_TOKENS = 512


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def messages_for(row: dict, profile: dict) -> list[dict]:
    role = row["role"]
    conversations = []
    for line in row["context"].splitlines():
        if "：" in line:
            speaker, value = line.split("：", 1)
            conversations.append({"from": speaker, "value": value})
    if not conversations or conversations[-1]["from"] == role:
        raise ValueError(f"CharacterEval item {row['id']} has no final user turn.")

    first = conversations[0]
    greeting = f"好的！现在我来扮演{role}。"
    if first["from"] == role:
        greeting += f"我首先发话：{first['value']}"
    system = (
        f"{profile}\n现在请你扮演一个角色扮演专家。"
        f"请你根据上述信息扮演{role}进行对话。"
    )
    messages = [{"role": "system", "content": system}, {"role": "assistant", "content": greeting}]
    for index in range(1, len(conversations) - 1):
        current = conversations[index]
        previous = conversations[index - 1]
        if current["from"] == role:
            if previous["from"] == role:
                raise ValueError(f"CharacterEval item {row['id']} has consecutive character turns.")
            messages.append({"role": "user", "content": f"{previous['from']}：{previous['value']}"})
            messages.append({"role": "assistant", "content": f"{current['from']}：{current['value']}"})
    final = conversations[-1]
    messages.append({"role": "user", "content": f"{final['from']}：{final['value']}"})
    return messages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_dir = ROOT / "models" / f"{model_info['slug']}-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}")
    data_path = DATA_DIR / "charactereval.jsonl"
    profiles = json.loads((DATA_DIR / "character_profiles.json").read_text(encoding="utf-8"))
    rows = read_jsonl(data_path)
    if len(rows) != 12:
        raise SystemExit(f"Expected the pinned 12-item CharacterEval subset; found {len(rows)} rows.")

    output_stem = f"{args.model}_charactereval_mlx_{args.bits}bit"
    output_path = ROOT / "results" / f"{output_stem}.jsonl"
    if output_path.exists():
        raise SystemExit(f"Results already exist for {output_stem}; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=1.0, top_p=0.95, top_k=64)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    warmup_messages = messages_for(rows[0], profiles[rows[0]["role"]])
    warmup_prompt = tokenizer.apply_chat_template(
        warmup_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(model, tokenizer, warmup_prompt, max_tokens=32, sampler=sampler):
        pass
    print("CharacterEval warm-up complete (excluded from measured runs).", flush=True)

    with output_path.open("w", encoding="utf-8") as output:
        for repetition in range(1, 6):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            for index, row in enumerate(rows, start=1):
                prompt = tokenizer.apply_chat_template(
                    messages_for(row, profiles[row["role"]]),
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
                fragments = []
                started = time.perf_counter()
                last = None
                for last in stream_generate(model, tokenizer, prompt, max_tokens=MAX_NEW_TOKENS, sampler=sampler):
                    fragments.append(last.text)
                elapsed = time.perf_counter() - started
                if last is None:
                    raise RuntimeError(f"Generation returned no tokens for item {row['id']}.")
                full_response = "".join(fragments).strip()
                # CharacterEval's released pipeline scores only the first generated line.
                response = full_response.splitlines()[0].strip() if full_response else ""
                record = {
                    "benchmark": "charactereval",
                    "dataset_revision": "c3d44a6fc1790cc8c4b2fd7c01f0c72930655e0c",
                    "reward_model_revision": "e953da5f57b86db7adca3a2714b4c3720f5b96a2",
                    "model_key": args.model,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "runtime": "mlx-lm",
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                    "repetition": repetition,
                    "seed": seed,
                    "item_id": row["id"],
                    "role": row["role"],
                    "context": row["context"],
                    "metrics": row["metrics"],
                    "response": response,
                    "full_response": full_response,
                    "charactereval_scores": None,
                    "generation_tokens": last.generation_tokens,
                    "latency_seconds_including_prefill": elapsed,
                    "max_new_tokens": MAX_NEW_TOKENS,
                    "temperature": 1.0,
                    "top_p": 0.95,
                    "top_k": 64,
                    "thinking": False,
                }
                output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                output.flush()
                print(
                    f"{args.model} MLX-{args.bits}-bit CharacterEval run {repetition}/5, "
                    f"item {index}/{len(rows)}: {last.generation_tokens} tokens, {elapsed:.1f}s",
                    flush=True,
                )
    print(f"Wrote {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
