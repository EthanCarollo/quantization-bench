#!/usr/bin/env python3
"""Generate five pinned LiveCodeBench v6 samples for one MLX model variant."""

import argparse
import json
import time
from pathlib import Path

import mlx.core as mx
from huggingface_hub import hf_hub_download
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "data" / "livecodebench" / "source.json").read_text(encoding="utf-8"))
FILES = ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"]
SEED_BASE = 46000
SYSTEM_PROMPT = (
    "You are an expert Python programmer. You will be given a question (problem specification) "
    "and will generate a correct Python program that matches the specification and passes all tests."
)
FORMAT_WITH_STARTER = "You will use the following starter code to write the solution to the problem and enclose your code within delimiters."
FORMAT_WITHOUT_STARTER = (
    "Read the inputs from stdin solve the problem and write the answer to stdout "
    "(do not directly test on the sample inputs). Enclose your code within delimiters as follows. "
    "Ensure that when the python program runs, it reads inputs, runs the algorithm and writes output to STDOUT."
)


def source_paths() -> list[Path]:
    return [
        Path(
            hf_hub_download(
                repo_id=SOURCE["dataset_repository"],
                repo_type="dataset",
                filename=filename,
                revision=SOURCE["dataset_revision"],
                cache_dir=ROOT / "hf-cache" / "livecodebench-v6",
            )
        )
        for filename in FILES
    ]


def iter_problems(paths: list[Path]):
    key = 0
    kept_fields = (
        "question_title",
        "question_content",
        "platform",
        "question_id",
        "contest_date",
        "starter_code",
        "difficulty",
    )
    for path in paths:
        with path.open(encoding="utf-8") as file:
            for line in file:
                row = json.loads(line)
                yield key, {name: row[name] for name in kept_fields}
                key += 1


def make_user_prompt(row: dict) -> str:
    prompt = f"### Question:\n{row['question_content']}\n\n"
    if row.get("starter_code"):
        prompt += f"### Format: {FORMAT_WITH_STARTER}\n"
        prompt += f"```python\n{row['starter_code']}\n```\n\n"
    else:
        prompt += f"### Format: {FORMAT_WITHOUT_STARTER}\n"
        prompt += "```python\n# YOUR CODE HERE\n```\n\n"
    return prompt + "### Answer: (use the provided format with backticks)\n\n"


def extract_code_like_upstream(response: str) -> str:
    lines = response.split("\n")
    fence_lines = [index for index, line in enumerate(lines) if "```" in line]
    if len(fence_lines) < 2:
        return ""
    return "\n".join(lines[fence_lines[-2] + 1 : fence_lines[-1]])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--max-tokens", type=int, default=2000)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_dir = ROOT / "models" / f"{model_info['slug']}-mlx-{args.bits}bit"
    if not model_dir.is_dir():
        raise SystemExit(f"Missing converted model: {model_dir}; run scripts/convert_model.py first.")
    paths = source_paths()
    problems = list(iter_problems(paths))
    if len(problems) != SOURCE["examples"] or len({row["question_id"] for _, row in problems}) != len(problems):
        raise SystemExit(f"Expected {SOURCE['examples']} unique release_v6 problems; found {len(problems)}.")

    stem = f"{args.model}_livecodebench_v6_mlx_{args.bits}bit"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    if output_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive or remove them explicitly before rerunning.")

    model, tokenizer = load(str(model_dir))
    if not tokenizer.has_chat_template:
        raise SystemExit("The converted model tokenizer has no chat template.")
    sampler = make_sampler(temp=0.2, top_p=0.95)
    model_size_gib = sum(path.stat().st_size for path in model_dir.rglob("*") if path.is_file()) / (1024**3)

    first_prompt = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": make_user_prompt(problems[0][1])},
        ],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    mx.random.seed(SEED_BASE - 1)
    for _ in stream_generate(model, tokenizer, first_prompt, max_tokens=32, sampler=sampler):
        pass
    print("Warm-up complete (excluded from measured runs).", flush=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as raw_file:
        for repetition in range(1, args.repetitions + 1):
            seed = SEED_BASE + repetition - 1
            mx.random.seed(seed)
            for position, (item_id, row) in enumerate(problems, start=1):
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": make_user_prompt(row)},
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
                    raise RuntimeError(f"Generation returned no tokens for LiveCodeBench item {item_id}.")
                response = "".join(fragments).strip()
                result = {
                    "benchmark": "livecodebench_v6",
                    "dataset_revision": SOURCE["dataset_revision"],
                    "verifier_revision": SOURCE["official_repository_revision"],
                    "model_key": args.model,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "runtime": "mlx-lm",
                    "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                    "repetition": repetition,
                    "seed": seed,
                    "item_id": item_id,
                    "question_id": row["question_id"],
                    "response": response,
                    "extracted_code": extract_code_like_upstream(response),
                    "prompt_tokens": last.prompt_tokens,
                    "generation_tokens": last.generation_tokens,
                    "decode_tps": last.generation_tps,
                    "latency_seconds_including_prefill": elapsed,
                    "model_size_gib": model_size_gib,
                    "max_new_tokens": args.max_tokens,
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "thinking": False,
                }
                raw_file.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                raw_file.flush()
                print(
                    f"{args.model} {args.bits}-bit LiveCodeBench v6 run {repetition}/{args.repetitions}, "
                    f"item {position}/{len(problems)}: {last.generation_tps:.1f} tok/s, {elapsed:.2f}s",
                    flush=True,
                )

    print(f"Wrote {output_path.relative_to(ROOT)} with {len(problems) * args.repetitions} generations.")


if __name__ == "__main__":
    main()
