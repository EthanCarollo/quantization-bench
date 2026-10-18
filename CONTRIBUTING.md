# Contributing

Use Angular-style Conventional Commit subjects for every commit:

```text
type(scope): imperative summary
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and `revert`.

Keep the benchmark reproducible: pin source dataset/model revisions, record prompts and sampling settings, preserve raw per-example outputs, and report repeated-run mean and standard deviation. Push completed commits to `main`.

Keep model inference local. Add a benchmark to the scorecard only after its local evaluation has completed and its raw outputs are present in `results/`.
