#!/usr/bin/env python3
"""Generate five pinned LiveCodeBench v6 samples with a local GGUF model."""

import argparse
import json
import time
from pathlib import Path

from huggingface_hub import hf_hub_download

from gguf_server import LlamaServer


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
QUANTIZATION = {"format": "GGUF", "type": "Q4_K_M"}


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
    kept_fields = (
        "question_title", "question_content", "platform", "question_id",
        "contest_date", "starter_code", "difficulty",
    )
    item_id = 0
    for path in paths:
        with path.open(encoding="utf-8") as file:
            for line in file:
                row = json.loads(line)
                yield item_id, {name: row[name] for name in kept_fields}
                item_id += 1


def make_user_prompt(row: dict) -> str:
    prompt = f"### Question:\n{row['question_content']}\n\n"
    if row.get("starter_code"):
        prompt += f"### Format: {FORMAT_WITH_STARTER}\n```python\n{row['starter_code']}\n```\n\n"
    else:
        prompt += f"### Format: {FORMAT_WITHOUT_STARTER}\n```python\n# YOUR CODE HERE\n```\n\n"
    return prompt + "### Answer: (use the provided format with backticks)\n\n"


def extract_code_like_upstream(response: str) -> str:
    lines = response.split("\n")
    fence_lines = [index for index, line in enumerate(lines) if "```" in line]
    if len(fence_lines) < 2:
        return ""
    return "\n".join(lines[fence_lines[-2] + 1 : fence_lines[-1]])


def read_existing(path: Path) -> dict[tuple[int, int], dict]:
    if not path.is_file():
        return {}
    rows = {}
    with path.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                row = json.loads(line)
                rows[(row["repetition"], row["item_id"])] = row
    return rows


def load_problems() -> list[tuple[int, dict]]:
    cache_path = ROOT / "hf-cache" / "livecodebench-v6" / f"problems-{SOURCE['dataset_revision']}.jsonl"
    if cache_path.is_file():
        with cache_path.open(encoding="utf-8") as file:
            return [
                (row["item_id"], row["problem"])
                for line in file
                if line.strip()
                for row in [json.loads(line)]
            ]

    problems = list(iter_problems(source_paths()))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as file:
        for item_id, problem in problems:
            file.write(json.dumps({"item_id": item_id, "problem": problem}, separators=(",", ":")) + "\n")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--context-size", type=int, default=8192)
    parser.add_argument("--repetitions", type=int, choices=(1,), default=1)
    parser.add_argument("--max-tokens", type=int, default=2000)
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_path = ROOT / "models" / "gguf" / f"{args.model}_gguf_q4_k_m.gguf"
    stem = f"{args.model}_livecodebench_v6_gguf_q4_k_m"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    problems = load_problems()
    if len(problems) != SOURCE["examples"] or len({row["question_id"] for _, row in problems}) != len(problems):
        raise SystemExit(f"Expected {SOURCE['examples']} unique release_v6 problems; found {len(problems)}.")

    existing = read_existing(output_path)
    if any(key[0] not in range(1, 6) or key[1] not in range(len(problems)) for key in existing):
        raise SystemExit(f"Malformed partial output in {output_path}; move it aside before rerunning.")
    model_size_gib = model_path.stat().st_size / (1024**3)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with LlamaServer(model_path, port=args.port, context_size=args.context_size) as server:
        with output_path.open("a", encoding="utf-8") as raw_file:
            for repetition in range(1, args.repetitions + 1):
                for position, (item_id, row) in enumerate(problems, start=1):
                    key = (repetition, item_id)
                    if key in existing:
                        continue
                    started = time.perf_counter()
                    response_data = server.chat_completion(
                        {
                            "model": model_info["short_name"],
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": make_user_prompt(row)},
                            ],
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "max_tokens": args.max_tokens,
                            "seed": SEED_BASE + repetition * 100_000 + item_id,
                        }
                    )
                    elapsed = time.perf_counter() - started
                    choice = response_data["choices"][0]
                    message = choice["message"]
                    content = message.get("content") or ""
                    usage = response_data.get("usage") or {}
                    row_result = {
                        "benchmark": "livecodebench_v6",
                        "dataset_revision": SOURCE["dataset_revision"],
                        "verifier_revision": SOURCE["official_repository_revision"],
                        "model_key": args.model,
                        "model_id": model_info["model_id"],
                        "model_revision": model_info["revision"],
                        "runtime": "llama.cpp",
                        "quantization": QUANTIZATION,
                        "context_size": args.context_size,
                        "gpu_layers": server.gpu_layers,
                        "repetition": repetition,
                        "seed": SEED_BASE + repetition * 100_000 + item_id,
                        "item_id": item_id,
                        "question_id": row["question_id"],
                        "response": content.strip(),
                        "extracted_code": extract_code_like_upstream(content.strip()),
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "generation_tokens": usage.get("completion_tokens"),
                        "latency_seconds_including_prefill": elapsed,
                        "model_size_gib": model_size_gib,
                        "max_new_tokens": args.max_tokens,
                        "temperature": 0.2,
                        "top_p": 0.95,
                        "finish_reason": choice.get("finish_reason"),
                    }
                    raw_file.write(json.dumps(row_result, separators=(",", ":")) + "\n")
                    raw_file.flush()
                    existing[key] = row_result
                    if position % 25 == 0 or position == len(problems):
                        print(
                            f"Generated repetition {repetition}/5: {position}/{len(problems)} for {stem}.",
                            flush=True,
                        )

    if len(existing) != SOURCE["examples"] * args.repetitions:
        raise SystemExit(f"Incomplete generation file: {len(existing)}/{SOURCE['examples'] * args.repetitions} samples.")
    print(f"Wrote {output_path.relative_to(ROOT)} ({len(existing)} samples).")


if __name__ == "__main__":
    main()
