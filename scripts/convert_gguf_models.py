#!/usr/bin/env python3
"""Convert the pinned Hugging Face checkpoints to the GGUF scorecard variants."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))
LLAMA_CPP_COMMIT = "529ac893e754e95a50469b2122f5efe28dfc08a0"
DEFAULT_LLAMA_CPP = Path.home() / ".cache" / "roleplay-bench" / "llama.cpp"
QUANTIZATIONS = {"gguf_bf16": None, "gguf_q8_0": "Q8_0", "gguf_q4_k_m": "Q4_K_M"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["all", *REGISTRY], default="all")
    parser.add_argument("--variant", choices=["all", *QUANTIZATIONS], default="all")
    parser.add_argument("--llama-cpp", type=Path, default=DEFAULT_LLAMA_CPP)
    parser.add_argument("--threads", type=int, default=6)
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

    converter = llama_cpp / "convert_hf_to_gguf.py"
    quantizer = llama_cpp / "build" / "bin" / "llama-quantize"
    if not converter.is_file() or not quantizer.is_file():
        raise SystemExit("Build llama.cpp first (including the llama-quantize target).")

    model_keys = list(REGISTRY) if args.model == "all" else [args.model]
    variants = list(QUANTIZATIONS) if args.variant == "all" else [args.variant]
    source_root = ROOT / "models" / "gguf-source"
    output_root = ROOT / "models" / "gguf"
    output_root.mkdir(parents=True, exist_ok=True)

    for model_key in model_keys:
        model = REGISTRY[model_key]
        source_dir = source_root / model_key
        if model.get("gguf_files") and all(variant in model["gguf_files"] for variant in variants):
            gguf_repository = model.get("gguf_repository", model)
            for variant in variants:
                output_path = output_root / f"{model_key}_{variant}.gguf"
                if not output_path.is_file():
                    filename = model["gguf_files"][variant]
                    repo_id = gguf_repository["model_id"]
                    revision = gguf_repository["revision"]
                    print(
                        f"Downloading {repo_id}/{filename}@{revision}…",
                        flush=True,
                    )
                    source_path = Path(
                        hf_hub_download(
                            repo_id=repo_id,
                            filename=filename,
                            revision=revision,
                            local_dir=str(source_dir),
                        )
                    )
                    source_path.replace(output_path)
                else:
                    print(f"Keeping existing {output_path.name}.", flush=True)
                if output_path.stat().st_size < 1_000_000_000:
                    raise SystemExit(f"GGUF output is missing or unexpectedly small: {output_path}")
                print(f"Ready: {output_path.relative_to(ROOT)} ({output_path.stat().st_size:,} bytes)", flush=True)
            shutil.rmtree(source_dir, ignore_errors=True)
            continue

        if model.get("gguf_source"):
            source = model["gguf_source"]
            bf16_path = output_root / f"{model_key}_gguf_bf16.gguf"
            if bf16_path.exists() and bf16_path.stat().st_size < 1_000_000_000:
                raise SystemExit(f"GGUF source is incomplete; remove it before retrying: {bf16_path}")
            if not bf16_path.is_file():
                print(
                    f"Downloading pinned BF16 GGUF {source['model_id']}/{source['bf16_file']}@{source['revision']}…",
                    flush=True,
                )
                source_path = Path(
                    hf_hub_download(
                        repo_id=source["model_id"],
                        filename=source["bf16_file"],
                        revision=source["revision"],
                        local_dir=str(source_dir),
                    )
                )
                source_path.replace(bf16_path)

            for variant in variants:
                if variant == "gguf_bf16":
                    continue
                output_path = output_root / f"{model_key}_{variant}.gguf"
                if output_path.is_file():
                    print(f"Keeping existing {output_path.name}.", flush=True)
                    continue
                quant_type = QUANTIZATIONS[variant]
                print(f"Quantizing {model_key} to {quant_type}…", flush=True)
                subprocess.run(
                    [
                        str(quantizer),
                        str(bf16_path),
                        str(output_path),
                        quant_type,
                        str(args.threads),
                    ],
                    check=True,
                    cwd=llama_cpp,
                )

            for variant in variants:
                path = output_root / f"{model_key}_{variant}.gguf"
                if not path.is_file() or path.stat().st_size < 1_000_000_000:
                    raise SystemExit(f"GGUF output is missing or unexpectedly small: {path}")
                print(f"Ready: {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)", flush=True)
            if "gguf_bf16" not in variants:
                bf16_path.unlink(missing_ok=True)
            shutil.rmtree(source_dir, ignore_errors=True)
            continue

        print(f"Downloading {model['model_id']}@{model['revision']}…", flush=True)
        snapshot_download(
            repo_id=model["model_id"],
            revision=model["revision"],
            local_dir=str(source_dir),
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.tiktoken", "*.jinja", "*.txt", "*.py"],
        )

        bf16_path = output_root / f"{model_key}_gguf_bf16.gguf"
        if not bf16_path.is_file():
            print(f"Converting {model_key} to GGUF BF16…", flush=True)
            converter_env = os.environ.copy()
            converter_env["TMPDIR"] = str(output_root)
            subprocess.run(
                [
                    sys.executable,
                    str(converter),
                    str(source_dir),
                    "--outfile",
                    str(bf16_path),
                    "--outtype",
                    "bf16",
                    "--use-temp-file",
                ],
                check=True,
                cwd=llama_cpp,
                env=converter_env,
            )
        else:
            print(f"Keeping existing {bf16_path.name}.", flush=True)

        for variant in variants:
            quant_type = QUANTIZATIONS[variant]
            output_path = output_root / f"{model_key}_{variant}.gguf"
            if variant == "gguf_bf16":
                continue
            if output_path.is_file():
                print(f"Keeping existing {output_path.name}.", flush=True)
                continue
            print(f"Quantizing {model_key} to {quant_type}…", flush=True)
            subprocess.run(
                [
                    str(quantizer),
                    str(bf16_path),
                    str(output_path),
                    quant_type,
                    str(args.threads),
                ],
                check=True,
                cwd=llama_cpp,
            )

        for variant in variants:
            path = output_root / f"{model_key}_{variant}.gguf"
            if not path.is_file() or path.stat().st_size < 1_000_000_000:
                raise SystemExit(f"GGUF output is missing or unexpectedly small: {path}")
            print(f"Ready: {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)", flush=True)
        if "gguf_bf16" not in variants:
            bf16_path.unlink(missing_ok=True)
        shutil.rmtree(source_dir, ignore_errors=True)

    print(f"Built with llama.cpp {commit}.")


if __name__ == "__main__":
    main()
