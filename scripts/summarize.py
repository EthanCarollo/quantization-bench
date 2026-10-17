#!/usr/bin/env python3
"""Build one scorecard for both RoleBench tracks and all model quantizations."""

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SITE_DATA = ROOT / "site-data"
REGISTRY = {
    **json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8")),
    **json.loads((ROOT / "data" / "openrouter_models.json").read_text(encoding="utf-8")),
}
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
    {
        "suffix": "openrouter",
        "label": "OpenRouter",
        "tag": "openrouter",
        "method": "OpenRouter hosted model",
        "quantization": {"format": "OpenRouter", "type": "Hosted"},
        "required": False,
    },
)
ADDITIONAL_BENCHMARKS = {
    "ifbench": ("prompt_loose_accuracy_100", 300, "prompt_loose_accuracy_100"),
    "hle": ("accuracy_100", None, None),
    "livecodebench_v6": ("pass_at_1_100", 1055, None),
    "automationbench": ("task_success_mean_100", 600, "task_success_100"),
    "toolsandbox": ("similarity_mean_100", 1032, "scenario_similarity_100"),
    "personagym": ("persona_score_mean_100", 200, "persona_score_mean_100"),
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


def summarize_optional(
    model_key: str, variant: dict, benchmark: str
) -> tuple[float, float | None, int, int] | None:
    metric, expected_examples, item_metric = ADDITIONAL_BENCHMARKS[benchmark]
    stem = f"{model_key}_{benchmark}_{variant['suffix']}"
    path = RESULTS / f"{stem}_runs.jsonl"
    if not path.is_file():
        return None
    runs = read_jsonl(path)
    run_count = len(runs)
    expected_repetitions = (
        {1} if benchmark in {"ifbench", "livecodebench_v6", "automationbench", "toolsandbox", "personagym"} and run_count == 1
        else {1, 2, 3, 4, 5} if run_count == 5
        else set()
    )
    if not expected_repetitions or {run.get("repetition") for run in runs} != expected_repetitions:
        return None
    if any(
        run.get("benchmark") != benchmark
        or run.get("model_key") != model_key
        or run.get("quantization") != variant["quantization"]
        for run in runs
    ):
        return None
    counts = {run.get("n_examples") for run in runs}
    if len(counts) != 1 or None in counts:
        return None
    n_examples = counts.pop()
    if expected_examples is not None and n_examples != expected_examples:
        return None
    if item_metric is not None:
        item_path = RESULTS / f"{stem}.jsonl"
        if not item_path.is_file():
            return None
        items = read_jsonl(item_path)
        repetitions = {run["repetition"] for run in runs}
        item_keys = {(item.get("repetition"), item.get("item_id")) for item in items}
        if (
            not items
            or (expected_examples is not None and len(items) != expected_examples * run_count)
            or len(item_keys) != len(items)
            or any(
                item.get("benchmark") != benchmark
                or item.get("model_key") != model_key
                or item.get("repetition") not in repetitions
                or not isinstance(item.get(item_metric), (int, float))
                for item in items
            )
        ):
            return None
        for run in runs:
            run_items = [item for item in items if item.get("repetition") == run["repetition"]]
            if (
                not run_items
                or (expected_examples is not None and len(run_items) != expected_examples)
                or len({item.get("item_id") for item in run_items}) != len(run_items)
                or not math.isclose(
                    statistics.mean(item[item_metric] for item in run_items),
                    run[metric],
                    abs_tol=1e-9,
                )
            ):
                return None
    values = [run.get(metric) for run in sorted(runs, key=lambda run: run["repetition"])]
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100 for value in values):
        return None
    deviation = statistics.stdev(values) if run_count > 1 else None
    return statistics.mean(values), deviation, run_count, n_examples


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


def render_optional(value: tuple[float, float | None] | None) -> str:
    if value is None:
        return "—"
    return f"{value[0]:.2f}" if value[1] is None else f"{value[0]:.2f} ± {value[1]:.2f}"


def render_score(value: tuple[float, float | None] | None) -> str:
    if value is None:
        return "—"
    return f"{value[0]:.2f}" if value[1] is None else f"{value[0]:.2f} ± {value[1]:.2f}"


