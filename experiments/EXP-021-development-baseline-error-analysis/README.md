# EXP-021 — Development Baseline Error Analysis

Status: **Blocked on EXP-020.**

## Question

Where does the frozen Agent 4 baseline disagree with adjudicated experts on the
16-row development partition?

## Design

- Open only development labels.
- Keep eight holdout labels sealed and unread.
- Build confusion matrices, per-class measures, and a rationale-backed error taxonomy.
- Record setting, class, confidence, and potential memory relevance.

## Outputs

- Development baseline report.
- Error taxonomy.
- Setting-by-error heatmap.
- Candidate-correctability register.

## Acceptance

- Every error traces to an adjudicated human rationale.
- Holdout hash and seal state remain unchanged.
- The experiment selects no policy rule.
- Null findings are retained.

## Boundaries

Development error prevalence is local to this sample. It does not establish
holdout performance, external validity, or a generalization claim.
