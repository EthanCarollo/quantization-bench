#!/usr/bin/env python3
"""Run the five-repeat RoleBench and CharacterEval scorecard for pinned GGUF models."""

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

from rouge_score.rouge_scorer import RougeScorer


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
LLAMA_CPP_COMMIT = "529ac893e754e95a50469b2122f5efe28dfc08a0"
DEFAULT_LLAMA_CPP = Path.home() / ".cache" / "roleplay-bench" / "llama.cpp"
BENCHMARK_DIRS = {
    "rolebench_generalization": "rolebench-generalization",
    "rolebench_role_specific": "rolebench-role-specific",
}
QUANTIZATIONS = {
    "gguf_bf16": {"format": "GGUF", "type": "BF16"},
    "gguf_q8_0": {"format": "GGUF", "type": "Q8_0"},
    "gguf_q4_k_m": {"format": "GGUF", "type": "Q4_K_M"},
}
SEED_BASE = 42000
CHARACTEREVAL_SEED_BASE = 43000
MAX_NEW_TOKENS = 512
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 64
SYSTEM_TEMPLATE = (
    "You are {role}, your description is: {description}. Now please answer some questions to accurately "
    "show your personality traits! Your speaking style should fully imitate the personality role assigned "
    "to you! Please do not expose that you are an artificial intelligence model or a language model, you "
    "must always remember that you are only assigned one personality role. Don’t be verbose or too formal "
    "or polite when speaking."
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def messages_for_charactereval(row: dict, profile: str) -> list[dict]:
    role = row["role"]
    conversations = []
    for line in row["context"].splitlines():
        if "：" in line:
            speaker, value = line.split("：", 1)
            conversations.append({"from": speaker, "value": value})
    if not conversations or conversations[-1]["from"] == role:
        raise ValueError(f"CharacterEval item {row['id']} has no final user turn.")

    first = conversations[0]
    greeting = f"好的！现在我来扮演{role}。"
    if first["from"] == role:
        greeting += f"我首先发话：{first['value']}"
    system = f"{profile}\n现在请你扮演一个角色扮演专家。请你根据上述信息扮演{role}进行对话。"
    messages = [{"role": "system", "content": system}, {"role": "assistant", "content": greeting}]
    for index in range(1, len(conversations) - 1):
        current = conversations[index]
        previous = conversations[index - 1]
        if current["from"] == role:
            if previous["from"] == role:
                raise ValueError(f"CharacterEval item {row['id']} has consecutive character turns.")
            messages.append({"role": "user", "content": f"{previous['from']}：{previous['value']}"})
            messages.append({"role": "assistant", "content": f"{current['from']}：{current['value']}"})
    final = conversations[-1]
    messages.append({"role": "user", "content": f"{final['from']}：{final['value']}"})
    return messages


def allocate_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(process: subprocess.Popen, base_url: str, log_path: Path) -> None:
    deadline = time.monotonic() + 900
    health_url = f"{base_url}/health"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-6000:]
            raise RuntimeError(f"llama-server stopped before becoming ready:\n{tail}")
        try:
            with urllib.request.urlopen(health_url, timeout=3) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(2)
    raise TimeoutError(f"llama-server did not become ready within 15 minutes; log: {log_path}")


def post_chat(
    base_url: str,
    messages: list[dict],
    max_tokens: int,
    seed: int,
    reasoning_budget_tokens: int | None = None,
) -> tuple[str, dict]:
    payload = {
        "model": "local",
        "messages": messages,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_tokens": max_tokens,
        "seed": seed,
        "chat_template_kwargs": {"enable_thinking": False},
        "stream": False,
    }
    if reasoning_budget_tokens is not None:
        payload["reasoning_budget_tokens"] = reasoning_budget_tokens
        payload["reasoning_control"] = True
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:4000]
        raise RuntimeError(f"llama-server returned HTTP {exc.code}: {detail}") from exc
    content = result["choices"][0]["message"].get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"llama-server returned no assistant text: {result}")
    return content.strip(), result.get("usage", {})


