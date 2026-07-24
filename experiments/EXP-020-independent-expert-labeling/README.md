# EXP-020 — Independent Expert Labeling

Status: **Pending expert input.**

## Question

What adjudicated labels do two independent reviewers assign to the 24 current
generalization-safe patterns?

## Design

- Two reviewers label all 24 blind rows independently.
- AI output, memory advice, leakage class, and 16/8 partition are hidden.
- Compute Cohen's kappa before adjudication.
- Preserve raw returns; write final decisions as `GoldLabelRecord-v2`.

## Outputs

- Reviewer-1 and reviewer-2 immutable returns.
- Agreement and disagreement report.
- Adjudication record.
- Frozen gold-label manifest and hashes.

## Acceptance

- All rows contain permitted label, rationale, confidence, reviewer, and date.
- Synthetic or AI-generated reviewers are rejected.
- Missing, blank, and unknown-provenance labels cannot enter the gold set.
- Disagreements are resolved by an adjudication role.

## Boundaries

At 1-19 safe labels, results are pilot-only. At 20-24, quantitative MSc
reporting is allowed only with small-sample limitations. Label collection does
not authorize a policy or runtime change.
