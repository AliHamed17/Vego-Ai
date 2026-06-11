# ADR-0001: PhD Research Workspace Architecture

## Status

Accepted.

## Date

2026-06-11.

## Context

The project needs to support source code, experiments, generated outputs, literature, papers, thesis work, agent memory, and reversible progress tracking.

The existing VEGO-AI package was delivered as a zip archive with runnable code and research materials.

## Decision

Use a layered research workspace:

- preserve the extracted package in `VEGO-AI/`,
- manage research planning and documentation in `docs/`,
- record experiments in `experiments/`,
- keep data zones under `data/`,
- write papers/thesis materials in dedicated folders,
- use `src/` only for future cleaned reusable code,
- use agent memory for prompt continuity.

## Consequences

Benefits:

- Clear separation of code, data, outputs, and interpretation.
- Easier reproducibility and thesis writing.
- Safer future refactoring.
- Agents can orient quickly.

Tradeoffs:

- More folders than a small code-only project.
- Existing package remains nested until a deliberate refactor is planned.
- Git baseline still needs to be created after reviewing what should be tracked.

