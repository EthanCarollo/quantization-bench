# IFBench

This directory contains the 300-prompt IFBench test split from the benchmark authors. The source snapshot and checksum are recorded in `source.json`.

The test prompts are distributed under ODC-BY-1.0; cite the benchmark authors and retain this attribution when reusing the data. The verifier implementation is separately licensed Apache-2.0 and is pinned in `requirements-ifbench.txt`.

IFBench reports prompt-level loose accuracy by default. This is an exact verifier score on a 0–100 scale, not a human rating. The official paper evaluates at temperature 0.

All model evaluations published here run locally. Hosted API results are not included.

Source: [allenai/IFBench](https://github.com/allenai/IFBench) and [allenai/IFBench_test](https://huggingface.co/datasets/allenai/IFBench_test).
