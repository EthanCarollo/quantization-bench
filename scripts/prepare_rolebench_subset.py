#!/usr/bin/env python3
"""Recreate the pinned, deterministic 10-item RoleBench subset."""

import hashlib
import json
import random
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "rolebench-mini"
REVISION = "a57ed54f9613921e4a5f1b63601a558cd5acf971"
BASE_URL = f"https://huggingface.co/datasets/ZenMoore/RoleBench/resolve/{REVISION}/"
SOURCE_PATHS = (
    "profiles-eng/desc.json",
    "rolebench-eng/role-generalization/general/test.jsonl",
    "rolebench-eng/role-generalization/role_specific/test.jsonl",
)


def fetch(path: str) -> bytes:
    url = BASE_URL + quote(path, safe="/") + "?download=true"
    with urlopen(url, timeout=120) as response:
        return response.read()


def main() -> None:
    source = {path: fetch(path) for path in SOURCE_PATHS}
    descriptions = json.loads(source[SOURCE_PATHS[0]].decode("utf-8"))
    examples = []
    for path in SOURCE_PATHS[1:]:
        examples.extend(
            json.loads(line)
            for line in source[path].decode("utf-8").splitlines()
            if line.strip()
        )
    random.Random(42).shuffle(examples)

    selected = []
    seen_roles = set()
    for example in examples:
        role = example["role"]
        if role in seen_roles:
            continue
        seen_roles.add(role)
        selected.append(example)
        if len(selected) == 10:
            break
    if len(selected) != 10:
        raise RuntimeError("Could not select ten distinct roles")

    records = []
    for index, example in enumerate(selected, start=1):
        role = example["role"]
        records.append(
            {
                "id": index,
                "role": role,
                "description": descriptions[role],
                "question": example["question"],
                "reference": example["generated"][0],
                "source_type": example.get("type", ""),
            }
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / "rolebench_mini.jsonl"
    output.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in records
        ),
        encoding="utf-8",
    )
    manifest = {
        "dataset": "ZenMoore/RoleBench",
        "dataset_revision": REVISION,
        "license": "Apache-2.0",
        "benchmark": "RoleBench English role-generalization test split",
        "selection": "Python random.Random(42), shuffled merged general/test + role_specific/test, first item for each distinct role until 10 examples",
        "source_files": {
            path: hashlib.sha256(data).hexdigest() for path, data in source.items()
        },
        "local_file": "data/rolebench-mini/rolebench_mini.jsonl",
        "local_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "examples": len(records),
        "seed": 42,
        "reference_field": "generated[0]",
    }
    (DATA_DIR / "source.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"examples": len(records), "roles": [r["role"] for r in records], "sha256": manifest["local_sha256"]},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
