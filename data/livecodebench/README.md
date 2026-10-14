# LiveCodeBench v6

The pinned release contains 1,055 code-generation problems. Its raw problem and test-case files are downloaded from Hugging Face by `scripts/prepare_livecodebench.py` into the ignored `hf-cache/` directory; they are not committed because the full snapshot is several gigabytes and includes hidden tests.

The scorecard will report execution-checked pass@1 on the pinned v6 *lite* test set. Five independently seeded one-sample runs are reported as mean ± sample standard deviation; this is not the upstream leaderboard's 10-sample pass@1 protocol. The official prompt, extraction, and test checker revisions are pinned in `source.json`.

Source: [LiveCodeBench repository](https://github.com/LiveCodeBench/LiveCodeBench) and [code-generation dataset](https://huggingface.co/datasets/livecodebench/code_generation_lite).
