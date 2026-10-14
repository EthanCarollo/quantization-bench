#!/usr/bin/env python3
"""Aggregate five repeated RoleBench runs into a comparison table."""

import csv
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    summary = []
    for bits in (4, 8):
        run_path = RESULTS / f"gemma4_e2b_it_mlx_{bits}bit_runs.jsonl"
        item_path = RESULTS / f"gemma4_e2b_it_mlx_{bits}bit.jsonl"
        runs = read_jsonl(run_path)
        items = read_jsonl(item_path)
        if len(runs) != 5:
            raise SystemExit(f"Expected five runs for {bits}-bit; found {len(runs)}.")
        expected = {1, 2, 3, 4, 5}
        if {r["repetition"] for r in runs} != expected:
            raise SystemExit(f"Invalid repetition IDs for {bits}-bit.")
        per_run = [r["macro_rouge_l_f1"] for r in runs]
        summary.append(
            {
                "bits": bits,
                "method": f"MLX affine, group 64; {4.501 if bits == 4 else 8.500:.3f} reported bits/weight",
                "n_runs": len(runs),
                "n_examples_per_run": runs[0]["n_examples"],
                "rouge_l_mean": statistics.mean(per_run),
                "rouge_l_sample_sd": statistics.stdev(per_run),
                "decode_tps_mean": statistics.mean(r["decode_tps"] for r in items),
                "latency_seconds_mean": statistics.mean(r["latency_seconds_including_prefill"] for r in items),
                "peak_memory_gib_mean": statistics.mean(r["peak_memory_gib"] for r in items),
                "model_size_gib": items[0]["model_size_gib"],
            }
        )

    json_path = RESULTS / "summary.json"
    csv_path = RESULTS / "summary.csv"
    md_path = RESULTS / "summary.md"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)

    lines = [
        "# Gemma 4 E2B IT — RoleBench mini results",
        "",
        "Fixed 10-item RoleBench English role-generalization subset; one unscored warm-up, then five paired sampling seeds per quantization.",
        "ROUGE-L is the mean of the five per-run macro averages; `±` is sample standard deviation across runs.",
        "Decode tok/s and response latency are means across all 50 responses per quantization.",
        "",
        "| Quantization | Method | ROUGE-L F1 (mean ± SD) | Decode tok/s | Latency incl. prefill (s) | Peak MLX memory (GiB) | Model files (GiB) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['bits']}-bit | {row['method']} | {row['rouge_l_mean']:.4f} ± {row['rouge_l_sample_sd']:.4f} "
            f"| {row['decode_tps_mean']:.2f} | {row['latency_seconds_mean']:.2f} "
            f"| {row['peak_memory_gib_mean']:.2f} | {row['model_size_gib']:.2f} |"
        )
    lines += [
        "",
        "## Interpretation limits",
        "",
        "The reference is a single RoleGPT-generated answer. ROUGE-L is deterministic but rewards wording overlap, so this table is a reproducible reference-similarity and local-inference comparison, not a complete or unbiased human assessment of role-play quality. The subset has ten English examples and five random generations per example.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    generated = "\n".join(lines[6:10])
    start = "<!-- BENCHMARK_RESULTS_START -->"
    end = "<!-- BENCHMARK_RESULTS_END -->"
    before, rest = readme.split(start, 1)
    _, after = rest.split(end, 1)
    (ROOT / "README.md").write_text(f"{before}{start}\n\n{generated}\n\n{end}{after}", encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
