# Humanity's Last Exam (HLE)

The runner uses every text-only row from the pinned HLE test split. Rows with images are excluded because Gemma 4 E2B IT and Qwen3-4B are evaluated here as text-only models. The exact number of usable rows is recorded in each run, as the gated dataset is not vendored.

Responses follow the authors' prompt and are scored with the official structured-output judge prompt and schema. The default judge model is the one specified by the pinned HLE code. Judging makes external API requests; configure `OPENAI_API_KEY` before running `scripts/evaluate_hle.py`. HF access to `cais/hle` is gated, so accept its access terms and provide `HF_TOKEN` (or a logged-in Hugging Face CLI session).

Each variant is generated five times at the official temperature of 0.0. The table reports mean ± sample standard deviation of text-only accuracy across those repetitions. Since temperature is zero, repeated outputs can be identical; generation seeds are retained for auditability.

The HLE dataset and predictions are not copied into Git. Raw prompts, answers, generations, and judge reasoning stay in the ignored local cache/results files; publish only aggregate metrics. The source dataset and official evaluation code are [cais/hle](https://huggingface.co/datasets/cais/hle) and [Center for AI Safety's HLE repository](https://github.com/CenterforAI-Safety/HLE).
