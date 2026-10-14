#!/usr/bin/env python3
"""Fetch the exact six raw files comprising pinned LiveCodeBench release_v6."""

import json
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data" / "livecodebench" / "source.json").read_text(encoding="utf-8"))
FILES = ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"]
CACHE_DIR = ROOT / "hf-cache" / "livecodebench-v6"


def main() -> None:
    paths = []
    for filename in FILES:
        path = Path(
            hf_hub_download(
                repo_id=SOURCE["dataset_repository"],
                repo_type="dataset",
                filename=filename,
                revision=SOURCE["dataset_revision"],
                cache_dir=CACHE_DIR,
            )
        )
        paths.append(path)
        print(f"Pinned {filename}: {path.stat().st_size:,} bytes", flush=True)

    count = 0
    for path in paths:
        with path.open(encoding="utf-8") as file:
            for line in file:
                json.loads(line)
                count += 1
    if count != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} release_v6 rows; found {count}.")
    print(f"Verified all {count} pinned LiveCodeBench v6 problem records.")


if __name__ == "__main__":
    main()
