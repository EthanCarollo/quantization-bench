# roleplay-bench-results

A reproducible comparison of compact open-weight models on role-play and character-consistency benchmarks.

**[Open the interactive results page](https://ethancarollo.github.io/roleplay-bench-results/)** · français / English

The current snapshot compares Gemma 4 E2B IT and Qwen3-4B in MLX 4-bit and 8-bit formats. It reports five-run means and sample standard deviations for two RoleBench tracks and CharacterEval. Other benchmark and GGUF results are still pending; blank scores are not zeros.

The website explains the metrics, protocol, quantization, limitations, and reproduction steps. For raw outputs and machine-readable tables, see [`results/`](results/), especially [`summary.csv`](results/summary.csv), [`summary.json`](results/summary.json), and [`environment.json`](results/environment.json). Dataset revisions and selected examples are documented in [`data/`](data/).

To regenerate the scorecard and the website's data bundle after adding benchmark outputs:

```bash
python scripts/summarize.py
```

Generation requirements and the full evaluation commands are on the [results page](https://ethancarollo.github.io/roleplay-bench-results/#reproduce).