def item_filename(model_key: str, benchmark: str, variant: str) -> Path:
    return ROOT / "results" / f"{model_key}_{benchmark}_{variant}.jsonl"


def is_complete(path: Path, count: int, expected_per_repetition: int) -> bool:
    if not path.is_file():
        return False
    try:
        records = read_jsonl(path)
        return len(records) == count and all(
            sum(record.get("repetition") == repetition for record in records) == expected_per_repetition
            for repetition in range(1, 6)
        )
    except (OSError, ValueError, KeyError, TypeError):
        return False


def run_rolebench(
    model_key: str,
    model_info: dict,
    variant: str,
    quantization: dict,
    benchmark: str,
    base_url: str,
    model_size_gib: float,
    scorer: RougeScorer,
) -> None:
    dataset_dir = ROOT / "data" / BENCHMARK_DIRS[benchmark]
    data_path = dataset_dir / "rolebench.jsonl"
    if not data_path.is_file():
        raise SystemExit(f"Missing benchmark data: {data_path}")
    rows = read_jsonl(data_path)
    if len(rows) != 10:
        raise SystemExit(f"Expected the pinned 10-item subset; found {len(rows)} rows in {data_path}.")

    stem = f"{model_key}_{benchmark}_{variant}"
    output_path = ROOT / "results" / f"{stem}.jsonl"
    run_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if is_complete(output_path, 50, 10) and is_complete(run_path, 5, 1):
        print(f"Already complete: {output_path.name}; skipping.", flush=True)
        return
    if output_path.exists() or run_path.exists():
        raise SystemExit(f"Partial or invalid results exist for {stem}; archive or remove them before rerunning.")

    tmp_output = output_path.with_name(f".{output_path.name}.partial")
    tmp_run = run_path.with_name(f".{run_path.name}.partial")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tmp_output.open("w", encoding="utf-8") as raw_file, tmp_run.open("w", encoding="utf-8") as run_file:
            for repetition in range(1, 6):
                seed = SEED_BASE + repetition - 1
                scores = []
                for index, row in enumerate(rows, start=1):
                    messages = [
                        {
                            "role": "system",
                            "content": SYSTEM_TEMPLATE.format(role=row["role"], description=row["description"]),
                        },
                        {"role": "user", "content": row["question"]},
                    ]
                    started = time.perf_counter()
                    response, usage = post_chat(
                        base_url,
                        messages,
                        MAX_NEW_TOKENS,
                        seed,
                        model_info.get("reasoning_budget_tokens"),
                    )
                    elapsed = time.perf_counter() - started
                    rouge_l_f1 = scorer.score(row["reference"], response)["rougeL"].fmeasure
                    scores.append(rouge_l_f1)
                    generation_tokens = usage.get("completion_tokens")
                    result = {
                        "benchmark": benchmark,
                        "dataset_revision": "a57ed54f9613921e4a5f1b63601a558cd5acf971",
                        "model_key": model_key,
                        "model_id": model_info["model_id"],
                        "model_revision": model_info["revision"],
                        "runtime": "llama.cpp",
                        "runtime_version": LLAMA_CPP_COMMIT,
                        "quantization": quantization,
                        "repetition": repetition,
                        "seed": seed,
                        "item_id": row["id"],
                        "role": row["role"],
                        "question": row["question"],
                        "reference": row["reference"],
                        "response": response,
                        "rouge_l_f1": rouge_l_f1,
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "generation_tokens": generation_tokens,
                        "decode_tps": generation_tokens / elapsed if generation_tokens and elapsed else None,
                        "latency_seconds_including_prefill": elapsed,
                        "model_size_gib": model_size_gib,
                        "max_new_tokens": MAX_NEW_TOKENS,
                        "temperature": TEMPERATURE,
                        "top_p": TOP_P,
                        "top_k": TOP_K,
                        "thinking": False,
                        "reasoning_budget_tokens": model_info.get("reasoning_budget_tokens"),
                    }
                    raw_file.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                    raw_file.flush()
                    print(
                        f"{model_key}@{variant} {benchmark} run {repetition}/5, "
                        f"item {index}/10: ROUGE-L={rouge_l_f1:.4f}, "
                        f"{generation_tokens or '?'} tokens, {elapsed:.1f}s",
                        flush=True,
                    )
                run_summary = {
                    "benchmark": benchmark,
                    "model_key": model_key,
                    "model_id": model_info["model_id"],
                    "model_revision": model_info["revision"],
                    "runtime": "llama.cpp",
                    "runtime_version": LLAMA_CPP_COMMIT,
                    "quantization": quantization,
                    "repetition": repetition,
                    "seed": seed,
                    "n_examples": len(scores),
                    "macro_rouge_l_f1": statistics.mean(scores),
                    "reasoning_budget_tokens": model_info.get("reasoning_budget_tokens"),
                }
                run_file.write(json.dumps(run_summary, ensure_ascii=False, separators=(",", ":")) + "\n")
                run_file.flush()
                print(
                    f"Completed {model_key}@{variant} {benchmark} run {repetition}/5: "
                    f"macro ROUGE-L={run_summary['macro_rouge_l_f1']:.4f}",
                    flush=True,
                )
        tmp_output.replace(output_path)
        tmp_run.replace(run_path)
    finally:
        tmp_output.unlink(missing_ok=True)
        tmp_run.unlink(missing_ok=True)


