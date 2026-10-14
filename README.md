# roleplay-bench-results

Reproducible role-play benchmark runs for open-weight language models. Each comparison records the model revision, runtime, weight quantization method, prompt set, sampling parameters, raw responses, and per-run scores.

## Current benchmark

The first run uses a fixed 10-example subset of the English **RoleBench role-generalization test split**. The subset is selected with seed `42`, with at most one prompt per role. The source dataset revision, source-file hashes, selected prompts, role profiles, and reference responses are stored in [`data/rolebench-mini/`](data/rolebench-mini/).

RoleBench is distributed under Apache-2.0. This small subset retains the original English test questions and RoleGPT reference answers. It follows the official RoleBench role-generalization prompt template and uses ROUGE-L F1 against the reference, as in the published benchmark pipeline. ROUGE-L measures lexical overlap with one reference; it is not a complete measure of role-play quality and can prefer similar wording. No LLM judge is used.

Each quantization is run five times across the same ten prompts, after one unscored warm-up to exclude first-call MLX compilation from timing. Sampling seeds are paired across quantizations. The table reports the mean and sample standard deviation of the five per-run macro means. Decode speed and latency are averaged over all generated responses.

## Results

<!-- BENCHMARK_RESULTS_START -->

| Quantization | Method | ROUGE-L F1 (mean ± SD) | Decode tok/s | Latency incl. prefill (s) | Peak MLX memory (GiB) | Model files (GiB) |
|---|---|---:|---:|---:|---:|---:|
| 4-bit | MLX affine, group 64; 4.501 reported bits/weight | 0.1188 ± 0.0192 | 63.12 | 1.42 | 2.88 | 2.46 |
| 8-bit | MLX affine, group 64; 8.500 reported bits/weight | 0.2052 ± 0.0155 | 36.35 | 2.44 | 5.19 | 4.61 |

<!-- BENCHMARK_RESULTS_END -->

Detailed per-run results and raw responses are under [`results/`](results/).

## Model and quantization

Base model: [`google/gemma-4-E2B-it`](https://huggingface.co/google/gemma-4-E2B-it), pinned to revision `3e22461f65e89153144f8adb70e3b8c2cc9845a7`.

Both variants are converted locally from that same Hugging Face checkpoint with `mlx_lm.convert`: uniform affine MLX weight-only quantization, group size 64, and 4 or 8 bits, without calibration data. This is MLX quantization, not GGUF or GPTQ. Non-quantized floating-point tensors use BF16. The converter reports 4.501 and 8.500 effective bits per weight, respectively. The model files are not checked into this repository.

The run uses the model's text path only. It follows the model card's sampling settings (`temperature=1.0`, `top_p=0.95`, `top_k=64`) and disables thinking. Generation is capped at 512 new tokens. Conversion and model loading are excluded from inference latency; prefill is included in per-response latency, while decode tokens/second is reported separately.

## Reproduce

Requirements: Apple Silicon Mac, macOS, Python 3.13, and permission to download the gated Gemma model. Accept Google's Gemma terms on Hugging Face, then make an access token available as `HF_TOKEN` in the shell.

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt

HF_TOKEN="$HF_TOKEN" .venv/bin/python scripts/convert_model.py --bits 4
HF_TOKEN="$HF_TOKEN" .venv/bin/python scripts/convert_model.py --bits 8

.venv/bin/python scripts/run_benchmark.py --bits 4
.venv/bin/python scripts/run_benchmark.py --bits 8
.venv/bin/python scripts/summarize.py
```

To recreate the checked-in prompt subset from its pinned Hugging Face revision:

```bash
.venv/bin/python scripts/prepare_rolebench_subset.py
```

## Sources

- RoleBench dataset and license: [ZenMoore/RoleBench](https://huggingface.co/datasets/ZenMoore/RoleBench)
- RoleBench paper and citation: [RoleLLM (arXiv:2310.00746)](https://arxiv.org/abs/2310.00746)
- Official RoleBench prompt/evaluation configuration: [OpenCompass role-generalization English config](https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/rolebench/role_generalization_eng.py)
- MLX conversion and quantization: [mlx-lm](https://github.com/ml-explore/mlx-lm)
- Model card and license: [Gemma 4 E2B IT](https://huggingface.co/google/gemma-4-E2B-it)

## Commit convention

Use Angular-style commits, for example `feat(bench): add Gemma 4 4-bit results`, and push completed commits to `main`. See [CONTRIBUTING.md](CONTRIBUTING.md).
