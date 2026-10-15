#!/usr/bin/env python3
"""Run five pinned IFBench repetitions against local llama.cpp GGUF models."""

import argparse
import json
import os
import socket
import statistics
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from ifbench import instructions_registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
DATA_PATH = ROOT / "data" / "ifbench" / "IFBench_test.jsonl"
DATASET_REVISION = "2e8a48de45ff3bf41242f927254ca81b59ca3ae2"
VERIFIER_REVISION = "1c40f0c10d9b5c5c2f10a175a28007ebb64f7f4d"
LLAMA_CPP_COMMIT = "529ac893e754e95a50469b2122f5efe28dfc08a0"
DEFAULT_LLAMA_CPP = Path.home() / ".cache" / "roleplay-bench" / "llama.cpp"
MODEL_DIR = ROOT / "models" / "gguf"
VARIANTS = {
    "gguf_bf16": {"format": "GGUF", "type": "BF16"},
    "gguf_q8_0": {"format": "GGUF", "type": "Q8_0"},
    "gguf_q4_k_m": {"format": "GGUF", "type": "Q4_K_M"},
}
SEED_BASE = 44000
MAX_NEW_TOKENS = 4096


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def allocate_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def loose_following(row: dict, response: str) -> list[bool]:
    """Mirror the official prompt-level loose verifier variants."""
    lines = response.split("\n")
    response_remove_first = "\n".join(lines[1:]).strip()
    response_remove_last = "\n".join(lines[:-1]).strip()
    response_remove_both = "\n".join(lines[1:-1]).strip()
    candidates = [
        response,
        response.replace("*", ""),
        response_remove_first,
        response_remove_last,
        response_remove_both,
        response_remove_first.replace("*", ""),
        response_remove_last.replace("*", ""),
        response_remove_both.replace("*", ""),
    ]
    checks = []
    for index, instruction_id in enumerate(row["instruction_id_list"]):
        instruction_class = instructions_registry.INSTRUCTION_DICT[instruction_id]
        instruction = instruction_class(instruction_id)
        verifier_kwargs = {key: value for key, value in row["kwargs"][index].items() if value is not None}
        instruction.build_description(**verifier_kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=row["prompt"])
        checks.append(any(candidate.strip() and instruction.check_following(candidate) for candidate in candidates))
    return checks


def post_chat(base_url: str, prompt: str, seed: int) -> tuple[str, dict, str | None]:
    payload = {
        "model": "local",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": 0,
        "max_tokens": MAX_NEW_TOKENS,
        "seed": seed,
        "chat_template_kwargs": {"enable_thinking": False},
        "stream": False,
    }
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=1800) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:4000]
        raise RuntimeError(f"llama-server returned HTTP {exc.code}: {detail}") from exc
    choice = result["choices"][0]
    content = choice["message"].get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"llama-server returned no assistant text: {result}")
    return content.strip(), result.get("usage", {}), choice.get("finish_reason")


def wait_for_server(process: subprocess.Popen, base_url: str, log_path: Path) -> None:
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        if process.poll() is not None:
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-6000:]
            raise RuntimeError(f"llama-server stopped before becoming ready:\n{tail}")
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=3) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(2)
    raise TimeoutError(f"llama-server did not become ready within 15 minutes; log: {log_path}")


def is_complete(output_path: Path, run_path: Path) -> bool:
    if not output_path.is_file() or not run_path.is_file():
        return False
    try:
        items = read_jsonl(output_path)
        runs = read_jsonl(run_path)
        return (
            len(items) == 1500
            and len(runs) == 5
            and {row.get("repetition") for row in runs} == {1, 2, 3, 4, 5}
            and all(sum(row.get("repetition") == rep for row in items) == 300 for rep in range(1, 6))
        )
    except (OSError, ValueError, TypeError):
        return False


