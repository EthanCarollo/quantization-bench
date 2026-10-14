#!/usr/bin/env python3
"""Score HLE generations with the authors' structured-output judge protocol."""

import argparse
import asyncio
import hashlib
import json
import math
import os
import statistics
from pathlib import Path
from typing import Literal

from datasets import load_dataset
from openai import AsyncOpenAI
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "data" / "hle" / "source.json").read_text(encoding="utf-8"))
JUDGE_PROMPT = """Judge whether the following [response] to [question] is correct or not based on the precise and unambiguous [correct_answer] below.

[question]: {question}

[response]: {response}

Your judgement must be in the format and criteria specified below:

extracted_final_answer: The final exact answer extracted from the [response]. Put the extracted answer as 'None' if there is no exact, final answer to extract from the response.

[correct_answer]: {correct_answer}

reasoning: Explain why the extracted_final_answer is correct or incorrect based on [correct_answer], focusing only on if there are meaningful differences between [correct_answer] and the extracted_final_answer. Do not comment on any background to the problem, do not attempt to solve the problem, do not argue for any answer different than [correct_answer], focus only on whether the answers match.

correct: Answer 'yes' if extracted_final_answer matches the [correct_answer] given above, or is within a small margin of error for numerical problems. Answer 'no' otherwise, i.e. if there if there is any inconsistency, ambiguity, non-equivalency, or if the extracted answer is incorrect.

confidence: The extracted confidence score between 0|%| and 100|%| from [response]. Put 100 if there is no confidence score available."""


class ExtractedAnswer(BaseModel):
    extracted_final_answer: str
    reasoning: str
    correct: Literal["yes", "no"]
    confidence: int
    strict: Literal[True]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_text_questions():
    token = os.environ.get("HF_TOKEN") or True
    dataset = load_dataset(
        SOURCE["dataset_repository"],
        split=SOURCE["dataset_split"],
        revision=SOURCE["dataset_revision"],
        token=token,
        cache_dir=ROOT / "hf-cache" / "hle",
    )
    rows = [dict(row) for row in dataset if not has_image(row.get("image"))]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise RuntimeError("Pinned HLE text-only split is empty or contains duplicate ids.")
    return rows


def has_image(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, float) and math.isnan(value):
        return False
    return True


