# Quantization Bench

Measured benchmark change by quantization, compared with each model's GGUF BF16 baseline.

**[Open Quantization Bench](https://ethancarollo.github.io/quantization-bench/)** · français / English

Delta values are paired across five runs and shown in percentage points. Hosted OpenRouter models are shown by absolute score because no matching local BF16 baseline exists. Publisher-reported loss claims are not currently collected. Raw outputs and machine-readable tables are in [`results/`](results/); benchmark sources and dataset revisions are in [`data/`](data/).

To regenerate the scorecard and website data after adding benchmark outputs:

```bash
python scripts/summarize.py
```

Evaluation scripts and environment requirements are in [`scripts/`](scripts/) and the repository's `requirements-*.txt` files.

## Local Q4 benchmark runs

The six local checkpoints are Gemma 4 E2B, Gemma 4 E4B, Qwen3 4B, LFM2.5 2.6B, Qwen3.5 4B, and Ministral 3 3B. The local evaluation uses GGUF Q4_K_M. Build or download each model with its pinned source before starting a benchmark:

HLE is excluded from this evaluation plan.

```bash
.venv/bin/python scripts/convert_gguf_models.py --model gemma4_e2b_it --variant gguf_q4_k_m
```

LiveCodeBench and AutomationBench run against a local CUDA-enabled `llama-server` and need no paid API keys:

```bash
.venv/bin/python scripts/run_livecodebench_gguf.py --model gemma4_e2b_it
.venv/bin/python scripts/evaluate_livecodebench.py --format gguf --sandbox bubblewrap --model gemma4_e2b_it
.venv/bin/python scripts/run_automationbench_gguf.py --model gemma4_e2b_it
```

The Bubblewrap option runs the pinned upstream checker with the network disabled, a private PID/user namespace, read-only mounts, a 128 MiB temporary filesystem, and CPU/address-space/process limits. Docker remains available with `--sandbox docker` on machines with a working Docker engine and subordinate UID/GID mappings.

ToolSandbox and PersonaGym keep their published external simulators and judges. Set `OPENAI_API_KEY` and `RAPID_API_KEY` in the process environment before ToolSandbox; set `OPENAI_API_KEY` and `TOGETHER_API_KEY` before PersonaGym. Do not add these secrets to the repository or result files.

```bash
"$HOME/.cache/roleplay-bench/toolsandbox-venv/bin/python" scripts/run_toolsandbox_gguf.py --model gemma4_e2b_it
"$HOME/.cache/roleplay-bench/personagym-venv/bin/python" scripts/run_personagym_gguf.py --model gemma4_e2b_it
```

The official public suites cover one complete pass over 1,055 LiveCodeBench v6 problems, 600 scored AutomationBench tasks, 1,032 ToolSandbox scenarios, and 200 PersonaGym personas covering 10,000 questions. LiveCodeBench reports pass@1; a single pass has no run-level standard deviation. ToolSandbox and PersonaGym require many external judge or simulator calls. Once complete, regenerate the website and scorecard with `python scripts/summarize.py`; the new single-pass suites are shown as absolute scores because they do not have matching BF16 runs.

To prepare the pinned benchmark sources and isolated Python environments on another machine, run `bash scripts/setup_optional_benchmarks.sh`.
