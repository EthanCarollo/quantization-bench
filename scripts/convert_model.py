#!/usr/bin/env python3
"""Download a pinned Gemma checkpoint and create a uniform MLX quant."""

import argparse
import os
from pathlib import Path

from huggingface_hub import snapshot_download
from mlx_lm.convert import convert


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "google/gemma-4-E2B-it"
MODEL_REVISION = "3e22461f65e89153144f8adb70e3b8c2cc9845a7"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, choices=(4, 8), required=True)
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("Set HF_TOKEN after accepting the Gemma terms on Hugging Face.")

    source_dir = snapshot_download(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        token=token,
        local_dir=ROOT / "models" / f"google-gemma-4-e2b-it-{MODEL_REVISION[:8]}",
    )
    output_dir = ROOT / "models" / f"gemma-4-e2b-it-mlx-{args.bits}bit"
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
    print(f"Created {output_dir} from {MODEL_ID}@{MODEL_REVISION} with MLX affine {args.bits}-bit, group 64.")


if __name__ == "__main__":
    main()