async def judge_one(client, question: dict, response: str, model: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        question=question["question"],
        correct_answer=question["answer"],
        response=response,
    )
    completion = await client.beta.chat.completions.parse(
        model=model,
        max_completion_tokens=SOURCE["judge"]["max_completion_tokens"],
        messages=[{"role": "user", "content": prompt}],
        response_format=ExtractedAnswer,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("HLE judge returned no structured result.")
    return {
        "extracted_final_answer": parsed.extracted_final_answer,
        "reasoning": parsed.reasoning,
        "correct": parsed.correct,
        "confidence": parsed.confidence,
    }


async def main_async(args, rows: list[dict], generations: list[dict], scored_path: Path) -> None:
    question_by_id = {row["id"]: row for row in rows}
    generations_by_key = {}
    for item in generations:
        if (
            item.get("model_key") != args.model
            or item.get("quantization", {}).get("bits") != args.bits
            or item.get("dataset_revision") != SOURCE["dataset_revision"]
        ):
            raise RuntimeError("HLE generation metadata does not match the requested model, quantization, or dataset.")
        key = (item["question_id"], item["repetition"])
        if key in generations_by_key:
            raise RuntimeError(f"Duplicate HLE generation for {key}.")
        generations_by_key[key] = item
    expected = {(row["id"], repetition) for row in rows for repetition in range(1, 6)}
    if set(generations_by_key) != expected:
        raise RuntimeError("Expected exactly five complete HLE generations for every text-only question.")

    existing = read_jsonl(scored_path) if scored_path.exists() else []
    scored_by_key = {(row["question_id"], row["repetition"]): row for row in existing}
    if len(scored_by_key) != len(existing):
        raise RuntimeError("HLE scored cache contains duplicate question/repetition entries.")
    if any(row.get("judge_model") != args.judge for row in existing):
        raise RuntimeError("Existing HLE scores use another judge; archive them before changing --judge.")
    cache = {}
    for result in existing:
        cache[(result["question_id"], result["response_sha256"], result["judge_model"])] = {
            "extracted_final_answer": result["extracted_final_answer"],
            "reasoning": result["reasoning"],
            "correct": result["correct"],
            "confidence": result["confidence"],
        }

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for the official HLE judge; no judge calls were made.")
    client = AsyncOpenAI(api_key=api_key, timeout=300.0, max_retries=1)
    semaphore = asyncio.Semaphore(args.workers)
    pending_by_cache_key = {}
    reused = []
    for key, generation in generations_by_key.items():
        if key in scored_by_key:
            continue
        row = question_by_id[key[0]]
        response_hash = hashlib.sha256(generation["response"].encode("utf-8")).hexdigest()
        cache_key = (key[0], response_hash, args.judge)
        if cache_key in cache:
            judgment = cache[cache_key]
            result = make_score_row(generation, response_hash, judgment, args.judge)
            scored_by_key[key] = result
            reused.append((key, result))
        else:
            pending_by_cache_key.setdefault(cache_key, []).append((key, generation, row, response_hash))

    if pending_by_cache_key or reused:
        scored_path.parent.mkdir(parents=True, exist_ok=True)
        with scored_path.open("a", encoding="utf-8") as output:
            for _, result in reused:
                output.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                output.flush()

            async def one(entries):
                key, generation, row, response_hash = entries[0]
                async with semaphore:
                    judgment = await judge_one(client, row, generation["response"], args.judge)
                cache[(key[0], response_hash, args.judge)] = judgment
                return [
                    (entry_key, make_score_row(entry_generation, entry_hash, judgment, args.judge))
                    for entry_key, entry_generation, _, entry_hash in entries
                ]

            tasks = [asyncio.create_task(one(entries)) for entries in pending_by_cache_key.values()]
            for task in asyncio.as_completed(tasks):
                for key, result in await task:
                    scored_by_key[key] = result
                    output.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                    output.flush()
                    if len(scored_by_key) % 100 == 0:
                        print(f"Official HLE judge completed {len(scored_by_key)}/{len(expected)} rows.", flush=True)

    if set(scored_by_key) != expected:
        raise RuntimeError("HLE judge output is incomplete; rerun to resume from cached scored rows.")

    runs = []
    for repetition in range(1, 6):
        run = [scored_by_key[(row["id"], repetition)] for row in rows]
        correct_count = sum(item["correct"] == "yes" for item in run)
        runs.append(
            {
                "benchmark": "hle",
                "dataset_revision": SOURCE["dataset_revision"],
                "verifier_revision": SOURCE["official_repository_revision"],
                "model_key": args.model,
                "model_id": REGISTRY[args.model]["model_id"],
                "model_revision": REGISTRY[args.model]["revision"],
                "quantization": {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64},
                "judge_model": args.judge,
                "repetition": repetition,
                "n_examples": len(run),
                "accuracy_100": 100.0 * correct_count / len(run),
            }
        )

    runs_path = scored_path.with_name(scored_path.name.replace("_scored.jsonl", "_runs.jsonl"))
    runs_path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in runs), encoding="utf-8")
    values = [row["accuracy_100"] for row in runs]
    print(
        f"HLE text-only accuracy: {statistics.mean(values):.2f} ± {statistics.stdev(values):.2f} /100 "
        f"over {len(rows)} questions and five repetitions."
    )


def make_score_row(generation: dict, response_hash: str, judgment: dict, judge_model: str) -> dict:
    return {
        "benchmark": "hle",
        "question_id": generation["question_id"],
        "repetition": generation["repetition"],
        "response_sha256": response_hash,
        "judge_model": judge_model,
        "extracted_final_answer": judgment["extracted_final_answer"],
        "reasoning": judgment["reasoning"],
        "correct": judgment["correct"],
        "confidence": judgment["confidence"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    parser.add_argument("--judge", default=SOURCE["judge"]["default_model"])
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 2:
        raise SystemExit("The official HLE protocol requires at least two judge workers.")
    stem = f"{args.model}_hle_mlx_{args.bits}bit"
    raw_path = ROOT / "results" / f"{stem}.jsonl"
    scored_path = ROOT / "results" / f"{stem}_scored.jsonl"
    if not raw_path.is_file():
        raise SystemExit(f"Missing generation file {raw_path}; run scripts/run_hle.py first.")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for the official HLE judge; no judge calls were made.")
    try:
        rows = load_text_questions()
    except Exception as exc:
        raise SystemExit(
            f"Could not load gated HLE data ({type(exc).__name__}: {exc}); accept access and set HF_TOKEN."
        ) from exc
    asyncio.run(main_async(args, rows, read_jsonl(raw_path), scored_path))


if __name__ == "__main__":
    main()
