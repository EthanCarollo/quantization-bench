# Role-play benchmark scorecard

Each cell is the mean ± sample standard deviation across five run-level means; each run has ten prompts.
Scores are ROUGE-L F1 multiplied by 100, shown on a 0–100 scale.

| Quantization / model | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | Parameters |
|---|---:|---:|---:|
| MLX-4-bit — Gemma 4 E2B IT | 30.20 ± 2.74 | 14.08 ± 0.57 | 2.3B effectifs (5.1B total) |
| MLX-8-bit — Gemma 4 E2B IT | 35.93 ± 5.72 | 12.94 ± 0.57 | 2.3B effectifs (5.1B total) |
| MLX-4-bit — Qwen3-4B | 33.12 ± 1.25 | 12.35 ± 0.61 | 4.0B total (3.6B hors embeddings) |
| MLX-8-bit — Qwen3-4B | 35.54 ± 1.73 | 13.80 ± 0.42 | 4.0B total (3.6B hors embeddings) |

All four variants use MLX affine weight quantization with group size 64. The sampling settings and ten prompts are held fixed across model variants within each benchmark.

ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. Scores compare models within each RoleBench track; the two tracks are separate test subsets.