def run_variant(model_key: str, variant: str, args) -> None:
    model_info = REGISTRY[model_key]
    model_path = MODEL_DIR / f"{model_key}_{variant}.gguf"
    if not model_path.is_file():
        raise SystemExit(f"Missing GGUF model: {model_path}; run scripts/convert_gguf_models.py first.")
    rows = read_jsonl(DATA_PATH)
    if len(rows) != 300 or len({row["key"] for row in rows}) != 300:
        raise SystemExit(f"Expected 300 unique rows in the pinned IFBench split; found {len(rows)}.")

    stem = f"{model_key}_ifbench_{variant}"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    run_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if is_complete(output_path, run_path):
        print(f"Already complete: {stem}; skipping.", flush=True)
        return
    if output_path.exists() or run_path.exists():
        raise SystemExit(f"Partial or invalid results exist for {stem}; archive or remove them before rerunning.")

    port = allocate_port()
    base_url = f"http://127.0.0.1:{port}"
    log_path = args.server_log_dir / f"{stem}.log"
    server = args.llama_cpp / "build" / "bin" / "llama-server"
    command = [
        str(server), "--model", str(model_path), "--alias", "local",
        "--host", "127.0.0.1", "--port", str(port), "--ctx-size", str(args.context_size),
        "--n-gpu-layers", "999", "--threads", str(args.threads),
        "--threads-batch", str(args.threads), "--parallel", "1",
        "--flash-attn", "on", "--jinja", "--no-webui",
    ]
    tmp_output = output_path.with_name(f".{output_path.name}.partial")
    tmp_run = run_path.with_name(f".{run_path.name}.partial")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8") as log_file:
            process = subprocess.Popen(
                command,
                cwd=args.llama_cpp,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                env={**os.environ, "HF_HUB_DISABLE_TELEMETRY": "1"},
            )
            try:
                wait_for_server(process, base_url, log_path)
                first_prompt = rows[0]["prompt"]
                post_chat(base_url, first_prompt, SEED_BASE - 1)
                print(f"Warm-up complete for {model_key}@{variant}.", flush=True)
                with tmp_output.open("w", encoding="utf-8") as output, tmp_run.open("w", encoding="utf-8") as runs_file:
                    for repetition in range(1, 6):
                        seed = SEED_BASE + repetition - 1
                        prompt_scores = []
                        instruction_scores = []
                        truncated = 0
                        for index, row in enumerate(rows, start=1):
                            started = time.perf_counter()
                            response, usage, finish_reason = post_chat(base_url, row["prompt"], seed)
                            elapsed = time.perf_counter() - started
                            checks = loose_following(row, response)
                            score = float(all(checks))
                            prompt_scores.append(score)
                            instruction_scores.extend(checks)
                            truncated += finish_reason == "length"
                            result = {
                                "benchmark": "ifbench",
                                "dataset_revision": DATASET_REVISION,
                                "verifier_revision": VERIFIER_REVISION,
                                "model_key": model_key,
                                "model_id": model_info["model_id"],
                                "model_revision": model_info["revision"],
                                "runtime": "llama.cpp",
                                "runtime_version": LLAMA_CPP_COMMIT,
                                "quantization": VARIANTS[variant],
                                "repetition": repetition,
                                "seed": seed,
                                "item_id": row["key"],
                                "prompt": row["prompt"],
                                "instruction_id_list": row["instruction_id_list"],
                                "response": response,
                                "follow_instruction_list": checks,
                                "follow_all_instructions": bool(all(checks)),
                                "prompt_loose_accuracy_100": score * 100.0,
                                "prompt_tokens": usage.get("prompt_tokens"),
                                "generation_tokens": usage.get("completion_tokens"),
                                "latency_seconds_including_prefill": elapsed,
                                "finish_reason": finish_reason,
                                "model_size_gib": model_path.stat().st_size / (1024**3),
                                "max_new_tokens": MAX_NEW_TOKENS,
                                "temperature": 0.0,
                                "thinking": False,
                            }
                            output.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                            output.flush()
                            if index % 10 == 0 or index == len(rows):
                                print(
                                    f"{model_key}@{variant} IFBench run {repetition}/5, "
                                    f"item {index}/300: {sum(prompt_scores) / len(prompt_scores) * 100:.1f}% so far, "
                                    f"{elapsed:.1f}s",
                                    flush=True,
                                )

                        run = {
                            "benchmark": "ifbench",
                            "dataset_revision": DATASET_REVISION,
                            "verifier_revision": VERIFIER_REVISION,
                            "model_key": model_key,
                            "model_id": model_info["model_id"],
                            "model_revision": model_info["revision"],
                            "runtime": "llama.cpp",
                            "runtime_version": LLAMA_CPP_COMMIT,
                            "quantization": VARIANTS[variant],
                            "repetition": repetition,
                            "seed": seed,
                            "n_examples": len(rows),
                            "prompt_loose_accuracy_100": statistics.mean(prompt_scores) * 100.0,
                            "instruction_loose_accuracy_100": statistics.mean(instruction_scores) * 100.0,
                            "truncated_responses": truncated,
                            "max_new_tokens": MAX_NEW_TOKENS,
                        }
                        runs_file.write(json.dumps(run, separators=(",", ":")) + "\n")
                        runs_file.flush()
                        print(
                            f"Completed {model_key}@{variant} IFBench run {repetition}/5: "
                            f"loose accuracy={run['prompt_loose_accuracy_100']:.2f}%",
                            flush=True,
                        )
                tmp_output.replace(output_path)
                tmp_run.replace(run_path)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    finally:
        tmp_output.unlink(missing_ok=True)
        tmp_run.unlink(missing_ok=True)
    print(f"Wrote {output_path.relative_to(ROOT)} and {run_path.relative_to(ROOT)}.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["all", *REGISTRY], required=True)
    parser.add_argument("--variant", choices=["all", *VARIANTS], default="all")
    parser.add_argument("--llama-cpp", type=Path, default=DEFAULT_LLAMA_CPP)
    parser.add_argument("--context-size", type=int, default=8192)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--server-log-dir", type=Path, default=Path(tempfile.gettempdir()) / "roleplay-bench-llama")
    args = parser.parse_args()
    args.llama_cpp = args.llama_cpp.resolve()
    try:
        commit = subprocess.check_output(["git", "-C", str(args.llama_cpp), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Could not read llama.cpp checkout at {args.llama_cpp}: {exc}") from exc
    if commit != LLAMA_CPP_COMMIT:
        raise SystemExit(f"llama.cpp must be pinned at {LLAMA_CPP_COMMIT}; found {commit}.")
    if not (args.llama_cpp / "build" / "bin" / "llama-server").is_file():
        raise SystemExit("Build llama.cpp first (including the llama-server target).")
    if not DATA_PATH.is_file():
        raise SystemExit(f"Missing pinned IFBench data: {DATA_PATH}")
    args.server_log_dir.mkdir(parents=True, exist_ok=True)
    model_keys = list(REGISTRY) if args.model == "all" else [args.model]
    variants = list(VARIANTS) if args.variant == "all" else [args.variant]
    for model_key in model_keys:
        for variant in variants:
            run_variant(model_key, variant, args)


if __name__ == "__main__":
    main()
