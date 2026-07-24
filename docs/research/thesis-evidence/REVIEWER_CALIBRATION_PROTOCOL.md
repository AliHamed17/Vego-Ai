# Reviewer Calibration Protocol — EXP-019

Status: **Evaluation-ready; supervisor approval and two reviewers required.**

## Purpose

Calibrate the label vocabulary and rationale standard without consuming any of
the 24 generalization-safe evaluation rows. The three current same-pattern rows
are suitable because they are already excluded from every primary
generalization metric.

## Inputs

- Three anonymized same-pattern rows.
- The approved reviewer instructions.
- The three permitted labels.
- A calibration-only copy of the blind sheet.

Do not show reviewers Agent 4 output, memory advice, current comparison output,
leakage details, or the existing memory-derived judgment before their independent
responses are locked.

## Procedure

1. Reviewer 1 labels all three rows independently.
2. Reviewer 2 labels all three rows independently.
3. Freeze both calibration returns and record their hashes.
4. Compare labels, rationales, confidence, and ambiguous terms.
5. Discuss disagreements as protocol interpretation issues, not as majority voting.
6. Record each clarification in a versioned protocol-change log.
7. Repeat only if a major ambiguity remains; do not rehearse the 24 evaluation rows.
8. Freeze the final instruction version before EXP-020 begins.

## Calibration discussion prompts

- Which evidence distinguishes a valid alternative from a misconception?
- When should `Undetermined / Needs Review` be used?
- What minimum rationale is sufficient for later adjudication?
- Does the row contain information that invites guessing beyond the provided context?
- Are reviewer confidence levels being used consistently?

## Acceptance

- Both reviewers complete all three rows.
- Every field validates against `GoldLabelRecord-v2`.
- Every disagreement and clarification is recorded.
- The final instructions have a version and SHA-256 hash.
- Calibration rows remain marked `generalizationSafe = false`.
- No calibration label is copied into EXP-020, EXP-021, EXP-024, or EXP-025.

## Output

- Two immutable calibration returns.
- One calibration disagreement log.
- One approved instruction version.
- One signed decision that EXP-020 may begin.

## Claim boundary

Calibration demonstrates reviewer preparation and protocol clarity only. It
does not measure Agent 4 accuracy, memory accuracy, policy performance, or
generalization.
