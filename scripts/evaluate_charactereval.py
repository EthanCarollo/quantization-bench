#!/usr/bin/env python3
"""Score generated CharacterEval answers with the authors' BaichuanCharRM."""

import argparse
import json
from pathlib import Path

import torch
from transformers.dynamic_module_utils import get_class_from_dynamic_module


MODEL_ID = "morecry/BaichuanCharRM"
MODEL_REVISION = "e953da5f57b86db7adca3a2714b4c3720f5b96a2"
MAX_SEQUENCE_LENGTH = 4096


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--offload-dir", type=Path, required=True)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    profiles = json.loads(args.profiles.read_text(encoding="utf-8"))
    args.offload_dir.mkdir(parents=True, exist_ok=True)
    tokenizer_class = get_class_from_dynamic_module(
        "tokenization_baichuan.BaichuanTokenizer",
        MODEL_ID,
        revision=MODEL_REVISION,
    )
    tokenizer = tokenizer_class.from_pretrained(MODEL_ID, revision=MODEL_REVISION, use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    configuration_class = get_class_from_dynamic_module(
        "configuration_baichuan.BaichuanConfig",
        MODEL_ID,
        revision=MODEL_REVISION,
    )
    config = configuration_class.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    reward_model_class = get_class_from_dynamic_module(
        "modeling_baichuan.BaichuanCharRM",
        MODEL_ID,
        revision=MODEL_REVISION,
    )
    model = reward_model_class.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        config=config,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map="auto",
        max_memory={0: "14GiB", "cpu": "26GiB"},
        offload_folder=str(args.offload_dir),
        low_cpu_mem_usage=True,
        use_safetensors=False,
    ).eval()
    input_device = model.get_input_embeddings().weight.device
    print(f"Loaded {MODEL_ID}@{MODEL_REVISION}; input device={input_device}; device map={model.hf_device_map}", flush=True)

    total = 0
    for path in args.files:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for record_index, record in enumerate(records, start=1):
            profile = str(profiles[record["role"]])
            scores = []
            for dimension in record["metrics"]:
                score_text = (
                    "<RoleInfo>\n\n" + profile + "\n\n<Context>\n\n" + record["context"]
                    + "\n\n<Response>\n\n" + record["response"]
                    + "\n\n<Dimension>\n\n" + dimension["metric_zh"]
                )
                token_ids = tokenizer.encode(score_text, add_special_tokens=False) + [tokenizer.eos_token_id]
                token_ids = token_ids[-MAX_SEQUENCE_LENGTH:]
                input_ids = torch.tensor(token_ids, dtype=torch.long, device=input_device).unsqueeze(0)
                with torch.inference_mode():
                    output = model(input_ids=input_ids)
                    score_1_5 = float(output[1].item() * 4 + 1)
                scores.append({
                    "metric_en": dimension["metric_en"],
                    "metric_zh": dimension["metric_zh"],
                    "score_1_5": score_1_5,
                    "score_100": (score_1_5 - 1) * 25,
                })
                total += 1

            record["charactereval_scores"] = scores
            record["judge_model_id"] = MODEL_ID
            record["judge_model_revision"] = MODEL_REVISION
            path.write_text(
                "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in records),
                encoding="utf-8",
            )
            if record_index % 5 == 0 or record_index == len(records):
                print(f"{path.name}: scored {record_index}/{len(records)} responses; {total} dimension ratings", flush=True)


if __name__ == "__main__":
    main()
