# EXP-030 — BigUI source fidelity and provenance

## Purpose

Verify that every fact rendered in BigUI resolves to a schema-valid, hash-bound
canonical source and that stale, duplicate, private, or dangling records are
rejected before publication.

## Evidence boundary

This is research-infrastructure evidence. It can support source fidelity,
traceability, and reproducibility claims only. It cannot establish
classification accuracy, generalization, reduced human effort, or decision
value.

## Acceptance

- All `EXP-000` through `EXP-036` records resolve exactly once.
- Every rendered metric re-derives from its source record.
- Every source hash matches.
- Safe-label count zero forces empirical metrics to `null`.
- Private and controlled raw records never enter the tracked snapshot.
- A failed refresh preserves the last accepted BigUI.
