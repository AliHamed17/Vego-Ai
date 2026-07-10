# Chapter 6 — Evaluation Methodology

> Draft. Honest-by-construction: this chapter defines *how* the artifact is evaluated; it states no
> accuracy result and makes no improvement claim, because the generalization-safe expert labels required to
> support such a claim have not yet been collected (see §6.8). Sources: `docs/research/evaluation-plan.md`,
> `docs/research/methodology.md`, `docs/research/expert-labeling-protocol.md`,
> `reports/generated/exp003/annotation_package/`, `artifacts/EVALUATION_STRICT_REVIEW.md`.

## 6.1 Goal and design-science stance

This work is a design-science study (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013), and its evaluation must address two distinct questions that design-science research requires: whether the artifact does what it claims, and whether the artifact produces a beneficial effect.

**Mechanism validity** asks whether the artifact does what it claims structurally. Does the selective intervention policy correctly identify cases where human judgment is needed? Does the feedback manager capture structured, schema-validated feedback? Does the judgment memory store reusable judgments with provenance? Does the advisory layer retrieve relevant memories and present them as graded evidence? Does the parallel comparison produce a deterministic, non-destructive comparison artifact? These questions can be answered by inspecting the implemented pipeline, its tests, and its generated outputs — they do not require independent expert labels.

**Empirical effect** asks whether reusable human judgment changes assessment quality, measured as agreement with *independent expert labels*, relative to the original Agent 4 baseline. This question requires ground truth that does not yet exist, and answering it honestly is the subject of the evaluation protocol defined in this chapter.

The separation between these two questions is important: mechanism validity is established by the current work, while empirical effect is the subject of a carefully designed evaluation protocol whose execution is pending. The methodology defines how to obtain admissible evidence for the second question without compromising the validity already established for the first.

## 6.2 The baseline (C0) and what "ground truth" is *not*

The baseline is the original VEGO-AI Agent 4 variability classification, preserved read-only at tag `official-vego-ai-baseline` (`2eeccb1`): `VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json`. Across the four settings (ucd_ch, ucd_pw, cd_ch, cd_pw) this covers **179 student models** aggregated into **27 recurring variability patterns** (9 Substantial, 18 Occasional, 0 Undetermined).

A critical point governs the entire evaluation design: **the repository contains no independent benchmark.** The author-reviewed files `VEGO-AI/analysis/agentD_variability_classes_*.json` are **byte-identical** to the Agent 4 output for all 27 patterns — every field, including the textual justification, matches exactly. This means they record author *agreement* with Agent 4, not an independent assessment. Using them as ground truth would be grading Agent 4 against itself — a circular evaluation that could not detect either the system's errors or the artifact's improvements.

This finding has a concrete methodological consequence: the only admissible ground truth for evaluating accuracy is **newly collected, independent expert labels** obtained through the protocol defined in §6.6. The byte-identical files remain in the repository as documentation of the baseline's provenance but are never used as evaluation labels.

## 6.3 Conditions (C0–C4B)

The study compares six conditions that correspond to the progressive layers of the artifact. Each condition adds one layer to the previous one, making the contribution chain visible and evaluable at each step.

| Condition | Name | What changes relative to C0 | Primary evidence |
| --- | --- | --- | --- |
| C0 | Original VEGO-AI | None (baseline) | Agent 4 variability classes |
| C1 | Review queue (M1) | Selective human-review triggers activated | Queue size, trigger reasons, coverage |
| C2 | Structured feedback (M2) | Schema-validated expert decisions attached | Resolved queue, signature checks, rationale completeness |
| C3 | Reusable memory (M3) | Provenance-tracked judgment memory built | Memory items, match reasons, conflicts |
| C4A | Advisory layer (M4A) | Memory retrieved as advisory evidence | Advice strength, conflict warnings, `ai_classification_changed = false` |
| C4B | Memory-informed comparison (M4B-1) | Deterministic parallel classification | Original vs memory-informed vs expert labels |

Conditions C0 through C4A are fully implemented and can be evaluated for mechanism validity now. Condition C4B is the controlled experiment whose empirical results depend on independent expert labels.

## 6.4 Metrics

The evaluation uses two tiers of metrics, reflecting the distinction between mechanism validity and empirical effect.

**Primary metrics (C4B, against expert labels, generalization-safe rows only):** accuracy and macro-F1 of the substantial/occasional/undetermined classification, computed separately for the original Agent 4 labels and the memory-informed labels, both compared against the independent expert gold labels.

**Secondary metrics, organized by condition:**

*Targeting (C1):* number and proportion of patterns queued, distribution of trigger reasons (human_review, undetermined, low_confidence, guidelines_update), and coverage — the proportion of eventually-incorrect Agent 4 classifications that are captured by the review queue.

