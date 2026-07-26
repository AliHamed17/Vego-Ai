# EXP-037 — Paper baseline reconciliation

## Question

Which values in the MAS4MODELS paper draft can be aligned with the frozen
repository baseline, and which values are only contextual?

## Method

- Bind the reviewed paper extraction to the local PDF SHA-256 and page/table.
- Reconcile paper-reported model and pattern counts with the current locked
  repository snapshot.
- Keep Phase A–C metrics attached to their original agents and evaluation
  protocols.
- Treat Phase D as qualitative author assessment, not independent ground
  truth.
- Compare H-layer capabilities as implemented system properties, not as
  classification accuracy.

## Acceptance

- Every paper value has a page/table reference.
- Count differences are reported without calling them improvements.
- No Phase A–C score is reused as an H-layer accuracy metric.
- Classification improvement remains not measurable at safe N=0.

## Claim boundary

This experiment supports provenance and architecture-version reconciliation.
It cannot prove that the current system is more accurate than the paper.
