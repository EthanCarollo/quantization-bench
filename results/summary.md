# Model benchmark scorecard

RoleBench and CharacterEval show the mean ± sample standard deviation across five run-level means. IFBench uses one complete pass over the 300-prompt test split per hosted model; its single-pass score has no run-level standard deviation. A dash means no complete result is available.
RoleBench uses ROUGE-L F1 multiplied by 100; CharacterEval uses CharacterRM mapped to 0–100; IFBench uses loose accuracy; HLE uses text-only judge accuracy; LiveCodeBench uses pass@1.

| Model variant | RoleBench generalization — ROUGE-L /100 | RoleBench role-specific — ROUGE-L /100 | CharacterEval — CharacterRM /100 | IFBench — loose /100 | HLE text-only — accuracy /100 | LiveCodeBench v6 — pass@1 /100 | Parameters |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemma4-e2b-it@mlx4 | 30.20 ± 2.74 | 14.08 ± 0.57 | 62.04 ± 5.36 | — | — | — | 2.3B effectifs (5.1B total) |
| gemma4-e2b-it@mlx8 | 35.93 ± 5.72 | 12.94 ± 0.57 | 64.27 ± 4.79 | — | — | — | 2.3B effectifs (5.1B total) |
| gemma4-e2b-it@bf16 | 36.05 ± 3.04 | 13.16 ± 0.44 | 66.17 ± 2.77 | — | — | — | 2.3B effectifs (5.1B total) |
| gemma4-e2b-it@q8_0 | 36.89 ± 2.46 | 13.69 ± 0.70 | 66.65 ± 2.36 | — | — | — | 2.3B effectifs (5.1B total) |
| gemma4-e2b-it@q4_k_m | 36.95 ± 2.85 | 13.97 ± 0.60 | 64.87 ± 1.50 | — | — | — | 2.3B effectifs (5.1B total) |
| qwen3-4b@mlx4 | 33.12 ± 1.25 | 12.35 ± 0.61 | 56.27 ± 6.11 | — | — | — | 4.0B total (3.6B hors embeddings) |
| qwen3-4b@mlx8 | 35.54 ± 1.73 | 13.80 ± 0.42 | 63.80 ± 4.14 | — | — | — | 4.0B total (3.6B hors embeddings) |
| qwen3-4b@bf16 | 35.61 ± 1.09 | 13.82 ± 0.66 | 60.74 ± 5.09 | — | — | — | 4.0B total (3.6B hors embeddings) |
| qwen3-4b@q8_0 | 35.83 ± 1.00 | 13.67 ± 0.45 | 59.54 ± 4.21 | — | — | — | 4.0B total (3.6B hors embeddings) |
| qwen3-4b@q4_k_m | 35.18 ± 1.74 | 13.94 ± 0.33 | 58.31 ± 4.44 | — | — | — | 4.0B total (3.6B hors embeddings) |
| ministral-3-3b@bf16 | 14.66 ± 5.63 | 10.84 ± 0.35 | 51.69 ± 7.48 | — | — | — | 3.4B language + 0.4B vision |
| ministral-3-3b@q8_0 | 14.77 ± 5.96 | 10.78 ± 0.58 | 48.27 ± 9.11 | — | — | — | 3.4B language + 0.4B vision |
| ministral-3-3b@q4_k_m | 13.64 ± 3.62 | 10.71 ± 0.60 | 54.57 ± 3.62 | — | — | — | 3.4B language + 0.4B vision |
| qwen3.5-4b@bf16 | 15.47 ± 3.51 | 12.28 ± 0.25 | 67.67 ± 4.92 | — | — | — | 5B total (model card) |
| qwen3.5-4b@q8_0 | 18.57 ± 8.05 | 12.34 ± 0.69 | 65.84 ± 2.62 | — | — | — | 5B total (model card) |
| qwen3.5-4b@q4_k_m | 15.18 ± 3.05 | 12.75 ± 0.68 | 63.39 ± 5.27 | — | — | — | 5B total (model card) |
| lfm2.5-2.6b@bf16 | 18.95 ± 3.63 | 11.04 ± 0.62 | 48.13 ± 6.04 | — | — | — | 2.69B total (model card) |
| lfm2.5-2.6b@q8_0 | 19.24 ± 0.93 | 11.61 ± 0.62 | 45.12 ± 4.88 | — | — | — | 2.69B total (model card) |
| lfm2.5-2.6b@q4_k_m | 19.56 ± 3.69 | 11.03 ± 0.58 | 42.61 ± 10.99 | — | — | — | 2.69B total (model card) |
| gpt-6-luna-xhigh@openrouter | 31.24 ± 1.33 | 16.53 ± 1.34 | — | 53.67 | — | — | Modèle hébergé · OpenRouter |
| deepseek-v4.1-flash@openrouter | 24.70 ± 4.75 | 15.02 ± 1.03 | — | 48.00 | — | — | Modèle hébergé · OpenRouter |
| muse-spark-1.3-contributor@openrouter | 32.86 ± 2.90 | 14.01 ± 0.69 | — | 78.00 | — | — | Modèle hébergé · OpenRouter |
| deepseek-v4-flash-0731@openrouter | 28.71 ± 4.73 | 15.68 ± 0.41 | — | — | — | — | Modèle hébergé · OpenRouter |
| deepseek-v3.2@openrouter | 36.41 ± 6.56 | 15.15 ± 0.61 | — | — | — | — | Modèle hébergé · OpenRouter |

MLX variants use affine weight quantization with group size 64. GGUF variants use llama.cpp BF16, Q8_0, or Q4_K_M files. OpenRouter entries are hosted APIs, not local quantizations; their same-model BF16 delta is unavailable. IFBench uses the same 300 prompts and official verifier for each hosted model at temperature 0; reasoning effort and maximum output tokens vary by model and are recorded with each result.

RoleBench ROUGE-L measures wording overlap with one RoleGPT reference, not role-play quality as a percentage. CharacterEval scores come from the authors' human-annotated CharacterRM; they are averaged equally across the 12 dimensions covered by the fixed subset and linearly mapped from 1–5 to 0–100. IFBench reports official prompt-level loose accuracy; HLE reports the official judge accuracy over the text-only subset; LiveCodeBench reports execution-checked pass@1. These scores use different datasets and evaluators and should be compared only within each column.
