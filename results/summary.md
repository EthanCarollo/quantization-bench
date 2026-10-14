# Model benchmark scorecard

Each populated cell is the mean ± sample standard deviation across five run-level means; a dash means that five-run result is not yet available.
RoleBench uses ROUGE-L F1 multiplied by 100; CharacterEval uses CharacterRM mapped to 0–100; IFBench uses loose accuracy; HLE uses text-only judge accuracy; LiveCodeBench uses pass@1.

| Quantization / model | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | IFBench — loose /100 | HLE text-only — accuracy /100 | LiveCodeBench v6 — pass@1 /100 | Parameters |
|---|---:|---:|---:|---:|---:|---:|---:|
| MLX-4-bit — Gemma 4 E2B IT | 30.20 ± 2.74 | 14.08 ± 0.57 | 62.04 ± 5.36 | — | — | — | 2.3B effectifs (5.1B total) |
| MLX-8-bit — Gemma 4 E2B IT | 35.93 ± 5.72 | 12.94 ± 0.57 | 64.27 ± 4.79 | — | — | — | 2.3B effectifs (5.1B total) |
| MLX-4-bit — Qwen3-4B | 33.12 ± 1.25 | 12.35 ± 0.61 | 56.27 ± 6.11 | — | — | — | 4.0B total (3.6B hors embeddings) |
| MLX-8-bit — Qwen3-4B | 35.54 ± 1.73 | 13.80 ± 0.42 | 63.80 ± 4.14 | — | — | — | 4.0B total (3.6B hors embeddings) |

All four variants use MLX affine weight quantization with group size 64. The sampling settings and prompts are held fixed across model variants within each benchmark.

RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores come from the authors' human-annotated CharacterRM; they are averaged equally across the 12 dimensions covered by the fixed subset and linearly mapped from 1–5 to 0–100. IFBench reports official prompt-level loose accuracy; HLE reports the official judge accuracy over the text-only subset; LiveCodeBench reports execution-checked pass@1. These scores use different datasets and evaluators and should be compared only within each column.
