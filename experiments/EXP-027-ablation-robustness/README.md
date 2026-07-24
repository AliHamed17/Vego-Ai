# EXP-027 — Ablation and Robustness

Status: **Proposal — not approved.**

## Question

Which approved mechanism elements are necessary for any observed paired effect
and safety behavior?

## Design

- Run only after the primary external EXP-025 analysis.
- Predeclare ablations before outcome inspection.
- Keep baseline and policy hashes fixed.
- Test removal or restriction of routing, retrieval, conflict, and confidence conditions.

## Outputs

- Ablation effect table.
- Sensitivity and class-balance analysis.
- Failure-mode register.
- Robustness appendix.

## Acceptance

- No external-set tuning.
- Null and harmful ablations are reported.
- Ablation cannot replace or rescue the primary analysis.
- Every configuration remains non-destructive.

## Boundaries

This is explanatory follow-up evidence only. It cannot authorize automatic
correction or a clinical/domain-transfer claim.
