#!/usr/bin/env python3
"""Apply the pinned LiveCodeBench execution checker in one disposable Docker sandbox per problem."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "data" / "livecodebench" / "source.json").read_text(encoding="utf-8"))
FILES = ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"]
RESULT_PREFIX = "__LIVE_CODE_BENCH_RESULT__"
IMAGE = "roleplay-bench-results/livecodebench-evaluator:28fef95"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def run_sandbox(row: dict, codes: list[str]) -> list[bool]:
    job = {
        "question_id": row["question_id"],
        "row": {
            "public_test_cases": row["public_test_cases"],
            "private_test_cases": row["private_test_cases"],
            "metadata": row["metadata"],
        },
        "codes": codes,
    }
    command = [
        "docker", "run", "--rm", "--interactive",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--memory=2g",
        "--cpus=2",
        "--pids-limit=64",
        "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=128m",
        IMAGE,
    ]
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(job, separators=(",", ":")),
            text=True,
            capture_output=True,
            timeout=1800,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"LiveCodeBench sandbox exceeded 30 minutes for {row['question_id']}") from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"Docker sandbox failed for {row['question_id']} (exit {completed.returncode}): "
            f"{completed.stderr[-1200:]}"
        )
    payloads = [line[len(RESULT_PREFIX):] for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if not payloads:
        raise RuntimeError(f"Docker sandbox returned no result for {row['question_id']}: {completed.stdout[-1200:]}")
    result = json.loads(payloads[-1])
    if result["question_id"] != row["question_id"] or len(result["candidates"]) != len(codes):
        raise RuntimeError(f"Malformed Docker evaluation result for {row['question_id']}.")
    for candidate in result["candidates"]:
        if not candidate.get("completed"):
            raise RuntimeError(f"Incomplete official checker result for {row['question_id']}.")
    return [bool(candidate["passed"]) for candidate in result["candidates"]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    args = parser.parse_args()

    stem = f"{args.model}_livecodebench_v6_mlx_{args.bits}bit"
    raw_path = ROOT / "results" / f"{stem}.jsonl"
    scored_path = ROOT / "results" / f"{stem}_scored.jsonl"
    runs_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if not raw_path.is_file():
        raise SystemExit(f"Missing generation file {raw_path}; run scripts/run_livecodebench.py first.")
    if scored_path.exists() or runs_path.exists():
        raise SystemExit(f"Scores already exist for {stem}; archive or remove them explicitly before rerunning.")

    generations = read_jsonl(raw_path)
    if len(generations) != SOURCE["examples"] * 5:
        raise SystemExit(f"Expected {SOURCE['examples'] * 5} generations in {raw_path.name}; found {len(generations)}.")
    by_question = {}
    for row in generations:
        by_question.setdefault(row["question_id"], {})[row["repetition"]] = row
    if len(by_question) != SOURCE["examples"] or any(set(reps) != {1, 2, 3, 4, 5} for reps in by_question.values()):
        raise SystemExit("Expected five generations for every one of the 1,055 unique problem ids.")

    run_scores = {repetition: [] for repetition in range(1, 6)}
    scored_path.parent.mkdir(parents=True, exist_ok=True)
    item_count = 0
    with scored_path.open("w", encoding="utf-8") as output:
        for path in source_paths():
            with path.open(encoding="utf-8") as dataset_file:
                for line in dataset_file:
                    problem = json.loads(line)
                    question_id = problem["question_id"]
                    generations_for_item = by_question.get(question_id)
                    if generations_for_item is None or any(
                        row["item_id"] != item_count for row in generations_for_item.values()
                    ):
                        raise RuntimeError(
                            f"Generation/source alignment mismatch at item {item_count}, question {question_id}."
                        )
                    codes = [generations_for_item[rep]["extracted_code"] for rep in range(1, 6)]
                    verdicts = run_sandbox(problem, codes)
                    for repetition, passed in enumerate(verdicts, start=1):
                        result = {
                            "benchmark": "livecodebench_v6",
                            "dataset_revision": SOURCE["dataset_revision"],
                            "verifier_revision": SOURCE["official_repository_revision"],
                            "model_key": args.model,
                            "model_id": REGISTRY[args.model]["model_id"],
                            "model_revision": REGISTRY[args.model]["revision"],
                            "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                            "item_id": item_count,
                            "question_id": problem["question_id"],
                            "repetition": repetition,
                            "pass_at_1": passed,
                            "score_100": 100.0 if passed else 0.0,
                        }
                        output.write(json.dumps(result, separators=(",", ":")) + "\n")
                        run_scores[repetition].append(100.0 if passed else 0.0)
                    output.flush()
                    item_count += 1
                    if item_count % 10 == 0:
                        print(f"Scored {item_count}/{SOURCE['examples']} problems for {stem}.", flush=True)

    if item_count != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} source rows; evaluated {item_count}.")
    with runs_path.open("w", encoding="utf-8") as file:
        for repetition, scores in run_scores.items():
            row = {
                "benchmark": "livecodebench_v6",
                "model_key": args.model,
                "model_id": REGISTRY[args.model]["model_id"],
                "model_revision": REGISTRY[args.model]["revision"],
                "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                "repetition": repetition,
                "n_examples": len(scores),
                "pass_at_1_100": statistics.mean(scores),
            }
            file.write(json.dumps(row, separators=(",", ":")) + "\n")

    print(f"Wrote {scored_path.relative_to(ROOT)} and {runs_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
