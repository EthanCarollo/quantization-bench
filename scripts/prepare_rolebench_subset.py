#!/usr/bin/env python3
"""Recreate deterministic 10-item RoleBench general and role-specific sets."""

import hashlib
import json
import random
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
REVISION = "a57ed54f9613921e4a5f1b63601a558cd5acf971"
BASE_URL = f"https://huggingface.co/datasets/ZenMoore/RoleBench/resolve/{REVISION}/"
SOURCES = {
    "profiles-eng/desc.json": "profiles",
    "rolebench-eng/role-generalization/general/test.jsonl": "generalization",
    "rolebench-eng/role-generalization/role_specific/test.jsonl": "role_specific",
}


def fetch(path: str) -> bytes:
    url = BASE_URL + quote(path, safe="/") + "?download=true"
    with urlopen(url, timeout=120) as response:
        return response.read()


def load_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


def make_subset(task: str, examples: list[dict], descriptions: dict, source_hashes: dict) -> None:
    rng = random.Random(42)
    rng.shuffle(examples)
    selected = []
    seen_roles = set()
    for example in examples:
        role = example["role"]
        if role in seen_roles or role not in descriptions:
            continue
        seen_roles.add(role)
        selected.append(example)
        if len(selected) == 10:
            break
    if len(selected) != 10:
        raise RuntimeError(f"Could not select ten distinct roles for {task}; found {len(selected)}")

    records = [
        {
            "id": index,
            "role": example["role"],
            "description": descriptions[example["role"]],
            "question": example["question"],
            "reference": example["generated"][0],
            "source_type": example.get("type", ""),
        }
        for index, example in enumerate(selected, start=1)
    ]

    data_dir = ROOT / "data" / f"rolebench-{task}"
    data_dir.mkdir(parents=True, exist_ok=True)
    local_path = data_dir / "rolebench.jsonl"
    local_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records),
        encoding="utf-8",
    )
    manifest = {
        "dataset": "ZenMoore/RoleBench",
        "dataset_revision": REVISION,
        "license": "Apache-2.0",
        "benchmark": f"RoleBench role-generalization {task} test subset",
        "selection": "Python random.Random(42), shuffled selected test file, first example for each distinct role until ten prompts",
        "source_file_sha256": source_hashes,
        "local_file": str(local_path.relative_to(ROOT)),
        "local_sha256": hashlib.sha256(local_path.read_bytes()).hexdigest(),
        "examples": len(records),
        "seed": 42,
        "reference_field": "generated[0]",
    }
    (data_dir / "source.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"task": task, "examples": len(records), "roles": [row["role"] for row in records]}, ensure_ascii=False))


def main() -> None:
    source = {path: fetch(path) for path in SOURCES}
    profiles_path = next(path for path, kind in SOURCES.items() if kind == "profiles")
    descriptions = json.loads(source[profiles_path].decode("utf-8"))
    for task, source_key in (
        ("generalization", "rolebench-eng/role-generalization/general/test.jsonl"),
        ("role-specific", "rolebench-eng/role-generalization/role_specific/test.jsonl"),
    ):
        make_subset(
            task,
            load_jsonl(source[source_key]),
            descriptions,
            {source_key: hashlib.sha256(source[source_key]).hexdigest(), profiles_path: hashlib.sha256(source[profiles_path]).hexdigest()},
        )


if __name__ == "__main__":
    main()
