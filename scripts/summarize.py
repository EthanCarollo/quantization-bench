#!/usr/bin/env python3
"""Build one scorecard for both RoleBench tracks and all model quantizations."""

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
BENCHMARKS = (
    "rolebench_generalization",
    "rolebench_role_specific",
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_pair(model_key: str, bits: int, benchmark: str) -> tuple[float, float]:
    stem = f"{model_key}_{benchmark}_mlx_{bits}bit"
    run_path = RESULTS / f"{stem}_runs.jsonl"
    item_path = RESULTS / f"{stem}.jsonl"
    if not run_path.is_file() or not item_path.is_file():
        raise SystemExit(f"Missing completed benchmark outputs for {stem}")
    runs = read_jsonl(run_path)
    items = read_jsonl(item_path)
    if len(runs) != 5 or {row["repetition"] for row in runs} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected five complete repetitions for {stem}")
    if len(items) != 50 or {row["repetition"] for row in items} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected 50 generated responses for {stem}")
    if any(run["n_examples"] != 10 for run in runs):
        raise SystemExit(f"Expected ten examples in every run for {stem}")
    values = [run["macro_rouge_l_f1"] * 100.0 for run in runs]
    return statistics.mean(values), statistics.stdev(values)


def summarize_charactereval(model_key: str, bits: int) -> tuple[float, float]:
    stem = f"{model_key}_charactereval_mlx_{bits}bit"
    path = RESULTS / f"{stem}.jsonl"
    if not path.is_file():
        raise SystemExit(f"Missing completed CharacterEval outputs for {stem}")
    items = read_jsonl(path)
    if len(items) != 60 or {row["repetition"] for row in items} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected 60 responses over five repetitions for {stem}")
    per_run = []
    for repetition in range(1, 6):
        run_items = [row for row in items if row["repetition"] == repetition]
        if len(run_items) != 12:
            raise SystemExit(f"Expected 12 responses in repetition {repetition} for {stem}")
        by_dimension = defaultdict(list)
        for item in run_items:
            scores = item.get("charactereval_scores")
            if not scores or len(scores) != len(item["metrics"]):
                raise SystemExit(f"Missing CharacterRM scores for {stem}, item {item['item_id']}")
            for score in scores:
                by_dimension[score["metric_en"]].append(score["score_100"])
        if len(by_dimension) != 12:
            raise SystemExit(f"Expected all 12 CharacterEval dimensions for {stem}; found {len(by_dimension)}")
        per_run.append(statistics.mean(statistics.mean(values) for values in by_dimension.values()))
    return statistics.mean(per_run), statistics.stdev(per_run)


def main() -> None:
    rows = []
    for model_key, model in REGISTRY.items():
        for bits in (4, 8):
            row = {
                "quantization": f"MLX-{bits}-bit — {model['display_name']}",
                "method": f"MLX affine, group 64, {bits} bits",
                "rolebench_generalization_mean_100": None,
                "rolebench_generalization_sd_100": None,
                "rolebench_role_specific_mean_100": None,
                "rolebench_role_specific_sd_100": None,
                "charactereval_mean_100": None,
                "charactereval_sd_100": None,
                "parameters": model["parameter_label"],
                "model_key": model_key,
                "bits": bits,
            }
            for benchmark in BENCHMARKS:
                mean, sd = summarize_pair(model_key, bits, benchmark)
                row[f"{benchmark}_mean_100"] = mean
                row[f"{benchmark}_sd_100"] = sd
            mean, sd = summarize_charactereval(model_key, bits)
            row["charactereval_mean_100"] = mean
            row["charactereval_sd_100"] = sd
            rows.append(row)

    summary_json = RESULTS / "summary.json"
    summary_csv = RESULTS / "summary.csv"
    summary_md = RESULTS / "summary.md"
    summary_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = list(rows[0])
    with summary_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Role-play benchmark scorecard",
        "",
        "Each cell is the mean ± sample standard deviation across five run-level means; every run uses the fixed prompts for its track.",
        "RoleBench uses ROUGE-L F1 multiplied by 100; CharacterEval uses CharacterRM mapped to 0–100.",
        "",
        "| Quantization / model | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | Parameters |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        general = f"{row['rolebench_generalization_mean_100']:.2f} ± {row['rolebench_generalization_sd_100']:.2f}"
        specific = f"{row['rolebench_role_specific_mean_100']:.2f} ± {row['rolebench_role_specific_sd_100']:.2f}"
        charactereval = f"{row['charactereval_mean_100']:.2f} ± {row['charactereval_sd_100']:.2f}"
        lines.append(f"| {row['quantization']} | {general} | {specific} | {charactereval} | {row['parameters']} |")
    lines += [
        "",
        "All four variants use MLX affine weight quantization with group size 64. The sampling settings and prompts are held fixed across model variants within each benchmark.",
        "",
        "RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores come from the authors' human-annotated CharacterRM; they are averaged equally across the 12 dimensions covered by the fixed subset and linearly mapped from 1–5 to 0–100. The CharacterEval column is a separate dataset and evaluator.",
        "",
    ]
    summary_md.write_text("\n".join(lines), encoding="utf-8")

    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start = "<!-- BENCHMARK_RESULTS_START -->"
    end = "<!-- BENCHMARK_RESULTS_END -->"
    before, rest = readme.split(start, 1)
    _, after = rest.split(end, 1)
    readme_path.write_text(f"{before}{start}\n\n{chr(10).join(lines[5:])}\n{end}{after}", encoding="utf-8")
    print(summary_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
