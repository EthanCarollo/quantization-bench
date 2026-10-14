# RoleBench mini subset

This directory contains ten English examples from the RoleBench **role-generalization test split** and their character descriptions. The examples retain their original test question and `generated[0]` reference response.

Source: [`ZenMoore/RoleBench`](https://huggingface.co/datasets/ZenMoore/RoleBench), revision `a57ed54f9613921e4a5f1b63601a558cd5acf971`, Apache-2.0. The source files and their SHA-256 hashes, selection seed, and local subset hash are recorded in [`source.json`](source.json).

Selection is reproducible: merge `general/test.jsonl` followed by `role_specific/test.jsonl`, shuffle with Python `random.Random(42)`, then keep the first example for each distinct role until ten examples are selected. No examples are chosen based on model outputs.

Citation:

```bibtex
@article{wang2023rolellm,
  title={RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of Large Language Models},
  author={Wang, Zekun Moore and Peng, Zhongyuan and Que, Haoran and others},
  journal={arXiv preprint arXiv:2310.00746},
  year={2023}
}
```
