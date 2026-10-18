# Quantization Bench

This repository compares **local model runs only**. Hosted model results have been removed. The scorecard lists the benchmark suites with completed evaluations: RoleBench generalization, RoleBench role-specific, CharacterEval, IFBench, and AutomationBench.

**[Open Quantization Bench](https://ethancarollo.github.io/quantization-bench/)** · français / English

RoleBench and CharacterEval compare GGUF quantizations with each model's GGUF BF16 baseline across five paired runs. IFBench and AutomationBench are complete single-pass evaluations. Their scores have no run-level standard deviation. Scores are only comparable within the same benchmark column. Raw outputs and summaries are in [`results/`](results/); pinned benchmark data and source revisions are in [`data/`](data/).

Regenerate the scorecard and website data after adding local outputs:

```bash
python scripts/summarize.py
```

## Local models and evaluations

The six local checkpoints are Gemma 4 E2B, Gemma 4 E4B, Qwen3 4B, Qwen3.5 4B, LFM2.5 2.6B, and Ministral 3 3B. GGUF evaluations use llama.cpp; MLX evaluations use mlx-lm. Model revisions and supported quantizations are in [`data/model_registry.json`](data/model_registry.json).

RoleBench and CharacterEval use five runs over fixed, pinned subsets. IFBench uses the complete 300-prompt test split and official verifier at temperature 0. AutomationBench uses the 600 scored public tasks and local `llama-server` endpoint.

The GGUF Q4_K_M AutomationBench runner needs the pinned upstream checkout and its local environment. Prepare them with:

```bash
bash scripts/setup_automationbench.sh
```

Then run a model evaluation with:

```bash
"$HOME/.cache/roleplay-bench/automationbench-venv/bin/python" scripts/run_automationbench_gguf.py --model gemma4_e2b_it
```

Only publish completed local model evaluations in the scorecard. Keep credentials and model artifacts out of Git.
