# EXP-023 — Deterministic Policy Development

Status: **Proposal — not approved.**

## Question

Can development-only evidence justify one frozen deterministic parallel policy
without changing the VEGO-AI baseline?

## Entry gate

All conditions are required:

1. At least 20 generalization-safe adjudicated labels.
2. At least three potentially correctable development errors.
3. Errors span at least two settings.
4. EXP-022 advice is relevant, scope-correct, conflict-free, and safe.
5. Iris and Arnon approve one explicit policy record.

## Design

- Use only the 16 development rows.
- Create `PolicyCandidateRecord-v1`.
- Freeze rules, fallback, policy hash, partition hash, and label-set hash.
- Output only `parallel_proposal_only`.
- Preserve baseline on uncertainty, conflict, missing evidence, denial, or timeout.

## Acceptance

- No sealed-holdout or external outcome is used.
- Baseline and protected runtime remain unchanged.
- A single candidate is frozen or policy work stops.

## Boundaries

This experiment authorizes no Agent 4, M4B-2, live hook, or baseline mutation.
