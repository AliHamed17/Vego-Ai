# M4B-1.1 Policy Refinement Plan (DESIGN ONLY — not approved, not implemented)

Created: 2026-06-16. Status: **design draft, BLOCKED.** No code changes. Do **not** implement until
(1) ≥20 generalization-safe expert labels exist (EXP-003), (2) Phase-3 error analysis is run on those
labels, and (3) the supervisor/reviewer approves a specific rule change. Today: *"Accuracy improvement
cannot be evaluated yet."*

> This document only *designs* a possible deterministic refinement of `memory_informed_classifier.py`
> (current `POLICY_VERSION = "memory-informed-classifier-v1"`). It commits to nothing. No LLM/API, no
> embeddings, no Agent-4 change, no M4B-2, no baseline overwrite — under any refinement considered here.

## 1. Baseline errors discovered (to be filled from EXP-003)
**Currently empty by design.** There are 0 generalization-safe expert labels, so we do not yet know where
Agent 4 is wrong. After EXP-003 (`evaluate_accuracy_improvement.py` → `error_analysis.csv`), fill:
- error-type distribution (false_substantial / false_occasional / ambiguous / guideline_update_missed),
- errors by setting / diagram type / confidence / advice strength,
- the specific patterns Agent 4 misclassified vs the expert.

Until that table exists, every "proposed rule" below is a *hypothesis*, not a justified change.

## 2. Which errors reusable memory could plausibly help
Memory can only help where (a) a relevant, conflict-free, **leakage-safe** human judgment exists, and
(b) that judgment disagrees with a **low/medium-confidence** original classification. The current run shows
this is rare: only 2/27 rows have moderate+ memory disagreement (both already escalated), and 0 rows have a
*strong, leakage-safe* disagreement. So the realistic near-term help is **escalation** (Strategy A), not
automatic correction.

## 3. Current policy (v1) limitations
- **Conservative by construction:** v1 proposes a different class only on *strong disagreement*, which did
  not occur (0/27 differ). So "0 differences" is partly a policy property, not only the data.
- It does not use **original confidence** as a gate (a Medium/Low original + strong memory could justify a
  *proposed* alternative; v1 ignores confidence).
- It does not use a **memory match-score threshold** (advisory vs proposal).
- `needs_guideline_update` memory and `valid_alternative` decision types are not mapped to distinct actions.

## 4. Proposed deterministic rule changes (candidate; choose AFTER error analysis)
All proposals keep `ai_behavior_changed_in_baseline = false` and write only the parallel comparison.

1. **Confidence-gated strong correction:** if `advice_strength == strong` AND conflict-free AND leakage-safe
   AND `original_confidence ∈ {Low, Medium}` AND memory disagrees → *propose* the memory-supported class
   (parallel only) + `requires_human_review`. If original confidence is High → escalate, do not propose.
2. **Decision-type mapping:** `valid_alternative → Substantial`; `modeling_error → Occasional`;
   `needs_guideline_update → flag guideline review` (no class change); `ambiguous → human review`;
   `domain_specific → follow reuse_scope` (only within scope).
3. **Conflict handling:** `conflict_status == needs_adjudication → human review only` (never auto-propose).
4. **Leakage gate:** exclude `same_pattern_memory_used` from any performance claim; allow proposals only on
   leakage-safe memory.
5. **Match-score threshold:** match score ≥3 → eligible for proposal; =2 → advisory only; <2 → no memory.

## 5. Expected effect (hypothesis, to be tested)
- Likely increases `requires_human_review_after_memory` (more escalation) and may produce a small number of
  *changed* rows where memory is strong + original confidence low. Net accuracy effect is **unknown** and
  must be measured leave-one-pattern-out on safe labels — it could be neutral, positive, or negative.

## 6. Risks
- **Overfitting** rules to a tiny label set; **single-rater** bias; **leakage** if gates are mis-set;
  conservative-vs-aggressive trade-off (more changes = more changed-and-wrong risk);
  guideline-update memory wrongly driving class changes. Mitigate with leave-one-pattern-out + 2 raters.

## 7. Evaluation protocol (how a refinement would be judged)
Run `evaluate_accuracy_improvement.py` on the same expert labels for **v1 vs v1.1**, reporting on
**generalization-safe rows only**: accuracy, macro-F1, changed-and-correct, changed-and-wrong, escalation
precision/recall vs baseline errors, and a McNemar-style paired table. A refinement is adopted **only if**
it improves safe macro-F1 without increasing changed-and-wrong, under leave-one-pattern-out.

## 8. Rollback plan
v1.1 would ship behind a new `policy_variant` field (`memory-informed-classifier-v1.1`) on a feature branch
`feature/m4b1-policy-refinement`, writing only `memory_informed_comparison.json`. Rollback = revert the
branch / set variant back to v1; baseline `eval_output/` and Agent 4 are never touched, so rollback is total
and risk-free. v1 remains the default until v1.1 demonstrates safe improvement.

## 9. Gate (repeat)
Implementation (Phase 7) stays **BLOCKED** until: ≥20 safe expert labels + Phase-3 error analysis + explicit
approval. No code in `memory_informed_classifier.py` / schemas / tests changes before then.
