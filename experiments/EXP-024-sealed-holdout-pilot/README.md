# EXP-024 — Sealed Holdout Pilot

Status: **Blocked on an approved, frozen EXP-023 candidate.**

## Question

Does the frozen deterministic candidate produce positive net correction on
eight previously sealed rows without harmful regression?

## Design

- Verify policy, partition, label-set, baseline, and source hashes.
- Open the eight adjudicated holdout labels once.
- Apply the frozen parallel policy without modification.
- Report paired correctness and net correction.

## Metrics

- Changed-and-correct.
- Changed-and-wrong.
- Both-correct.
- Both-wrong.
- Net correction.
- Accuracy and macro-F1 with Wilson intervals where applicable.

## Acceptance

- One run only.
- No policy revision after outcome inspection.
- Baseline and protected-path hashes remain unchanged.
- `EvaluationRunManifest-v2` is complete.

## Boundaries

With N=8, every result is a pilot. It cannot support a formal improvement or
generalization claim.
