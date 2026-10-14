#!/usr/bin/env python3
"""Download a pinned HF model and convert it to an MLX affine quantization."""

import argparse
import json
import os
from pathlib import Path

from huggingface_hub import snapshot_download
from mlx_lm.convert import convert


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data" / "model_registry.json").read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=REGISTRY, required=True)
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    args = parser.parse_args()

    config = REGISTRY[args.model]
    token = os.environ.get("HF_TOKEN")
    if config["requires_hf_token"] and not token:
        raise SystemExit("Set HF_TOKEN after accepting the Gemma terms on Hugging Face.")

    source_dir = ROOT / "models" / config["snapshot_dir"]
    snapshot_download(
        repo_id=config["model_id"],
        revision=config["revision"],
        token=token,
        local_dir=source_dir,
    )
    output_dir = ROOT / "models" / f"{config['slug']}-mlx-{args.bits}bit"
    if output_dir.exists():
        raise SystemExit(f"Output already exists: {output_dir}; remove it explicitly to reconvert.")

    convert(
        hf_path=str(source_dir),
        mlx_path=str(output_dir),
        quantize=True,
        q_bits=args.bits,
        q_group_size=64,
        q_mode="affine",
        dtype="bfloat16",
    )
    print(
        f"Created {output_dir.relative_to(ROOT)} from {config['model_id']}@{config['revision']} "
        f"with MLX affine {args.bits}-bit, group 64."
    )


if __name__ == "__main__":
    main()
