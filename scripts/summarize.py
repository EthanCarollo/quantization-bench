#!/usr/bin/env python3
"""Build the scorecard from local model evaluations with complete results."""

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SITE_DATA = ROOT / "site-data"
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
BENCHMARKS = (
    "rolebench_generalization",
    "rolebench_role_specific",
)
VARIANTS = (
    {
        "suffix": "mlx_4bit",
        "label": "MLX-4-bit",
        "tag": "mlx4",
        "method": "MLX affine, group 64, 4 bits",
        "quantization": {"format": "MLX", "mode": "affine", "bits": 4, "group_size": 64},
        "required": True,
    },
    {
        "suffix": "mlx_8bit",
        "label": "MLX-8-bit",
        "tag": "mlx8",
        "method": "MLX affine, group 64, 8 bits",
        "quantization": {"format": "MLX", "mode": "affine", "bits": 8, "group_size": 64},
        "required": True,
    },
    {
        "suffix": "gguf_bf16",
        "label": "GGUF-BF16",
        "tag": "bf16",
        "method": "GGUF BF16 (llama.cpp)",
        "quantization": {"format": "GGUF", "type": "BF16"},
        "required": False,
    },
    {
        "suffix": "gguf_q8_0",
        "label": "GGUF-Q8_0",
        "tag": "q8_0",
        "method": "GGUF Q8_0 (llama.cpp)",
        "quantization": {"format": "GGUF", "type": "Q8_0"},
        "required": False,
    },
    {
        "suffix": "gguf_q4_k_m",
        "label": "GGUF-Q4_K_M",
        "tag": "q4_k_m",
        "method": "GGUF Q4_K_M (llama.cpp)",
        "quantization": {"format": "GGUF", "type": "Q4_K_M"},
        "required": False,
    },
)
ADDITIONAL_BENCHMARKS = {
    "ifbench": ("prompt_loose_accuracy_100", 300, "prompt_loose_accuracy_100"),
    "automationbench": ("task_success_mean_100", 600, "task_success_100"),
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_pair(model_key: str, variant: dict, benchmark: str) -> tuple[float, float] | None:
    stem = f"{model_key}_{benchmark}_{variant['suffix']}"
    run_path = RESULTS / f"{stem}_runs.jsonl"
    item_path = RESULTS / f"{stem}.jsonl"
    if not run_path.is_file() or not item_path.is_file():
        if variant["required"]:
            raise SystemExit(f"Missing completed benchmark outputs for {stem}")
        return None
    runs = read_jsonl(run_path)
    items = read_jsonl(item_path)
    if len(runs) != 5 or {row["repetition"] for row in runs} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected five complete repetitions for {stem}")
    if len(items) != 50 or {row["repetition"] for row in items} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected 50 generated responses for {stem}")
    if any(run["n_examples"] != 10 for run in runs):
        raise SystemExit(f"Expected ten examples in every run for {stem}")
    if any(
        run.get("model_key") != model_key
        or run.get("quantization") != variant["quantization"]
        for run in runs
    ):
        raise SystemExit(f"Model or quantization metadata does not match the scorecard row for {stem}")
    values = [run["macro_rouge_l_f1"] * 100.0 for run in runs]
    return statistics.mean(values), statistics.stdev(values)


def summarize_charactereval(model_key: str, variant: dict) -> tuple[float, float] | None:
    stem = f"{model_key}_charactereval_{variant['suffix']}"
    path = RESULTS / f"{stem}.jsonl"
    if not path.is_file():
        if variant["required"]:
            raise SystemExit(f"Missing completed CharacterEval outputs for {stem}")
        return None
    items = read_jsonl(path)
    if len(items) != 60 or {row["repetition"] for row in items} != {1, 2, 3, 4, 5}:
        raise SystemExit(f"Expected 60 responses over five repetitions for {stem}")
    if any(
        row.get("model_key") != model_key
        or row.get("quantization") != variant["quantization"]
        for row in items
    ):
        raise SystemExit(f"Model or quantization metadata does not match the scorecard row for {stem}")
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


def summarize_single_pass(
    model_key: str, variant: dict, benchmark: str
) -> tuple[float, int, int] | None:
    metric, expected_examples, item_metric = ADDITIONAL_BENCHMARKS[benchmark]
    stem = f"{model_key}_{benchmark}_{variant['suffix']}"
    run_path = RESULTS / f"{stem}_runs.jsonl"
    item_path = RESULTS / f"{stem}.jsonl"
    if not run_path.is_file() and not item_path.is_file():
        return None
    if not run_path.is_file() or not item_path.is_file():
        raise SystemExit(f"Incomplete local results for {stem}")
    runs = read_jsonl(run_path)
    items = read_jsonl(item_path)
    if len(runs) != 1 or runs[0].get("repetition") != 1:
        raise SystemExit(f"Expected one complete local pass for {stem}")
    run = runs[0]
    if (
        run.get("benchmark") != benchmark
        or run.get("model_key") != model_key
        or run.get("quantization") != variant["quantization"]
        or run.get("n_examples") != expected_examples
        or len(items) != expected_examples
    ):
        raise SystemExit(f"Model, format, or example count does not match the local protocol for {stem}")
    if any(
        item.get("benchmark") != benchmark
        or item.get("model_key") != model_key
        or item.get("quantization") != variant["quantization"]
        or item.get("repetition") != 1
        or not isinstance(item.get(item_metric), (int, float))
        for item in items
    ):
        raise SystemExit(f"Invalid local result rows for {stem}")
    if len({item.get("item_id") for item in items}) != expected_examples:
        raise SystemExit(f"Duplicate or missing examples in {stem}")
    mean = statistics.mean(item[item_metric] for item in items)
    if not math.isclose(mean, run[metric], abs_tol=1e-9):
        raise SystemExit(f"Run summary does not match raw item scores for {stem}")
    if not isinstance(mean, (int, float)) or not math.isfinite(mean) or not 0 <= mean <= 100:
        raise SystemExit(f"Invalid score in {stem}")
    return mean, 1, expected_examples


def site_run_scores(model_key: str, variant: dict, benchmark: str) -> list[float]:
    """Return the five site metrics in repetition order for paired deltas."""
    if benchmark == "charactereval":
        items = read_jsonl(RESULTS / f"{model_key}_charactereval_{variant['suffix']}.jsonl")
        scores = []
        for repetition in range(1, 6):
            by_dimension = defaultdict(list)
            for item in items:
                if item["repetition"] != repetition:
                    continue
                for score in item["charactereval_scores"]:
                    by_dimension[score["metric_en"]].append(score["score_100"])
            scores.append(statistics.mean(statistics.mean(values) for values in by_dimension.values()))
        return scores

    runs = read_jsonl(RESULTS / f"{model_key}_{benchmark}_{variant['suffix']}_runs.jsonl")
    return [run["macro_rouge_l_f1"] * 100.0 for run in sorted(runs, key=lambda run: run["repetition"])]


def render_score(value: tuple[float, float | None] | None) -> str:
    if value is None:
        return "—"
    return f"{value[0]:.2f}" if value[1] is None else f"{value[0]:.2f} ± {value[1]:.2f}"


def main() -> None:
    rows = []
    for model_key, model in REGISTRY.items():
        supported_variants = set(
            model.get("scorecard_variants", (variant["suffix"] for variant in VARIANTS))
        )
        for variant in VARIANTS:
            if variant["suffix"] not in supported_variants:
                continue
            row = {
                "quantization": f"{model['short_name']}@{variant['tag']}",
                "model_tag": f"{model['short_name']}@{variant['tag']}",
                "model_name": model["display_name"],
                "variant_label": model.get("variant_label"),
                "variant_label_fr": model.get("variant_label_fr"),
                "variant_label_en": model.get("variant_label_en"),
                "method": variant["method"],
                "rolebench_generalization_mean_100": None,
                "rolebench_generalization_sd_100": None,
                "rolebench_role_specific_mean_100": None,
                "rolebench_role_specific_sd_100": None,
                "charactereval_mean_100": None,
                "charactereval_sd_100": None,
                "ifbench_prompt_accuracy_mean_100": None,
                "ifbench_prompt_accuracy_sd_100": None,
                "ifbench_n_runs": None,
                "ifbench_n_examples": None,
                "ifbench_truncated_responses": None,
                "ifbench_max_new_tokens": None,
                "automationbench_task_success_mean_100": None,
                "automationbench_task_success_sd_100": None,
                "automationbench_n_runs": None,
                "automationbench_n_examples": None,
                "parameters": model["parameter_label"],
                "model_key": model_key,
                "variant": variant["suffix"],
            }
            for benchmark in BENCHMARKS:
                result = summarize_pair(model_key, variant, benchmark)
                if result is not None:
                    row[f"{benchmark}_mean_100"], row[f"{benchmark}_sd_100"] = result
            charactereval = summarize_charactereval(model_key, variant)
            if charactereval is not None:
                row["charactereval_mean_100"], row["charactereval_sd_100"] = charactereval
            for benchmark, (prefix, metric) in {
                "ifbench": ("ifbench_prompt_accuracy", "prompt_loose_accuracy_100"),
                "automationbench": ("automationbench_task_success", "task_success_mean_100"),
            }.items():
                optional = summarize_single_pass(model_key, variant, benchmark)
                if optional is not None:
                    mean, run_count, n_examples = optional
                    row[f"{prefix}_mean_100"] = mean
                    row[f"{prefix}_sd_100"] = None
                    row[f"{benchmark}_n_runs"] = run_count
                    row[f"{benchmark}_n_examples"] = n_examples
                    run_path = RESULTS / f"{model_key}_{benchmark}_{variant['suffix']}_runs.jsonl"
                    run = read_jsonl(run_path)[0]
                    if benchmark == "ifbench":
                        row["ifbench_truncated_responses"] = run.get("truncated_responses")
                        row["ifbench_max_new_tokens"] = run.get("max_new_tokens")
            rows.append(row)

    variants_by_suffix = {variant["suffix"]: variant for variant in VARIANTS}
    site_benchmarks = (*BENCHMARKS, "charactereval")
    for row in rows:
        variant = variants_by_suffix[row["variant"]]
        is_gguf = variant["suffix"].startswith("gguf_")
        baseline = variants_by_suffix["gguf_bf16"]
        for benchmark in site_benchmarks:
            prefix = f"{benchmark}_delta_vs_bf16"
            mean_key, sd_key = f"{prefix}_mean_pp", f"{prefix}_sd_pp"
            row[mean_key] = None
            row[sd_key] = None
            if not is_gguf:
                continue
            if variant["suffix"] == "gguf_bf16":
                row[mean_key], row[sd_key] = 0.0, 0.0
                continue
            if row[f"{benchmark}_mean_100"] is None:
                continue
            quantized_runs = site_run_scores(row["model_key"], variant, benchmark)
            baseline_runs = site_run_scores(row["model_key"], baseline, benchmark)
            if len(quantized_runs) != len(baseline_runs) or len(quantized_runs) != 5:
                raise SystemExit(f"Expected five paired runs for {row['model_key']} {variant['suffix']} {benchmark}")
            deltas = [quantized - reference for quantized, reference in zip(quantized_runs, baseline_runs)]
            row[mean_key] = statistics.mean(deltas)
            row[sd_key] = statistics.stdev(deltas)

    summary_json = RESULTS / "summary.json"
    summary_csv = RESULTS / "summary.csv"
    summary_md = RESULTS / "summary.md"
    summary_json_text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    summary_json.write_text(summary_json_text, encoding="utf-8")
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "summary.json").write_text(summary_json_text, encoding="utf-8")
    (SITE_DATA / "environment.json").write_text(
        (RESULTS / "environment.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    columns = list(rows[0])
    with summary_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Model benchmark scorecard",
        "",
        "All rows are local model evaluations. RoleBench and CharacterEval report the mean ± sample standard deviation across five runs; IFBench and AutomationBench report one complete pass, so no run-level standard deviation is available. A dash means that model variant has no complete result for that benchmark.",
        "RoleBench uses ROUGE-L F1 × 100; CharacterEval uses CharacterRM mapped from 1–5 to 0–100; IFBench uses official loose accuracy; AutomationBench uses strict task completion. Scores belong to separate benchmarks and should be compared only within the same column.",
        "",
        "| Model variant | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | IFBench — loose /100 | AutomationBench — strict completion /100 | Parameters |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        general = render_score(
            None if row["rolebench_generalization_mean_100"] is None else (
                row["rolebench_generalization_mean_100"], row["rolebench_generalization_sd_100"]
            )
        )
        specific = render_score(
            None if row["rolebench_role_specific_mean_100"] is None else (
                row["rolebench_role_specific_mean_100"], row["rolebench_role_specific_sd_100"]
            )
        )
        charactereval = render_score(
            None if row["charactereval_mean_100"] is None else (
                row["charactereval_mean_100"], row["charactereval_sd_100"]
            )
        )
        ifbench = render_score(
            None if row["ifbench_prompt_accuracy_mean_100"] is None else (
                row["ifbench_prompt_accuracy_mean_100"], row["ifbench_prompt_accuracy_sd_100"]
            )
        )
        automationbench = render_score(
            None if row["automationbench_task_success_mean_100"] is None else (
                row["automationbench_task_success_mean_100"], row["automationbench_task_success_sd_100"]
            )
        )
        lines.append(
            f"| {row['model_tag']} | {general} | {specific} | {charactereval} | "
            f"{ifbench} | {automationbench} | {row['parameters']} |"
        )
    lines += [
        "",
        "MLX variants use affine weight quantization with group size 64. GGUF variants use llama.cpp BF16, Q8_0, or Q4_K_M files. IFBench scores use the official verifier over all 300 prompts at temperature 0. AutomationBench scores use the strict completion flag over all 600 scored public tasks.",
        "",
        "RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores use the authors' BaichuanCharRM reward model and weight the 12 covered dimensions equally. These metrics have different datasets and evaluators; do not compare scores across columns.",
        "",
    ]
    summary_md.write_text("\n".join(lines), encoding="utf-8")

    print(summary_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
