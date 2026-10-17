#!/usr/bin/env python3
"""Apply the pinned LiveCodeBench execution checker in one disposable sandbox per problem."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "data" / "livecodebench" / "source.json").read_text(encoding="utf-8"))
FILES = ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"]
RESULT_PREFIX = "__LIVE_CODE_BENCH_RESULT__"
IMAGE = "roleplay-bench-results/livecodebench-evaluator:28fef95"
EVALUATOR_VENV = Path.home() / ".cache" / "roleplay-bench" / "livecodebench-evaluator-venv"
SANDBOXES = {
    "docker": "docker (read-only, network disabled, 2 GiB memory, 2 CPUs, 64 PIDs)",
    "bubblewrap": "bubblewrap (user/PID/network namespaces, read-only mounts, 128 MiB tmpfs, RLIMIT_CPU=6s, RLIMIT_AS=2 GiB, RLIMIT_NPROC=64)",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def source_paths() -> list[Path]:
    return [
        Path(
            hf_hub_download(
                repo_id=SOURCE["dataset_repository"],
                repo_type="dataset",
                filename=filename,
                revision=SOURCE["dataset_revision"],
                cache_dir=ROOT / "hf-cache" / "livecodebench-v6",
            )
        )
        for filename in FILES
    ]


def bubblewrap_command() -> list[str]:
    if not EVALUATOR_VENV.joinpath("bin", "python").is_file():
        raise RuntimeError(f"Missing pinned LiveCodeBench evaluator environment: {EVALUATOR_VENV}")
    if not Path("/usr/bin/bwrap").is_file():
        raise RuntimeError("Bubblewrap is not installed; install bwrap or use --sandbox docker.")

    venv_config = EVALUATOR_VENV / "pyvenv.cfg"
    python_home = next(
        (line.split("=", 1)[1].strip() for line in venv_config.read_text(encoding="utf-8").splitlines() if line.startswith("home =")),
        None,
    )
    if not python_home:
        raise RuntimeError(f"Could not find the base Python path in {venv_config}.")
    python_root = Path(python_home).parent.parent
    mount_targets = (
        Path.home() / ".local" / "share" / "uv" / "python",
        EVALUATOR_VENV,
    )
    directories = {Path("/sandbox"), Path("/opt"), Path("/home")}
    for target in (*mount_targets, python_root):
        directories.add(target)
        parent = target.parent
        while parent != Path("/"):
            directories.add(parent)
            parent = parent.parent

    command = [
        "prlimit", "--cpu=6", "--as=2147483648", "--nproc=64", "--",
        "bwrap", "--unshare-user", "--unshare-all", "--disable-userns",
        "--new-session", "--die-with-parent", "--cap-drop", "ALL",
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--proc", "/proc", "--dev", "/dev",
        "--size", "134217728", "--tmpfs", "/tmp", "--chmod", "1777", "/tmp",
        "--size", "67108864", "--tmpfs", "/dev/shm", "--chmod", "1777", "/dev/shm",
    ]
    for directory in sorted(directories, key=lambda path: (len(path.parts), str(path))):
        command.extend(("--dir", str(directory)))
    command.extend((
        "--ro-bind", str(python_root), str(python_root),
        "--ro-bind", str(EVALUATOR_VENV), str(EVALUATOR_VENV),
        "--ro-bind", str(ROOT / "vendor" / "livecodebench" / "testing_util.py"), "/sandbox/testing_util.py",
        "--ro-bind", str(ROOT / "docker" / "livecodebench" / "evaluate_one.py"), "/sandbox/evaluate_one.py",
        "--chdir", "/sandbox", "--clearenv",
        "--setenv", "PATH", f"{EVALUATOR_VENV / 'bin'}:/usr/bin:/bin",
        "--setenv", "HOME", "/tmp",
        "--setenv", "TMPDIR", "/tmp",
        "--setenv", "LC_ALL", "C",
        "--setenv", "OPENBLAS_NUM_THREADS", "1",
        "--setenv", "PYTHONNOUSERSITE", "1",
        "--setenv", "PYTHONPATH", "/sandbox",
        "--", str(EVALUATOR_VENV / "bin" / "python"), "/sandbox/evaluate_one.py",
    ))
    return command


def run_sandbox(row: dict, codes: list[str], sandbox: str) -> list[bool]:
    job = {
        "question_id": row["question_id"],
        "row": {
            "public_test_cases": row["public_test_cases"],
            "private_test_cases": row["private_test_cases"],
            "metadata": row["metadata"],
        },
        "codes": codes,
    }
    if sandbox == "docker":
        command = [
            "docker", "run", "--rm", "--interactive",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--memory=2g",
            "--cpus=2",
            "--pids-limit=64",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=128m",
            IMAGE,
        ]
    else:
        command = bubblewrap_command()
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(job, separators=(",", ":")),
            text=True,
            capture_output=True,
            timeout=1800,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"LiveCodeBench sandbox exceeded 30 minutes for {row['question_id']}") from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"Docker sandbox failed for {row['question_id']} (exit {completed.returncode}): "
            f"{completed.stderr[-1200:]}"
        )
    payloads = [line[len(RESULT_PREFIX):] for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if not payloads:
        raise RuntimeError(f"Docker sandbox returned no result for {row['question_id']}: {completed.stdout[-1200:]}")
    result = json.loads(payloads[-1])
    if result["question_id"] != row["question_id"] or len(result["candidates"]) != len(codes):
        raise RuntimeError(f"Malformed Docker evaluation result for {row['question_id']}.")
    for candidate in result["candidates"]:
        if not candidate.get("completed"):
            raise RuntimeError(f"Incomplete official checker result for {row['question_id']}.")
    return [bool(candidate["passed"]) for candidate in result["candidates"]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), default=4)
    parser.add_argument("--format", choices=("mlx", "gguf"), default="mlx")
    parser.add_argument("--sandbox", choices=SANDBOXES, default="docker")
    args = parser.parse_args()

    if args.format == "mlx":
        suffix = f"mlx_{args.bits}bit"
        quantization = {"format": "MLX", "mode": "affine", "bits": args.bits, "group_size": 64}
    else:
        if args.bits != 4:
            raise SystemExit("This runner currently supports GGUF Q4_K_M only.")
        suffix = "gguf_q4_k_m"
        quantization = {"format": "GGUF", "type": "Q4_K_M"}
    stem = f"{args.model}_livecodebench_v6_{suffix}"
    raw_path = ROOT / "results" / f"{stem}.jsonl"
    scored_path = ROOT / "results" / f"{stem}_scored.jsonl"
    runs_path = ROOT / "results" / f"{stem}_runs.jsonl"
    if not raw_path.is_file():
        raise SystemExit(f"Missing generation file {raw_path}; run scripts/run_livecodebench.py first.")
    if scored_path.exists() or runs_path.exists():
        raise SystemExit(f"Scores already exist for {stem}; archive or remove them explicitly before rerunning.")

    generations = read_jsonl(raw_path)
    repetition_ids = {row.get("repetition") for row in generations}
    if repetition_ids not in ({1}, {1, 2, 3, 4, 5}) or len(generations) != SOURCE["examples"] * len(repetition_ids):
        raise SystemExit(
            f"Expected one or five complete passes ({SOURCE['examples']} or {SOURCE['examples'] * 5} generations) "
            f"in {raw_path.name}; found {len(generations)}."
        )
    by_question = {}
    for row in generations:
        by_question.setdefault(row["question_id"], {})[row["repetition"]] = row
    expected_repetitions = repetition_ids
    if len(by_question) != SOURCE["examples"] or any(set(reps) != expected_repetitions for reps in by_question.values()):
        raise SystemExit("Expected the same complete set of one or five generations for each unique problem id.")

    repetitions = sorted(expected_repetitions)
    run_scores = {repetition: [] for repetition in repetitions}
    scored_path.parent.mkdir(parents=True, exist_ok=True)
    item_count = 0
    with scored_path.open("w", encoding="utf-8") as output:
        for path in source_paths():
            with path.open(encoding="utf-8") as dataset_file:
                for line in dataset_file:
                    problem = json.loads(line)
                    question_id = problem["question_id"]
                    generations_for_item = by_question.get(question_id)
                    if generations_for_item is None or any(
                        row["item_id"] != item_count for row in generations_for_item.values()
                    ):
                        raise RuntimeError(
                            f"Generation/source alignment mismatch at item {item_count}, question {question_id}."
                        )
                    codes = [generations_for_item[rep]["extracted_code"] for rep in repetitions]
                    verdicts = run_sandbox(problem, codes, args.sandbox)
                    for repetition, passed in zip(repetitions, verdicts):
                        result = {
                            "benchmark": "livecodebench_v6",
                            "dataset_revision": SOURCE["dataset_revision"],
                            "verifier_revision": SOURCE["official_repository_revision"],
                            "model_key": args.model,
                            "model_id": REGISTRY[args.model]["model_id"],
                            "model_revision": REGISTRY[args.model]["revision"],
                            "runtime": "llama.cpp" if args.format == "gguf" else "mlx-lm",
                            "execution_sandbox": SANDBOXES[args.sandbox],
                            "quantization": quantization,
                            "context_size": generations_for_item[1].get("context_size"),
                            "gpu_layers": generations_for_item[1].get("gpu_layers"),
                            "item_id": item_count,
                            "question_id": problem["question_id"],
                            "repetition": repetition,
                            "pass_at_1": passed,
                            "score_100": 100.0 if passed else 0.0,
                        }
                        output.write(json.dumps(result, separators=(",", ":")) + "\n")
                        run_scores[repetition].append(100.0 if passed else 0.0)
                    output.flush()
                    item_count += 1
                    if item_count % 10 == 0:
                        print(f"Scored {item_count}/{SOURCE['examples']} problems for {stem}.", flush=True)

    if item_count != SOURCE["examples"]:
        raise SystemExit(f"Expected {SOURCE['examples']} source rows; evaluated {item_count}.")
    with runs_path.open("w", encoding="utf-8") as file:
        for repetition, scores in run_scores.items():
            row = {
                "benchmark": "livecodebench_v6",
                "model_key": args.model,
                "model_id": REGISTRY[args.model]["model_id"],
                "model_revision": REGISTRY[args.model]["revision"],
                "runtime": "llama.cpp" if args.format == "gguf" else "mlx-lm",
                "execution_sandbox": SANDBOXES[args.sandbox],
                "quantization": quantization,
                "context_size": generations[0].get("context_size"),
                "gpu_layers": generations[0].get("gpu_layers"),
                "repetition": repetition,
                "n_examples": len(scores),
                "pass_at_1_100": statistics.mean(scores),
            }
            file.write(json.dumps(row, separators=(",", ":")) + "\n")

    print(f"Wrote {scored_path.relative_to(ROOT)} and {runs_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
