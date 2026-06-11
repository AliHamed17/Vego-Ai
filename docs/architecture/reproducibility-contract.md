# Reproducibility Contract

For this project, a result is reproducible when another researcher can identify:

- source version,
- input data version,
- configuration,
- command,
- environment,
- model/API setting,
- output artifact,
- evaluation method,
- interpretation note.

## Minimum Run Record

For each run, record:

```text
Experiment ID:
Date:
Research question:
Code version:
Input data:
Config files:
Command:
Python version:
Dependencies:
Model/API:
Randomness:
Output path:
Known limitations:
```

## Storage Rules

- Do not store secrets in configs.
- Do not overwrite raw data.
- Do not manually edit generated outputs without recording it.
- Keep generated outputs out of Git unless they are small, stable, and needed for review.
- Prefer scripts and configs over manual steps.

