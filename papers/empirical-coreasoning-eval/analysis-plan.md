# Paper B — Pre-Registered Analysis Plan

> **Committed 2026-06-30, before any independent expert label is seen.** Baseline tag
> `official-vego-ai-baseline` (`2eeccb1`); policy `memory-informed-classifier-v1`. No analysis below may be
> altered after labels are observed; deviations must be reported as exploratory.

## 1. Questions (neutral; not predictions of improvement)
- **Q1 (targeting).** What share of baseline errors does selective review (M1) capture (coverage), and at
  what queue cost (40.7% now)?
- **Q2 (escalation).** Of `requires_human_review_after_memory` flags, what fraction correspond to actual
  baseline errors (escalation precision), and what fraction of errors are flagged (recall)?
- **Q3 (accuracy, gated).** On generalization-safe rows, how do original and memory-informed labels compare
  to expert gold? *Under policy v1 the two label sets are identical, so the expected delta is 0 by
  construction — a non-result that bounds the v1 contribution, not evidence of improvement.*
- **Q4 (refinement, conditional).** Do development-row errors justify a deterministic refinement (M4B-1.1)?

## 2. Data & splits
- Unit = recurring pattern. Generalization-safe set = 24 (19 `none` + 5 `cross_setting`); same-pattern (3)
  excluded from all accuracy/escalation metrics.
- Split **16 development / 8 sealed holdout** (`exp003/annotation_package/item_mapping_PRIVATE.csv`).
- Both reviewers label all 24 blind to the split; κ and adjudication recorded.

## 3. Metrics (fixed)
- Targeting: queue rate, trigger distribution, coverage of baseline errors.
- Escalation: precision, recall (on safe rows).
- Accuracy (gated ≥20): accuracy, macro-F1 (original vs memory-informed vs gold); paired-correctness table
  (changed-correct / changed-wrong / unchanged-correct / unchanged-wrong); McNemar where N permits.
- Reliability: Cohen's κ; adjudication rate; reviewer↔gold agreement.

## 4. Evidence gates (decision rules, pre-committed)
- 0 safe labels → "not evaluable"; **1–19** → pilot/qualitative only; **≥20** → quantitative (with threats);
  reviewer-2/adjudication present → reliability strengthened.
- **M4B-1.1 adopted only if**, on development rows under leave-one-pattern-out, it improves safe macro-F1
  **without increasing changed-and-wrong**; then frozen and evaluated **once** on the 8 holdout.

## 5. Stopping / falsification
- If escalation precision is low and no safe accuracy signal emerges at ≥20 labels, the honest reported
  outcome is "mechanism + methodology contribution; no measured effect" — this is an admissible result.
- Same-pattern agreement rates are never reported as effect evidence.
