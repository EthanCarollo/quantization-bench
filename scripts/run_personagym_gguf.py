#!/usr/bin/env python3
"""Run the pinned PersonaGym benchmark-v1 using a local GGUF model."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

from gguf_server import LlamaServer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data" / "personagym" / "source.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
REPO = Path.home() / ".cache" / "roleplay-bench" / "sources" / "PersonaGym"
QUANTIZATION = {"format": "GGUF", "type": "Q4_K_M"}
LOCAL_MODEL_ALIAS = "gpt-local"


def scale_score_100(score: float) -> float:
    return max(0.0, min(100.0, (float(score) - 1.0) * 25.0))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--context-size", type=int, default=8192)
    args = parser.parse_args()

    for key in ("OPENAI_API_KEY", "TOGETHER_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} is required by the pinned PersonaGym protocol; set it in the environment first.")
    if not (REPO / ".git").exists():
        raise SystemExit(f"Missing pinned PersonaGym checkout: {REPO}")
    found_revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    if found_revision != SOURCE["repository_revision"]:
        raise SystemExit(f"PersonaGym source must be pinned at {SOURCE['repository_revision']}; found {found_revision}.")

    model_info = REGISTRY[args.model]
    model_path = ROOT / "models" / "gguf" / f"{args.model}_gguf_q4_k_m.gguf"
    stem = f"{args.model}_personagym_gguf_q4_k_m"
    results_path = ROOT / "results" / f"{stem}.jsonl"
    runs_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if runs_path.exists():
        raise SystemExit(f"Results already exist for {stem}; archive them before starting a new run.")

    sys.path.insert(0, str(REPO / "code"))
    os.chdir(REPO / "code")
    import utils
    import run as personagym

    official_openai_chat_gen = utils.openai_chat_gen
    official_llama_chat_gen = utils.llama_chat_gen

    def routed_openai_chat_gen(
        input_prompt=None,
        persona=None,
        apikey=None,
        model_card="gpt-3.5-turbo",
        temperature=0.9,
        top_p=0.9,
        max_tokens=3000,
        max_attempt=3,
        time_interval=2,
        system=None,
        message=None,
    ):
        if model_card == LOCAL_MODEL_ALIAS:
            client = OpenAI(api_key="local", base_url=server.base_url, timeout=1800)
            if message is None:
                if persona:
                    message = [
                        {"role": "system", "content": f"Adopt the identity of {persona}. Answer the questions while staying in strict accordance with the nature of this identity."},
                        {"role": "user", "content": input_prompt},
                    ]
                elif system:
                    message = [{"role": "system", "content": system}, {"role": "user", "content": input_prompt}]
                else:
                    message = [{"role": "user", "content": input_prompt}]
            response = client.chat.completions.create(
                model=model_info["short_name"],
                messages=message,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].message.content
        return official_openai_chat_gen(
            input_prompt=input_prompt,
            persona=persona,
            apikey=os.environ["OPENAI_API_KEY"],
            model_card=model_card,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            max_attempt=max_attempt,
            time_interval=time_interval,
            system=system,
            message=message,
        )

    def routed_llama_chat_gen(
        input_prompt,
        persona=None,
        apikey=None,
        model_card="meta-llama/Meta-Llama-3-70B",
        temperature=0.9,
        top_p=0.9,
        max_attempt=3,
        time_interval=5,
        max_tokens=3000,
    ):
        return official_llama_chat_gen(
            input_prompt,
            persona=persona,
            apikey=os.environ["TOGETHER_API_KEY"],
            model_card=model_card,
            temperature=temperature,
            top_p=top_p,
            max_attempt=max_attempt,
            time_interval=time_interval,
        )

    utils.openai_chat_gen = routed_openai_chat_gen
    utils.llama_chat_gen = routed_llama_chat_gen

    existing = {}
    if results_path.exists():
        with results_path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    row = json.loads(line)
                    existing[row["persona"]] = row
    personas = personagym.benchmark_personas
    if len(personas) != SOURCE["personas"]:
        raise SystemExit(f"Expected {SOURCE['personas']} benchmark personas; found {len(personas)}.")
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with LlamaServer(model_path, port=args.port, context_size=args.context_size) as server:
        with results_path.open("a", encoding="utf-8") as output:
            for index, persona in enumerate(personas):
                if persona in existing:
                    continue
                scores = personagym.main(
                    persona=persona,
                    model=LOCAL_MODEL_ALIAS,
                    model_name=None,
                    saved_questions="benchmark-v1",
                    saved_responses=None,
                )
                item = {
                    "benchmark": "personagym",
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
                    "persona": persona,
                    "task_scores_100": {
                        task: scale_score_100(scores[task])
                        for task in SOURCE["tasks"]
                    },
                    "persona_score_mean_100": scale_score_100(scores["PersonaScore"]),
                }
                output.write(json.dumps(item, separators=(",", ":")) + "\n")
                output.flush()
                existing[persona] = item
                if (index + 1) % 5 == 0 or index + 1 == len(personas):
                    print(f"PersonaGym: completed {index + 1}/{len(personas)} personas.", flush=True)

    if len(existing) != SOURCE["personas"]:
        raise SystemExit(f"Incomplete PersonaGym output: {len(existing)}/{SOURCE['personas']} personas.")
    rows = list(existing.values())
    mean = sum(row["persona_score_mean_100"] for row in rows) / len(rows)
    run = {
        "benchmark": "personagym",
        "source_revision": SOURCE["repository_revision"],
        "judge_models": SOURCE["judges"],
        "model_key": args.model,
        "model_id": model_info["model_id"],
        "model_revision": model_info["revision"],
        "runtime": "llama.cpp",
        "quantization": QUANTIZATION,
        "context_size": args.context_size,
        "gpu_layers": server.gpu_layers,
        "repetition": 1,
        "n_examples": len(rows),
        "persona_score_mean_100": mean,
    }
    runs_path.write_text(json.dumps(run, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"PersonaGym: {mean:.2f}/100 official PersonaScore over {len(rows)} personas.")
    print(f"Wrote {results_path.relative_to(ROOT)} and {runs_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
