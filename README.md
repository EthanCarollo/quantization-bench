# roleplay-bench-results

A reproducible comparison of compact open-weight models on role-play and character-consistency benchmarks.

**[Open the interactive results page](https://ethancarollo.github.io/quantization-bench/)** · français / English

The scorecard covers five model families: Gemma 4 E2B IT and Qwen3-4B in MLX and GGUF, plus Ministral 3 3B Instruct, Qwen3.5-4B, and LFM2.5-2.6B in GGUF BF16, Q8_0, and Q4_K_M. Each variant has five runs for the two RoleBench tracks and CharacterEval. IFBench, Humanity’s Last Exam, and LiveCodeBench remain pending.

The website explains the metrics, protocol, quantization, limitations, and reproduction steps. For raw outputs and machine-readable tables, see [`results/`](results/), especially [`summary.csv`](results/summary.csv), [`summary.json`](results/summary.json), and [`environment.json`](results/environment.json). Dataset revisions and selected examples are documented in [`data/`](data/).

To regenerate the scorecard and the website's data bundle after adding benchmark outputs:

```bash
python scripts/summarize.py
```

Evaluation scripts and environment requirements are in [`scripts/`](scripts/) and the repository's `requirements-*.txt` files.
