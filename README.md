# Quantization Bench

Measured benchmark change by quantization, compared with each model's GGUF BF16 baseline.

**[Open Quantization Bench](https://ethancarollo.github.io/quantization-bench/)** · français / English

Delta values are paired across five runs and shown in percentage points. Hosted OpenRouter models are shown by absolute score because no matching local BF16 baseline exists. Publisher-reported loss claims are not currently collected. Raw outputs and machine-readable tables are in [`results/`](results/); benchmark sources and dataset revisions are in [`data/`](data/).

To regenerate the scorecard and website data after adding benchmark outputs:

```bash
python scripts/summarize.py
```

Evaluation scripts and environment requirements are in [`scripts/`](scripts/) and the repository's `requirements-*.txt` files.
