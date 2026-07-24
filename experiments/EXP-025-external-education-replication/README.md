# EXP-025 — External Education-Domain Replication

Status: **Proposal — not approved.**

## Question

Does a policy frozen before data collection retain a positive paired effect on
a new education-domain batch?

## Design

- Collect at least 30, target 48, new independently labeled patterns.
- Use two reviewers and adjudication.
- Keep the approved candidate policy frozen.
- Run the preregistered paired analysis once.

## Formal gate

All conditions must pass:

- External generalization-safe adjudicated N is at least 30.
- Net-correction paired-bootstrap 95% interval excludes zero.
- Exact McNemar `p < 0.05`.
- Macro-F1 does not decline.
- No predefined setting or class subgroup shows material harm.
- Baseline and protected-path hashes remain unchanged.

## Outputs

- External paired report.
- Confidence intervals and exact test.
- Subgroup safety analysis.
- `EvaluationRunManifest-v2`.

## Boundaries

This remains education-domain research. It supports no clinical claim or
automatic deployment. If any gate fails, no formal improvement claim is made.
