# Paper B — Outline

## 1. Introduction
- The question Paper A made answerable: does reusable human judgment help, clarify, or safely escalate
  variability decisions — measured honestly, on generalization-safe rows.

## 2. Study setup
- VEGO-AI conditions C0–C4B; 179 cases / 27 patterns / 4 settings.
- Label set: 24 generalization-safe candidates (19 `none` + 5 `cross_setting`); 16 development / 8 sealed
  holdout; both reviewers label all 24 blind to the split.

## 3. Pre-registered analysis plan
- Summarize `analysis-plan.md`: hypotheses, metrics, gates, decision and stopping rules (committed before
  labels).

## 4. Results — targeting & escalation (mechanism-level; partly available now)
- Targeting rate (11/27 = 40.7%), trigger distribution; escalation count (2/27) and, with labels,
  escalation precision/recall and coverage.

## 5. Results — leakage-safe accuracy & reliability (GATED)
- Reported only at ≥20 safe labels: accuracy / macro-F1 of original vs memory-informed vs expert gold on
  safe rows; paired-correctness table; McNemar; Cohen's κ and adjudication rate. *(Placeholder tables.)*

## 6. Error analysis & policy-refinement decision
- Development-row error taxonomy (false_substantial / false_occasional / ambiguous / guideline-update).
- M4B-1.1 is designed/evaluated **only if** dev errors justify it; holdout evaluated once after freeze.

## 7. Threats to validity (Ch 8). 8. Conclusion (honest, gate-bounded).
