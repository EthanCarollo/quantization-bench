#!/usr/bin/env python3
"""Run the pinned 600-task public AutomationBench with one local GGUF model."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path

from gguf_server import LlamaServer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data" / "automationbench" / "source.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
REPO = Path.home() / ".cache" / "roleplay-bench" / "sources" / "AutomationBench"
VENV = Path.home() / ".cache" / "roleplay-bench" / "automationbench-venv"
QUANTIZATION = {"format": "GGUF", "type": "Q4_K_M"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--context-size", type=int, default=32768)
    parser.add_argument("--parallel", type=int, default=2, help="Concurrent local inference requests.")
    parser.add_argument("--max-concurrent", type=int, default=2, help="AutomationBench tasks evaluated concurrently.")
    args = parser.parse_args()

    model_info = REGISTRY[args.model]
    model_path = ROOT / "models" / "gguf" / f"{args.model}_gguf_q4_k_m.gguf"
    stem = f"{args.model}_automationbench_gguf_q4_k_m"
    results_path = ROOT / "results" / f"{stem}.jsonl"
    runs_path = ROOT / "results" / f"{stem}_runs.jsonl"
    raw_path = Path.home() / ".cache" / "roleplay-bench" / "outputs" / f"{stem}_upstream.json"
    if results_path.exists() or runs_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive them before starting a new run.")
    if not (REPO / ".git").exists():
        raise SystemExit(f"Missing pinned AutomationBench checkout: {REPO}")
    found_revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    if found_revision != SOURCE["repository_revision"]:
        raise SystemExit(f"AutomationBench source must be pinned at {SOURCE['repository_revision']}; found {found_revision}.")
    executable = VENV / "bin" / "auto-bench"
    if not executable.is_file():
        raise SystemExit(f"AutomationBench environment is missing {executable}.")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with LlamaServer(model_path, port=args.port, context_size=args.context_size, parallel=args.parallel) as server:
        subprocess.run(
            [
                str(executable),
                "--model", model_info["short_name"],
                "--base-url", server.base_url,
                "--api-key", "local",
                "--num-examples", "-1",
                "--domains", ",".join(SOURCE["scored_domains"]),
                "--max-steps", str(SOURCE["max_steps"]),
                "--max-concurrent", str(args.max_concurrent),
                "--save-every", "1",
                "--export-json", str(raw_path),
            ],
            cwd=REPO,
            check=True,
        )

    export = json.loads(raw_path.read_text(encoding="utf-8"))
    tasks = export.get("tasks", [])
    if len(tasks) != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} scored AutomationBench tasks; found {len(tasks)}.")
    if len({task.get("name") for task in tasks}) != len(tasks) or any("passed" not in task for task in tasks):
        raise SystemExit("AutomationBench export has missing task names, duplicates, or incomplete pass flags.")

    item_rows = []
    for index, task in enumerate(tasks):
        item_rows.append(
            {
                "benchmark": "automationbench",
                "source_revision": SOURCE["repository_revision"],
                "model_key": args.model,
                "model_id": model_info["model_id"],
                "model_revision": model_info["revision"],
                "runtime": "llama.cpp",
                "quantization": QUANTIZATION,
                "context_size": args.context_size,
                "parallel_requests": args.parallel,
                "max_concurrent": args.max_concurrent,
                "gpu_layers": server.gpu_layers,
                "repetition": 1,
                "item_id": index,
                "task_name": task["name"],
                "task_success_100": 100.0 if task["passed"] else 0.0,
                "partial_credit_100": float(task.get("score", 0.0)) * 100.0,
                "assertions_total": task.get("assertions_total"),
                "assertions_passed": task.get("assertions_passed"),
            }
        )
    score = statistics.mean(row["task_success_100"] for row in item_rows)
    with results_path.open("w", encoding="utf-8") as output:
        for row in item_rows:
            output.write(json.dumps(row, separators=(",", ":")) + "\n")
    run = {
        "benchmark": "automationbench",
        "source_revision": SOURCE["repository_revision"],
        "model_key": args.model,
        "model_id": model_info["model_id"],
        "model_revision": model_info["revision"],
        "runtime": "llama.cpp",
        "quantization": QUANTIZATION,
        "context_size": args.context_size,
        "gpu_layers": server.gpu_layers,
        "max_steps": SOURCE["max_steps"],
        "max_concurrent": args.max_concurrent,
        "parallel_requests": args.parallel,
        "repetition": 1,
        "n_examples": len(item_rows),
        "task_success_mean_100": score,
        "partial_credit_mean_100": statistics.mean(row["partial_credit_100"] for row in item_rows),
    }
    runs_path.write_text(json.dumps(run, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"AutomationBench: {score:.2f}/100 strict success over {len(item_rows)} tasks.")
    print(f"Wrote {results_path.relative_to(ROOT)} and {runs_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
