# EXP-022 — Routing and Retrieval Validity

Status: **Blocked on EXP-021.**

## Question

Do M1 review routing and M4A retrieval target expert-identified development
errors with relevant, scope-correct, traceable evidence?

## Design

- Compare review flags with adjudicated baseline errors.
- Audit retrieval relevance blind to candidate-policy outcomes.
- Separate pattern, queue-item, case, and review-transaction denominators.
- Report leakage and conflicts explicitly.

## Metrics

- Review precision, recall, false alarms, and missed errors.
- Retrieval hit rate, top-1 relevance, scope correctness, and conflict rate.
- Same-pattern, same-setting, cross-setting, none, and unknown provenance counts.

## Acceptance

- Every denominator and exclusion is declared.
- Unknown or same-pattern rows are excluded from generalization metrics.
- Negative and ambiguous retrieval judgments remain visible.

## Boundaries

This experiment evaluates targeting and retrieval validity. It cannot by itself
prove an accuracy improvement or reduced effort.
