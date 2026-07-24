# EXP-019 — Reviewer Calibration

Status: **Evaluation-ready; supervisor approval and two human reviewers required.**

## Question

Can two reviewers apply the label vocabulary and rationale standard consistently
before the blind evaluation begins?

## Design

- Use the three same-pattern rows already excluded from generalization metrics.
- Collect two independent blind returns.
- Freeze and hash both returns before discussion.
- Discuss disagreements and clarify the protocol.
- Freeze the revised instruction version before EXP-020.

## Outputs

- Calibration disagreement log.
- Reviewer-return hashes.
- Versioned instruction record.
- Go/defer decision for EXP-020.

## Acceptance

- Both reviewers complete all three rows.
- Required fields validate against `GoldLabelRecord-v2`.
- Calibration rows remain `generalizationSafe = false`.
- No calibration label is transferred into evaluation.

## Boundaries

No accuracy, generalization, policy, or reviewer-reliability claim is made from
three calibration rows. No implementation code or baseline output changes.
