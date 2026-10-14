# CharacterEval fixed subset

Twelve Chinese next-utterance examples from CharacterEval's test set, sampled deterministically with one example per character and greedy coverage of the available evaluation dimensions. The exact source revision, source and local hashes, and selected metric labels are recorded in `source.json`.

CharacterEval evaluates responses with the authors' human-annotated BaichuanCharRM reward model. Its source repository is [morecry/CharacterEval](https://github.com/morecry/CharacterEval), licensed MIT; the benchmark paper is [CharacterEval (ACL 2024)](https://aclanthology.org/2024.acl-long.638/). The reward model is [`morecry/BaichuanCharRM`](https://huggingface.co/morecry/BaichuanCharRM), whose score is reported on its original 1–5 scale and linearly mapped to 0–100 as `(score - 1) × 25` for this table.
