# EXP-000 - Existing Packaged Results Audit

## Metadata

- Experiment ID: EXP-000
- Title: Existing packaged results audit
- Owner: Ali Hamed
- Date started: 2026-06-12
- Date completed: Unknown
- Status: planned
- Related research question: RQ1-RQ4

## Purpose

Map the delivered VEGO-AI package artifacts to reproducible research records before using any result as paper or thesis evidence.

## Inputs

- Source package: `VEGO-AI/`
- Ignored/deferred artifacts: `VEGO-AI/models/`, `VEGO-AI/analysis/`, `VEGO-AI/eval_output/`
- Tracked lightweight inputs: `VEGO-AI/inputs/`
- Audit registers: `docs/research/artifact-audit.md`, `docs/research/provenance-register.md`, `docs/research/publishability-register.md`

## Method

1. Record artifact groups without copying controlled contents into Git.
2. Confirm provenance and publishability before exposing examples in GitHub, Confluence, papers, or thesis appendices.
3. Map existing outputs to research questions and claims.
4. Identify commands needed to regenerate or validate the outputs.

## Commands

```powershell
.\scripts\research-health.ps1
python -m pytest VEGO-AI\tests -q
python -m compileall -q VEGO-AI\framework VEGO-AI\eval
```

## Outputs

- Metadata-only audit registers under `docs/research/`.
- Updated experiment registry entry.
- Later: curated evidence table entries after audit approval.

## Results

Not run yet.

## Interpretation

No scientific claim should depend on packaged outputs until provenance, sensitivity, and regeneration status are recorded.

## Limitations

- Artifact contents remain unaudited.
- IRB constraints are unknown.
- Existing outputs may depend on model/API settings that are not fully reconstructed yet.

## Reproducibility

Partial. The source code and lightweight inputs are tracked; controlled models and generated outputs are local/ignored pending audit.