def run_charactereval(
    model_key: str,
    model_info: dict,
    variant: str,
    quantization: dict,
    base_url: str,
    model_size_gib: float,
) -> None:
    data_dir = ROOT / "data" / "charactereval-mini"
    data_path = data_dir / "charactereval.jsonl"
    rows = read_jsonl(data_path)
    if len(rows) != 12:
        raise SystemExit(f"Expected the pinned 12-item CharacterEval subset; found {len(rows)} rows.")
    profiles = json.loads((data_dir / "character_profiles.json").read_text(encoding="utf-8"))
    output_path = item_filename(model_key, "charactereval", variant)
    if is_complete(output_path, 60, 12):
        print(f"Already complete: {output_path.name}; skipping.", flush=True)
        return
    if output_path.exists():
        raise SystemExit(f"Partial or invalid results exist for {output_path.name}; archive or remove it before rerunning.")

    tmp_output = output_path.with_name(f".{output_path.name}.partial")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tmp_output.open("w", encoding="utf-8") as output:
            for repetition in range(1, 6):
                seed = CHARACTEREVAL_SEED_BASE + repetition - 1
                for index, row in enumerate(rows, start=1):
                    response_messages = messages_for_charactereval(row, profiles[row["role"]])
                    started = time.perf_counter()
                    full_response, usage = post_chat(
                        base_url,
                        response_messages,
                        MAX_NEW_TOKENS,
                        seed,
                        model_info.get("reasoning_budget_tokens"),
                    )
                    elapsed = time.perf_counter() - started
                    response = full_response.splitlines()[0].strip() if full_response else ""
                    record = {
                        "benchmark": "charactereval",
                        "dataset_revision": "c3d44a6fc1790cc8c4b2fd7c01f0c72930655e0c",
                        "reward_model_revision": "e953da5f57b86db7adca3a2714b4c3720f5b96a2",
                        "model_key": model_key,
                        "model_id": model_info["model_id"],
                        "model_revision": model_info["revision"],
                        "runtime": "llama.cpp",
                        "runtime_version": LLAMA_CPP_COMMIT,
                        "quantization": quantization,
                        "repetition": repetition,
                        "seed": seed,
                        "item_id": row["id"],
                        "role": row["role"],
                        "context": row["context"],
                        "metrics": row["metrics"],
                        "response": response,
                        "full_response": full_response,
                        "charactereval_scores": None,
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "generation_tokens": usage.get("completion_tokens"),
                        "latency_seconds_including_prefill": elapsed,
                        "model_size_gib": model_size_gib,
                        "max_new_tokens": MAX_NEW_TOKENS,
                        "temperature": TEMPERATURE,
                        "top_p": TOP_P,
                        "top_k": TOP_K,
                        "thinking": False,
                        "reasoning_budget_tokens": model_info.get("reasoning_budget_tokens"),
                    }
                    output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                    output.flush()
                    print(
                        f"{model_key}@{variant} CharacterEval run {repetition}/5, "
                        f"item {index}/12: {record['generation_tokens'] or '?'} tokens, {elapsed:.1f}s",
                        flush=True,
                    )
        tmp_output.replace(output_path)
    finally:
        tmp_output.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["all", *REGISTRY], default="all")
    parser.add_argument("--variant", choices=["all", *QUANTIZATIONS], default="all")
    parser.add_argument("--llama-cpp", type=Path, default=DEFAULT_LLAMA_CPP)
    parser.add_argument("--context-size", type=int, default=8192)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--server-log-dir", type=Path, default=Path(tempfile.gettempdir()) / "roleplay-bench-llama")
    args = parser.parse_args()

    llama_cpp = args.llama_cpp.resolve()
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(llama_cpp), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Could not read llama.cpp checkout at {llama_cpp}: {exc}") from exc
    if commit != LLAMA_CPP_COMMIT:
        raise SystemExit(f"llama.cpp must be pinned at {LLAMA_CPP_COMMIT}; found {commit}.")
    server = llama_cpp / "build" / "bin" / "llama-server"
    if not server.is_file():
        raise SystemExit("Build llama.cpp first (including the llama-server target).")

    model_keys = list(REGISTRY) if args.model == "all" else [args.model]
    variants = list(QUANTIZATIONS) if args.variant == "all" else [args.variant]
    output_dir = ROOT / "models" / "gguf"
    args.server_log_dir.mkdir(parents=True, exist_ok=True)
    scorer = RougeScorer(["rougeL"], use_stemmer=False)

    for model_key in model_keys:
        model_info = REGISTRY[model_key]
        for variant in variants:
            model_path = output_dir / f"{model_key}_{variant}.gguf"
            if not model_path.is_file():
                raise SystemExit(f"Missing GGUF model file: {model_path}; run scripts/convert_gguf_models.py first.")
            model_size_gib = model_path.stat().st_size / (1024**3)
            port = allocate_port()
            base_url = f"http://127.0.0.1:{port}"
            log_path = args.server_log_dir / f"{model_key}_{variant}.log"
            command = [
                str(server),
                "--model",
                str(model_path),
                "--alias",
                "local",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--ctx-size",
                str(args.context_size),
                "--n-gpu-layers",
                "999",
                "--threads",
                str(args.threads),
                "--threads-batch",
                str(args.threads),
                "--parallel",
                "1",
                "--flash-attn",
                "on",
                "--jinja",
                "--no-webui",
            ]
            print(f"Starting {model_key}@{variant} ({model_size_gib:.2f} GiB)…", flush=True)
            with log_path.open("w", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    command,
                    cwd=llama_cpp,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env={**os.environ, "HF_HUB_DISABLE_TELEMETRY": "1"},
                )
                try:
                    wait_for_server(process, base_url, log_path)
                    print(f"llama-server ready for {model_key}@{variant}.", flush=True)
                    first = read_jsonl(ROOT / "data" / "rolebench-generalization" / "rolebench.jsonl")[0]
                    warmup_messages = [
                        {
                            "role": "system",
                            "content": SYSTEM_TEMPLATE.format(role=first["role"], description=first["description"]),
                        },
                        {"role": "user", "content": first["question"]},
                    ]
                    post_chat(
                        base_url,
                        warmup_messages,
                        MAX_NEW_TOKENS,
                        SEED_BASE - 1,
                        model_info.get("reasoning_budget_tokens"),
                    )
                    print("Warm-up complete (excluded from measured runs).", flush=True)
                    for benchmark in BENCHMARK_DIRS:
                        run_rolebench(
                            model_key,
                            model_info,
                            variant,
                            QUANTIZATIONS[variant],
                            benchmark,
                            base_url,
                            model_size_gib,
                            scorer,
                        )
                    run_charactereval(
                        model_key,
                        model_info,
                        variant,
                        QUANTIZATIONS[variant],
                        base_url,
                        model_size_gib,
                    )
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            print(f"Finished {model_key}@{variant}; server log: {log_path}", flush=True)


if __name__ == "__main__":
    main()
