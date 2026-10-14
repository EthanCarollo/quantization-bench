# Gemma 4 E2B IT — RoleBench mini results

Fixed 10-item RoleBench English role-generalization subset; one unscored warm-up, then five paired sampling seeds per quantization.
ROUGE-L is the mean of the five per-run macro averages; `±` is sample standard deviation across runs.
Decode tok/s and response latency are means across all 50 responses per quantization.

| Quantization | Method | ROUGE-L F1 (mean ± SD) | Decode tok/s | Latency incl. prefill (s) | Peak MLX memory (GiB) | Model files (GiB) |
|---|---|---:|---:|---:|---:|---:|
| 4-bit | MLX affine, group 64; 4.501 reported bits/weight | 0.1188 ± 0.0192 | 63.12 | 1.42 | 2.88 | 2.46 |
| 8-bit | MLX affine, group 64; 8.500 reported bits/weight | 0.2052 ± 0.0155 | 36.35 | 2.44 | 5.19 | 4.61 |

## Interpretation limits

The reference is a single RoleGPT-generated answer. ROUGE-L is deterministic but rewards wording overlap, so this table is a reproducible reference-similarity and local-inference comparison, not a complete or unbiased human assessment of role-play quality. The subset has ten English examples and five random generations per example.
