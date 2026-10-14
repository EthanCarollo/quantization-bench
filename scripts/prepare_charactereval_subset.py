#!/usr/bin/env python3
"""Create a deterministic, role-balanced CharacterEval subset."""

import hashlib
import json
import random
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
REVISION = "c3d44a6fc1790cc8c4b2fd7c01f0c72930655e0c"
BASE_URL = f"https://raw.githubusercontent.com/morecry/CharacterEval/{REVISION}/"
SOURCES = {
    "data/test_data.jsonl": "examples",
    "data/character_profiles.json": "profiles",
    "data/id2metric.jsonl": "metrics",
}


def fetch(path: str) -> bytes:
    with urlopen(BASE_URL + quote(path, safe="/"), timeout=120) as response:
        return response.read()


def read_speakers(context: str) -> list[str]:
    speakers = []
    for line in context.splitlines():
        if "：" in line:
            speakers.append(line.split("：", 1)[0])
    return speakers


def main() -> None:
    raw = {path: fetch(path) for path in SOURCES}
    examples = json.loads(raw["data/test_data.jsonl"].decode("utf-8"))
    profiles = json.loads(raw["data/character_profiles.json"].decode("utf-8"))
    metric_map = json.loads(raw["data/id2metric.jsonl"].decode("utf-8"))

    rng = random.Random(42)
    rng.shuffle(examples)
    candidates = []
    for example in examples:
        metrics = metric_map.get(str(example["id"]), [])
        speakers = read_speakers(example["context"])
        if metrics and example["role"] in profiles and speakers and speakers[-1] != example["role"]:
            candidates.append((example, metrics))

    metric_frequency = {}
    for _, metrics in candidates:
        for metric, _ in metrics:
            metric_frequency[metric] = metric_frequency.get(metric, 0) + 1

    selected = []
    seen_roles = set()
    covered_metrics = set()
    while len(selected) < 12:
        eligible = [
            (index, example, metrics)
            for index, (example, metrics) in enumerate(candidates)
            if example["role"] not in seen_roles
        ]
        if not eligible:
            raise RuntimeError(f"Could not select 12 distinct roles; found {len(selected)}")

        def rank(candidate):
            _, _, metrics = candidate
            names = {metric for metric, _ in metrics}
            new = names - covered_metrics
            rarity = sum(1 / metric_frequency[name] for name in new)
            return len(new), rarity

        best_rank = max(rank(candidate) for candidate in eligible)
        _, chosen, chosen_metrics = next(candidate for candidate in eligible if rank(candidate) == best_rank)
        selected.append((chosen, chosen_metrics))
        seen_roles.add(chosen["role"])
        covered_metrics.update(metric for metric, _ in chosen_metrics)

    records = []
    selected_profiles = {}
    for example, metrics in selected:
        selected_profiles[example["role"]] = profiles[example["role"]]
        records.append({
            "id": example["id"],
            "role": example["role"],
            "novel_name": example["novel_name"],
            "context": example["context"],
            "metrics": [{"metric_en": metric, "metric_zh": label} for metric, label in metrics],
        })

    data_dir = ROOT / "data" / "charactereval-mini"
    data_dir.mkdir(parents=True, exist_ok=True)
    examples_path = data_dir / "charactereval.jsonl"
    examples_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records),
        encoding="utf-8",
    )
    profiles_path = data_dir / "character_profiles.json"
    profiles_path.write_text(json.dumps(selected_profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "dataset": "morecry/CharacterEval",
        "dataset_revision": REVISION,
        "repository_license": "MIT",
        "paper": "https://aclanthology.org/2024.acl-long.638/",
        "examples": len(records),
        "distinct_roles": len(seen_roles),
        "selection": "Python random.Random(42) shuffle followed by greedy metric coverage, one example per role",
        "covered_metrics": sorted(covered_metrics),
        "source_file_sha256": {path: hashlib.sha256(value).hexdigest() for path, value in raw.items()},
        "local_files": {
            "examples": str(examples_path.relative_to(ROOT)),
            "profiles": str(profiles_path.relative_to(ROOT)),
        },
        "local_sha256": {
            "examples": hashlib.sha256(examples_path.read_bytes()).hexdigest(),
            "profiles": hashlib.sha256(profiles_path.read_bytes()).hexdigest(),
        },
        "selection_seed": 42,
        "reference_metric_field": "metrics",
    }
    (data_dir / "source.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"examples": len(records), "roles": [row["role"] for row in records], "metrics": sorted(covered_metrics)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
