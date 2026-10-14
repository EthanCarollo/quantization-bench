# roleplay-bench-results

Comparative role-play benchmarks for open-weight language models. Each model and quantization is evaluated on the same fixed prompts, five times, with raw answers and per-run scores retained for inspection.

## Results

<!-- BENCHMARK_RESULTS_START -->

| Quantization / model | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | Parameters |
|---|---:|---:|---:|
| MLX-4-bit — Gemma 4 E2B IT | 30.20 ± 2.74 | 14.08 ± 0.57 | 2.3B effectifs (5.1B total) |
| MLX-8-bit — Gemma 4 E2B IT | 35.93 ± 5.72 | 12.94 ± 0.57 | 2.3B effectifs (5.1B total) |
| MLX-4-bit — Qwen3-4B | 33.12 ± 1.25 | 12.35 ± 0.61 | 4.0B total (3.6B hors embeddings) |
| MLX-8-bit — Qwen3-4B | 35.54 ± 1.73 | 13.80 ± 0.42 | 4.0B total (3.6B hors embeddings) |

All four variants use MLX affine weight quantization with group size 64. The sampling settings and ten prompts are held fixed across model variants within each benchmark.

ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. Scores compare models within each RoleBench track; the two tracks are separate test subsets.

<!-- BENCHMARK_RESULTS_END -->

## How to read the score

Both RoleBench tracks use ROUGE-L F1 against one RoleGPT reference answer. The value is multiplied by 100 to fit a 0–100 scale. It is a wording-overlap score, not a percentage of role-play quality or a human rating. Compare model variants within a track; the two tracks have different questions.

## Benchmark protocol

- **RoleBench generalization:** 10 fixed English test prompts from the `general` subset.
- **RoleBench role-specific:** 10 fixed English test prompts from the `role_specific` subset.
- The same ten roles appear in both tracks. Questions and reference answers differ by track.
- Each variant receives one unscored warm-up, then five paired random seeds over the ten prompts: 50 measured answers per variant and track.
- Reported scores are the mean and sample standard deviation of the five run-level macro averages.
- Sampling is held fixed: temperature 1.0, top-p 0.95, top-k 64, thinking disabled, maximum 512 new tokens.

Both subsets are stored with the source revision, source-file hashes, selection seed, prompts, and references under [`data/`](data/). The benchmark source is [ZenMoore/RoleBench](https://huggingface.co/datasets/ZenMoore/RoleBench), licensed Apache-2.0. Evaluation follows the [official OpenCompass RoleBench configuration](https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/rolebench/role_generalization_eng.py).

## Models and quantization

The comparison uses [`google/gemma-4-E2B-it`](https://huggingface.co/google/gemma-4-E2B-it) and [`Qwen/Qwen3-4B`](https://huggingface.co/Qwen/Qwen3-4B), both pinned to revisions in [`data/model_registry.json`](data/model_registry.json). Gemma E2B has 2.3B effective parameters and 5.1B including embeddings; Qwen3-4B has 4.0B total parameters. The counts follow the respective model cards.

All four variants are converted locally from their pinned Hugging Face checkpoint with **MLX affine weight-only quantization**, group size 64, and BF16 for unquantized tensors. The converter reports 4.501 effective bits per weight for 4-bit and 8.500 for 8-bit. Model files are excluded from Git.

## Reproduce

Requirements: Apple Silicon, macOS, Python 3.13. Accept Google's Gemma terms on Hugging Face and expose an access token as `HF_TOKEN` before converting Gemma.

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/prepare_rolebench_subset.py

for model in gemma4_e2b_it qwen3_4b; do
  for bits in 4 8; do
    .venv/bin/python scripts/convert_model.py --model "$model" --bits "$bits"
    for benchmark in rolebench_generalization rolebench_role_specific; do
      .venv/bin/python scripts/run_benchmark.py --model "$model" --benchmark "$benchmark" --bits "$bits"
    done
  done
done

.venv/bin/python scripts/summarize.py
```

## Sources

- [RoleBench dataset](https://huggingface.co/datasets/ZenMoore/RoleBench) and [RoleLLM paper](https://arxiv.org/abs/2310.00746)
- [OpenCompass RoleBench evaluation configuration](https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/rolebench/role_generalization_eng.py)
- [Gemma 4 E2B IT model card and parameter counts](https://huggingface.co/google/gemma-4-E2B-it)
- [Qwen3-4B model card and parameter counts](https://huggingface.co/Qwen/Qwen3-4B)
- [MLX-LM conversion and quantization](https://github.com/ml-explore/mlx-lm)

## Commit convention

Use Angular-style commits and push completed commits to `main`; see [CONTRIBUTING.md](CONTRIBUTING.md).