def main() -> None:
    rows = []
    for model_key, model in REGISTRY.items():
        supported_variants = set(
            model.get(
                "scorecard_variants",
                (variant["suffix"] for variant in VARIANTS if variant["suffix"] != "openrouter"),
            )
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
                "ifbench_reasoning_effort": None,
                "ifbench_api_cost_usd": None,
                "hle_accuracy_mean_100": None,
                "hle_accuracy_sd_100": None,
                "livecodebench_pass_at_1_mean_100": None,
                "livecodebench_pass_at_1_sd_100": None,
                "automationbench_task_success_mean_100": None,
                "automationbench_task_success_sd_100": None,
                "automationbench_n_runs": None,
                "automationbench_n_examples": None,
                "toolsandbox_similarity_mean_100": None,
                "toolsandbox_similarity_sd_100": None,
                "toolsandbox_n_runs": None,
                "toolsandbox_n_examples": None,
                "personagym_persona_score_mean_100": None,
                "personagym_persona_score_sd_100": None,
                "personagym_n_runs": None,
                "personagym_n_examples": None,
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
            for benchmark in ADDITIONAL_BENCHMARKS:
                optional = summarize_optional(model_key, variant, benchmark)
                prefix = {
                    "ifbench": "ifbench_prompt_accuracy",
                    "hle": "hle_accuracy",
                    "livecodebench_v6": "livecodebench_pass_at_1",
                    "automationbench": "automationbench_task_success",
                    "toolsandbox": "toolsandbox_similarity",
                    "personagym": "personagym_persona_score",
                }[benchmark]
                if optional is not None:
                    mean, deviation, run_count, n_examples = optional
                    row[f"{prefix}_mean_100"] = mean
                    row[f"{prefix}_sd_100"] = deviation
                    row[f"{benchmark}_n_runs"] = run_count
                    row[f"{benchmark}_n_examples"] = n_examples
                    if benchmark == "ifbench":
                        run_path = RESULTS / f"{model_key}_{benchmark}_{variant['suffix']}_runs.jsonl"
                        run = read_jsonl(run_path)[0]
                        row["ifbench_truncated_responses"] = run.get("truncated_responses")
                        row["ifbench_max_new_tokens"] = run.get("max_new_tokens")
                        row["ifbench_reasoning_effort"] = run.get("reasoning_effort")
                        row["ifbench_api_cost_usd"] = run.get("api_cost_usd")
            rows.append(row)

    # Compare GGUF quantizations with the same model's GGUF BF16 runs. MLX rows
    # stay blank: this dataset has no MLX BF16 reference, so that delta would
    # mix quantization and runtime/format changes.
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
        "RoleBench and CharacterEval show the mean ± sample standard deviation across five run-level means. IFBench, LiveCodeBench, AutomationBench, ToolSandbox, and PersonaGym use one complete pass per model; their single-pass scores have no run-level standard deviation. A dash means no complete result is available.",
        "RoleBench uses ROUGE-L F1 multiplied by 100; CharacterEval uses CharacterRM mapped to 0–100; IFBench uses loose accuracy; HLE uses text-only judge accuracy; LiveCodeBench uses execution-checked pass@1; AutomationBench uses strict task completion; ToolSandbox uses official scenario similarity, including minefield constraints; PersonaGym uses average PersonaScore mapped from 1–5 to 0–100.",
        "",
        "| Model variant | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | IFBench — loose /100 | HLE text-only — accuracy /100 | LiveCodeBench v6 — pass@1 /100 | AutomationBench — strict completion /100 | ToolSandbox — scenario similarity /100 | PersonaGym — PersonaScore /100 | Parameters |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
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
        automationbench = render_optional(
            None if row["automationbench_task_success_mean_100"] is None else (
                row["automationbench_task_success_mean_100"], row["automationbench_task_success_sd_100"]
            )
        )
        toolsandbox = render_optional(
            None if row["toolsandbox_similarity_mean_100"] is None else (
                row["toolsandbox_similarity_mean_100"], row["toolsandbox_similarity_sd_100"]
            )
        )
        personagym = render_optional(
            None if row["personagym_persona_score_mean_100"] is None else (
                row["personagym_persona_score_mean_100"], row["personagym_persona_score_sd_100"]
            )
        )
        lines.append(
            f"| {row['model_tag']} | {general} | {specific} | {charactereval} | "
            f"{ifbench} | {hle} | {livecodebench} | {automationbench} | {toolsandbox} | {personagym} | {row['parameters']} |"
        )
    lines += [
        "",
        "MLX variants use affine weight quantization with group size 64. GGUF variants use llama.cpp BF16, Q8_0, or Q4_K_M files. OpenRouter entries are hosted APIs, not local quantizations; their same-model BF16 delta is unavailable. IFBench uses the same 300 prompts and official verifier for each hosted model at temperature 0; reasoning effort and maximum output tokens vary by model and are recorded with each result.",
        "",
        "RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores come from the authors' human-annotated CharacterRM; they are averaged equally across the 12 dimensions covered by the fixed subset and linearly mapped from 1–5 to 0–100. IFBench reports official prompt-level loose accuracy; HLE reports the official judge accuracy over the text-only subset; LiveCodeBench reports one full execution-checked pass@1 score; AutomationBench reports strict task completion; ToolSandbox reports the official scenario similarity; PersonaGym reports the official PersonaScore. These scores use different datasets and evaluators and should be compared only within each column.",
        "",
    ]
    summary_md.write_text("\n".join(lines), encoding="utf-8")

    print(summary_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
