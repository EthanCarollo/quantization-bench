#!/usr/bin/env python3
"""Run the pinned ToolSandbox suite with a local GGUF agent and official simulator."""

import argparse
import json
import os
import random
import statistics
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

from gguf_server import LlamaServer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data" / "toolsandbox" / "source.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
REPO = Path.home() / ".cache" / "roleplay-bench" / "sources" / "ToolSandbox"
VENV = Path.home() / ".cache" / "roleplay-bench" / "toolsandbox-venv"
QUANTIZATION = {"format": "GGUF", "type": "Q4_K_M"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--context-size", type=int, default=8192)
    args = parser.parse_args()

    for key in ("OPENAI_API_KEY", "RAPID_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} is required by the pinned ToolSandbox protocol; set it in the environment first.")
    if not (REPO / ".git").exists():
        raise SystemExit(f"Missing pinned ToolSandbox checkout: {REPO}")
    found_revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    if found_revision != SOURCE["repository_revision"]:
        raise SystemExit(f"ToolSandbox source must be pinned at {SOURCE['repository_revision']}; found {found_revision}.")

    model_info = REGISTRY[args.model]
    model_path = ROOT / "models" / "gguf" / f"{args.model}_gguf_q4_k_m.gguf"
    stem = f"{args.model}_toolsandbox_gguf_q4_k_m"
    results_path = ROOT / "results" / f"{stem}.jsonl"
    runs_path = ROOT / "results" / f"{stem}_runs.jsonl"
    output_root = Path.home() / ".cache" / "roleplay-bench" / "outputs" / "toolsandbox" / args.model
    if results_path.exists() or runs_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive them before starting a new run.")

    sys.path.insert(0, str(REPO))
    os.chdir(REPO)
    from tool_sandbox.cli import utils as cli_utils
    from tool_sandbox.cli.utils import RoleImplType, run_sandbox
    from tool_sandbox.common.tool_discovery import ToolBackend
    from tool_sandbox.roles.openai_api_agent import OpenAIAPIAgent

    class LocalToolAgent(OpenAIAPIAgent):
        def __init__(self) -> None:
            self.model_name = model_info["short_name"]
            self.openai_client = OpenAI(api_key="local", base_url=server.base_url)

    cli_utils.AGENT_TYPE_TO_FACTORY[RoleImplType.Gorilla] = LocalToolAgent
    name_to_scenario = cli_utils.resolve_scenarios(
        desired_scenario_names=None,
        preferred_tool_backend=ToolBackend.DEFAULT,
    )
    if len(name_to_scenario) != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} ToolSandbox scenarios; found {len(name_to_scenario)}.")

    random.seed(42)
    with LlamaServer(model_path, port=args.port, context_size=args.context_size) as server:
        os.environ["OPENAI_BASE_URL"] = server.base_url
        run_sandbox(
            agent_type=RoleImplType.Gorilla,
            user_type=RoleImplType.GPT_4_o_2024_05_13,
            name_to_scenario=name_to_scenario,
            processes=SOURCE["processes"],
            output_base_dir=output_root,
        )

    output_dirs = sorted(output_root.glob("agent_*_user_*") , key=lambda path: path.stat().st_mtime)
    if not output_dirs:
        raise SystemExit(f"ToolSandbox did not create a result directory under {output_root}.")
    summary_path = output_dirs[-1] / "result_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    scenarios = summary.get("per_scenario_results", [])
    if len(scenarios) != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} completed ToolSandbox scenarios; found {len(scenarios)}.")
    by_name = sorted(scenarios, key=lambda row: row["name"])
    item_rows = []
    for index, scenario in enumerate(by_name):
        value = float(scenario["similarity"])
        if not 0.0 <= value <= 1.0:
            raise SystemExit(f"Invalid official similarity for scenario {scenario['name']}: {value}")
        item_rows.append(
            {
                "benchmark": "toolsandbox",
                "source_revision": SOURCE["repository_revision"],
                "model_key": args.model,
                "model_id": model_info["model_id"],
                "model_revision": model_info["revision"],
                "runtime": "llama.cpp",
                "quantization": QUANTIZATION,
                "context_size": args.context_size,
                "gpu_layers": server.gpu_layers,
                "repetition": 1,
                "item_id": index,
                "scenario_name": scenario["name"],
                "scenario_similarity_100": value * 100.0,
                "milestone_similarity": float(scenario["milestone_similarity"]),
                "minefield_similarity": float(scenario["minefield_similarity"]),
                "turn_count": scenario["turn_count"],
                "exception_type": scenario.get("exception_type"),
            }
        )
    score = statistics.mean(row["scenario_similarity_100"] for row in item_rows)
    with results_path.open("w", encoding="utf-8") as output:
        for row in item_rows:
            output.write(json.dumps(row, separators=(",", ":")) + "\n")
    run = {
        "benchmark": "toolsandbox",
        "source_revision": SOURCE["repository_revision"],
        "model_key": args.model,
        "model_id": model_info["model_id"],
        "model_revision": model_info["revision"],
        "runtime": "llama.cpp",
        "quantization": QUANTIZATION,
        "context_size": args.context_size,
        "gpu_layers": server.gpu_layers,
        "repetition": 1,
        "n_examples": len(item_rows),
        "similarity_mean_100": score,
    }
    runs_path.write_text(json.dumps(run, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"ToolSandbox: {score:.2f}/100 official similarity over {len(item_rows)} scenarios.")
    print(f"Wrote {results_path.relative_to(ROOT)} and {runs_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
