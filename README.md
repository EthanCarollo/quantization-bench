# roleplay-bench-results

A reproducible comparison of compact open-weight models on role-play and character-consistency benchmarks.

**[Open the interactive results page](https://ethancarollo.github.io/quantization-bench/)** · français / English

The current snapshot compares Gemma 4 E2B IT and Qwen3-4B in MLX 4-bit and 8-bit formats, plus GGUF BF16, Q8_0, and Q4_K_M variants. Each model–quantization pair has five runs for two RoleBench tracks and CharacterEval; the scorecard reports means and sample standard deviations. IFBench, Humanity’s Last Exam, and LiveCodeBench remain pending; blank scores are not zeros.

The website explains the metrics, protocol, quantization, limitations, and reproduction steps. For raw outputs and machine-readable tables, see [`results/`](results/), especially [`summary.csv`](results/summary.csv), [`summary.json`](results/summary.json), and [`environment.json`](results/environment.json). Dataset revisions and selected examples are documented in [`data/`](data/).

To regenerate the scorecard and the website's data bundle after adding benchmark outputs:

```bash
python scripts/summarize.py
```

Generation requirements and the full evaluation commands are on the [results page](https://ethancarollo.github.io/quantization-bench/#reproduce).
