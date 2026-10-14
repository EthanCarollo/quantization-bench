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
ADDITIONAL_BENCHMARKS = {
    "ifbench": ("prompt_loose_accuracy_100", 300),
    "hle": ("accuracy_100", None),
    "livecodebench_v6": ("pass_at_1_100", 1055),
}


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


def summarize_optional(model_key: str, bits: int, benchmark: str) -> tuple[float, float] | None:
    metric, expected_examples = ADDITIONAL_BENCHMARKS[benchmark]
    stem = f"{model_key}_{benchmark}_mlx_{bits}bit"
    path = RESULTS / f"{stem}_runs.jsonl"
    if not path.is_file():
        return None
    runs = read_jsonl(path)
    if len(runs) != 5 or {run.get("repetition") for run in runs} != {1, 2, 3, 4, 5}:
        return None
    counts = {run.get("n_examples") for run in runs}
    if len(counts) != 1 or None in counts:
        return None
    n_examples = counts.pop()
    if expected_examples is not None and n_examples != expected_examples:
        return None
    values = [run.get(metric) for run in sorted(runs, key=lambda run: run["repetition"])]
    if any(not isinstance(value, (int, float)) for value in values):
        return None
    return statistics.mean(values), statistics.stdev(values)


def render_optional(value: tuple[float, float] | None) -> str:
    return "—" if value is None else f"{value[0]:.2f} ± {value[1]:.2f}"


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
                "ifbench_prompt_accuracy_mean_100": None,
                "ifbench_prompt_accuracy_sd_100": None,
                "hle_accuracy_mean_100": None,
                "hle_accuracy_sd_100": None,
                "livecodebench_pass_at_1_mean_100": None,
                "livecodebench_pass_at_1_sd_100": None,
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
            for benchmark in ADDITIONAL_BENCHMARKS:
                optional = summarize_optional(model_key, bits, benchmark)
                prefix = {
                    "ifbench": "ifbench_prompt_accuracy",
                    "hle": "hle_accuracy",
                    "livecodebench_v6": "livecodebench_pass_at_1",
                }[benchmark]
                if optional is not None:
                    row[f"{prefix}_mean_100"], row[f"{prefix}_sd_100"] = optional
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
        "# Model benchmark scorecard",
        "",
        "Each populated cell is the mean ± sample standard deviation across five run-level means; a dash means that five-run result is not yet available.",
        "RoleBench uses ROUGE-L F1 multiplied by 100; CharacterEval uses CharacterRM mapped to 0–100; IFBench uses loose accuracy; HLE uses text-only judge accuracy; LiveCodeBench uses pass@1.",
        "",
        "| Quantization / model | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | IFBench — loose /100 | HLE text-only — accuracy /100 | LiveCodeBench v6 — pass@1 /100 | Parameters |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        general = f"{row['rolebench_generalization_mean_100']:.2f} ± {row['rolebench_generalization_sd_100']:.2f}"
        specific = f"{row['rolebench_role_specific_mean_100']:.2f} ± {row['rolebench_role_specific_sd_100']:.2f}"
        charactereval = f"{row['charactereval_mean_100']:.2f} ± {row['charactereval_sd_100']:.2f}"
        ifbench = render_optional(
            None if row["ifbench_prompt_accuracy_mean_100"] is None else (
                row["ifbench_prompt_accuracy_mean_100"], row["ifbench_prompt_accuracy_sd_100"]
            )
        )
        hle = render_optional(
            None if row["hle_accuracy_mean_100"] is None else (
                row["hle_accuracy_mean_100"], row["hle_accuracy_sd_100"]
            )
        )
        livecodebench = render_optional(
            None if row["livecodebench_pass_at_1_mean_100"] is None else (
                row["livecodebench_pass_at_1_mean_100"], row["livecodebench_pass_at_1_sd_100"]
            )
        )
        lines.append(
            f"| {row['quantization']} | {general} | {specific} | {charactereval} | "
            f"{ifbench} | {hle} | {livecodebench} | {row['parameters']} |"
        )
    lines += [
        "",
        "All four variants use MLX affine weight quantization with group size 64. The sampling settings and prompts are held fixed across model variants within each benchmark.",
        "",
        "RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores come from the authors' human-annotated CharacterRM; they are averaged equally across the 12 dimensions covered by the fixed subset and linearly mapped from 1–5 to 0–100. IFBench reports official prompt-level loose accuracy; HLE reports the official judge accuracy over the text-only subset; LiveCodeBench reports execution-checked pass@1. These scores use different datasets and evaluators and should be compared only within each column.",
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