*Capture (C2):* schema validity rate, rationale completeness rate, signature-mismatch rate (should be zero under stable baselines), and the proportion of feedback marked as reusable.

*Retrieval (C3/C4A):* match count per query, explainable match-reason distribution, advice-strength distribution (none/weak/moderate/strong/conflicting), and conflict rate.

*Comparison (C4B):* the count of `memory_informed_differs_from_original`; a paired correctness table (changed-and-correct, changed-and-wrong, unchanged-correct, unchanged-wrong); a McNemar-style test where sample size permits; and escalation precision/recall — the proportion of `requires_human_review_after_memory` flags that correspond to actual baseline errors.

*Reliability:* inter-rater agreement (Cohen's κ) between the two independent reviewers; the proportion of items requiring adjudication; and the agreement between individual reviewer labels and the adjudicated gold labels.

### Running example: how the "Customer as actor" row would be evaluated

Returning to the running example from §4.4 and §5.6, the "Customer as actor" comparison record (ucd_ch P6) illustrates the evaluation design. Its `evaluation_leakage_status` is `same_pattern_memory_used` — the memory entry `HJM-ucd_ch-P6` was derived from feedback about this exact pattern. Even if an independent expert labels P6 as Substantial (agreeing with the human memory rather than Agent 4), this agreement cannot count toward generalization-safe accuracy, because the memory was not applied to a genuinely new case. The row is included in the mechanism-validation sheet but excluded from the primary evaluation set of 24 generalization-safe patterns. This per-row tagging is what makes the leakage discipline (§6.5) operational rather than merely conceptual.

> **Figure 6.1.** Evaluation workflow: independent expert annotation, leakage-filtered comparison, and evidence gates. See `thesis/figures/fig-6-1-evaluation-workflow.mmd`.

## 6.5 Leakage discipline

The evaluation faces a specific methodological challenge: the judgment memory may contain entries that are derived from the same pattern being evaluated, creating a feedback loop that inflates apparent accuracy. This is the same-pattern leakage problem.

Every C4B comparison row is tagged with an `evaluation_leakage_status` from a defined set: `none` (no memory leakage), `same_pattern_memory_used` (memory derived from the same pattern), `same_setting_memory_used` (memory from the same setting but a different pattern), `cross_setting_memory_used` (memory from a different setting), and `unknown`. Same-pattern reuse demonstrates the *mechanism* (the system can retrieve and apply a relevant past judgment) but cannot prove *generalization* (the system can apply past judgments to genuinely new cases). Same-pattern rows are therefore excluded from all generalization-safe metrics.

Generalization evidence must come from one of four designs: leave-one-pattern-out (use memory from 26 patterns to inform the 27th), cross-setting transfer (use memory from one domain to inform another), cross-diagram transfer (use memory from UCD to inform CD, or vice versa), or expert-holdout (use memory from development rows to inform sealed holdout rows).

In the current run, the three existing memory-derived labels are all `same_pattern`, yielding **0 generalization-safe labeled rows** — the binding constraint on this evaluation.

## 6.6 Independent expert annotation protocol

To obtain admissible ground truth, an independent annotation study is defined, with bias and leakage controls that are integral to validity.

**Unit and labels.** Each *pattern* (not each student model) receives one of three labels: `Substantial Variability`, `Occasional Variability`, or `Undetermined / Needs Review`. Each label is accompanied by a written rationale explaining the reviewer's reasoning and a confidence rating.

**Scope.** The **24 generalization-safe** patterns form the primary evaluation set. The **3 same-pattern** rows are isolated in a separate mechanism-validation sheet and excluded from generalization claims — they can show that retrieval works but not that it generalizes.

**Blind, neutral context.** Reviewers see only neutral context for each pattern: an anonymous item identifier, the setting (domain and diagram type), the pattern description, the affected student models (by count), the related guideline, and neutral cited evidence from the student submissions. All AI-derived fields — the original Agent 4 label and justification, the memory-advice strength, the memory-informed classification, the leakage status, and internal priority/ranking fields — are withheld to prevent anchoring bias. These fields appear only in an adjudication-internal audit sheet that is not shown to the initial reviewers.

**Anonymization and randomization.** Items carry an `anonymous_item_id`; the mapping between anonymous IDs and actual pattern IDs is stored in a private file (`item_mapping_PRIVATE.csv`) that is not shared with reviewers. Row order is randomized **separately per reviewer** to prevent order effects.

**Two reviewers plus adjudicator.** Two independent modeling experts label all 24 generalization-safe rows. A third expert adjudicates disagreements, informed by both reviewers' labels and rationales plus the audit-sheet context. Cohen's κ is computed from the two independent reviewers' labels before adjudication. Raw reviewer returns are preserved unchanged; the final adjudicated labels are frozen in a distinct gold-label file that becomes the sole ground truth for all subsequent analysis.

**Ethics gate.** Reviewer consent, anonymity, and any IRB documentation requirements are confirmed with the supervisor before outreach. The data contain no personal student information — student models are pseudonymous and identified only by case number within their setting.

**Panel selection.** Qualified, *available* modeling experts are prioritized over prominence. Reviewers should have experience with UML use-case and class diagrams and with the concept of valid modeling alternatives. A human–AI specialist may review the interaction protocol but is not the sole UML annotator.

## 6.7 Sealed development/holdout split for any policy refinement

The current deterministic policy (M4B-1, `memory-informed-classifier-v1`) changes **0 of 27** classifications. This means that under the current policy, original and memory-informed accuracy are identical by construction — no labeling, real or synthetic, can produce a difference. A delta is only possible if a future deterministic refinement (M4B-1.1) is justified by error analysis showing that specific policy rows should be adjusted.

To prevent optimistic bias from such a refinement, the 24 generalization-safe rows are split **16 development / 8 sealed holdout**, with the split recorded privately in `item_mapping_PRIVATE.csv`. Both reviewers label all 24 rows (they do not know which are development and which are holdout). Error analysis and policy-rule design use the 16 development rows only. The 8 holdout labels remain sealed — not inspected, not analyzed, not used in any design decision — until the refined policy is frozen. The holdout is then evaluated **once**, and the result is reported without post-hoc adjustment.

Tuning and evaluating on the same rows is prohibited. M4B-1.1 remains design-only and blocked (`docs/research/m4b1-policy-refinement-plan.md`). M4B-2 (LLM-based reclassification) is out of scope for this thesis.

## 6.8 Evidence gates (what each label count permits)

The evaluation defines explicit gates that link the available evidence to the permitted claims. These gates are enforced by the evaluation harness and the evidence-consistency guard.

| Generalization-safe expert labels | Permitted reporting |
| --- | --- |
| 0 (current) | "Accuracy improvement cannot be evaluated yet." Mechanism, traceability, and escalation evidence only. |
| 1–19 | Pilot/exploratory results only, with explicit small-sample threats and no strong quantitative claim. |
| ≥20 | Quantitative original-vs-memory-informed-vs-expert results, with stated limitations (narrow scope, conservative policy, small sample). |
| +2nd reviewer / adjudication | Strengthened label reliability (κ reported); stronger claims about expert-label validity. |

These gates serve a dual purpose. For the thesis, they define what claims the current evidence supports. For the reader, they make the evidence boundary transparent — there is no ambiguity about what has and has not been shown.

## 6.9 Reproducibility and instrumentation

All evaluation runs are deterministic and offline — no API or LLM calls are needed. The evaluation harness `VEGO-AI/analysis/evaluate_accuracy_improvement.py` consumes a labels CSV and emits: per-row comparisons between original, memory-informed, and expert labels; leakage-tiered accuracy and macro-F1; a paired correctness table; error-type analysis; and escalation precision/recall. The harness refuses to assert improvement while the count of generalization-safe labels is below 20.

Cross-report numeric invariants and the frozen baseline/policy are checked by `scripts/check_evidence_consistency.py`, which runs at the start and end of every agent prompt. The guard verifies 18 consistency checks, including: baseline outputs unchanged, `ai_classification_changed = 0`, no forbidden tracked artifacts, and no claim-language violations.

Every result maps to a registered experiment ID (EXP-001 through EXP-005), a specific git commit, and gitignored generated outputs under `reports/generated/`. The experiment registry (`experiments/registry.md`) documents each experiment's purpose, inputs, outputs, and current status.

Reproduction commands:

```bash
# Rebuild the M4B-1 comparison from baseline + human feedback
python -m VEGO-AI.framework.memory_informed_classifier

# Run the evaluation harness (requires labels CSV)
python VEGO-AI/analysis/evaluate_accuracy_improvement.py --labels <gold_labels.csv>

# Verify evidence consistency
python scripts/check_evidence_consistency.py

# Run the full test suite
python -m pytest VEGO-AI/tests -q
```

## 6.10 Summary

The methodology cleanly separates *mechanism validity* (established by the implemented pipeline, its 94 passing tests, and its generated artifacts) from *empirical effect* (pending independent expert labels). It defines a bias- and leakage-controlled annotation study to obtain admissible ground truth, pre-commits to a sealed development/holdout discipline so that any future policy refinement is evaluated honestly, and establishes explicit evidence gates that link label counts to permitted claims.

Under the current evidence, the only supportable claims concern reusable human judgment, traceability, and escalation — not classification accuracy. The methodology itself is a contribution: it identifies a subtle but important evaluation pitfall (the byte-identical baseline labels) and designs a protocol that avoids it, providing a template for evaluating similar human–AI collaboration artifacts in the future.
