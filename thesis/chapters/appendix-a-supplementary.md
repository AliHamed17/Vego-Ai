# Appendix A — Supplementary Materials

## A.1 M4B-1 policy table (complete)

The deterministic comparison policy maps each combination of advisory evidence to an outcome. The policy version is `memory-informed-classifier-v1`.

| # | Advice strength | Agreement with original | Conflict status | Outcome | `requires_human_review_after_memory` |
| --- | --- | --- | --- | --- | --- |
| 1 | none | — | — | Keep original | false |
| 2 | weak | — | — | Keep original | false |
| 3 | moderate | agree | none | Keep original | false |
| 4 | moderate | disagree | none | Keep original | true |
| 5 | strong | agree | none | Keep original | false |
| 6 | strong | disagree | none | Propose memory-supported alternative (parallel artifact only) | true |
| 7 | any | — | conflicting | Keep original | true |

Under the current data, row 4 is exercised by the "Customer as actor" pattern (ucd_ch P6). Rows 6 and 7 have not been exercised because no strong-disagreement or conflicting-memory cases exist in the current run. The policy changes zero of 27 classifications.

## A.2 Schema overview

The artifact chain uses six JSON schemas, each enforcing structural contracts at write time:

| Schema file | Layer | Key enforced fields |
| --- | --- | --- |
| `human_review_queue.schema.json` | M1 | `review_id`, `review_signature`, `source_pattern_id`, `trigger_reasons` |
| `human_feedback.schema.json` | M2 | `decision` (enum), `rationale` (required for non-approve), `reviewer_id`, `timestamp` |
| `human_judgment.schema.json` | M3 | `memory_id`, `memory_signature`, `source_review_id`, `reuse_scope`, `conflict_status` |
| `memory_advice.schema.json` | M4A | `advice_strength` (enum), `match_reasons`, `advice_mode = "advisory_only"` (const), `ai_classification_changed = false` (const) |
| `memory_informed_comparison.schema.json` | M4B-1 | `policy_version`, `decision_trace`, `mode = "experimental"` (const), `ai_behavior_changed_in_baseline = false` (const), `evaluation_leakage_status` |
| `review_signature.schema.json` | M1.2 | `signature_hash`, `source_fields`, `computation_method` |

The `const` fields in M4A and M4B-1 schemas are architectural guarantees: they cannot be overridden at runtime, making non-destruction a machine-verified property rather than a convention.

## A.3 Blind annotation sheet structure

Each reviewer receives a CSV with the following columns (AI-derived fields are withheld):

| Column | Description | Source |
| --- | --- | --- |
| `anonymous_item_id` | Randomized identifier (differs per reviewer) | Generated |
| `setting` | Domain and diagram type (e.g., "Cheers — Use-Case Diagram") | Baseline |
| `pattern_description` | Neutral description of the recurring deviation | Agent 4 output (neutralized) |
| `affected_student_models` | Count of models exhibiting this pattern | Agent 3 aggregation |
| `related_guideline` | The reference guideline the pattern relates to | Agent 2 output |
| `cited_evidence` | Neutral evidence excerpts from student submissions | Agent 3 output (neutralized) |
| `expert_label` | *Empty — to be filled by reviewer* | — |
| `expert_rationale` | *Empty — to be filled by reviewer* | — |
| `expert_confidence` | *Empty — to be filled by reviewer* | — |

**Withheld fields** (hidden from reviewers, present only in the adjudication audit sheet): `original_ai_label`, `ai_justification`, `memory_advice_strength`, `memory_informed_label`, `evaluation_leakage_status`, `priority_rank`.

Row order is randomized separately per reviewer to prevent order effects. The mapping between `anonymous_item_id` and actual pattern IDs is stored in `item_mapping_PRIVATE.csv`, which is not shared with reviewers.

## A.4 Evidence-consistency guard invariants

The guard (`scripts/check_evidence_consistency.py`) verifies 18 invariants at every agent prompt:

1. Baseline `eval_output/` files unchanged from tagged commit
2. `ai_classification_changed = 0` across all comparison records
3. `ai_behavior_changed_in_baseline = false` in all M4B-1 records
4. No forbidden tracked artifacts in `eval_output/`
5. Policy version matches `memory-informed-classifier-v1`
6. All M4A records have `advice_mode = "advisory_only"`
7. Memory-informed classifications that differ from original = 0
8. No claim-language violations in tracked documentation
9. Baseline tag `official-vego-ai-baseline` resolves to expected commit
10. All schema-validated artifacts pass their respective JSON schemas
11. Review signature integrity across M1–M2 chain
12. Memory provenance chain integrity (M2→M3 linkage)
13. Leakage status tags present on all comparison records
14. Generalization-safe label count matches reported value
15. No synthetic labels in real-evidence reporting paths
16. Current verified inventory passes (106 VEGO-AI tests, 89 research-infrastructure tests plus 7 subtests, and 39 offline H-layer tests)
17. No M4B-1.1 or M4B-2 code in the active codebase
18. Dashboard figures consistent with source data

## A.5 AI review loop architecture

The thesis quality assurance process uses an automated review loop with eight validators organized in three groups. The loop runs after each editing cycle and feeds issues back for correction before the next cycle.

> **Figure A.1.** AI review loop architecture for thesis quality assurance. See `thesis/figures/fig-ai-review-loop.mmd`.

**Structural validators** check that all section cross-references (§X.Y) resolve to real headings, all figure references match existing figure files, and all in-text citations appear in the reference list.

**Consistency validators** verify uniform terminology across chapters (e.g., "human–AI" with en-dash, "M4B-1" with hyphen, "Agent 4" with space) and confirm the "Customer as actor" running example threads correctly through chapters 1, 4, 5, 6, 7, 8, and 9 with consistent data.

**Evidence and claim guards** enforce the evidence gates: with 0 of 24 expert labels, no accuracy-improvement claim is permitted. The claim-language guard scans all chapters for forbidden language, and the evidence-consistency guard runs 18 automated invariant checks.

## A.6 Reproduction checklist

| Step | Command | Expected result |
| --- | --- | --- |
| Build M4B-1 comparison | `python -m VEGO-AI.framework.memory_informed_classifier` | 27 comparison records, 0 differ from original |
| Run evaluation harness | `python VEGO-AI/analysis/evaluate_accuracy_improvement.py --labels <gold_labels.csv>` | Requires labels CSV; refuses to assert improvement with <20 labels |
| Verify evidence consistency | `python scripts/check_evidence_consistency.py` | 18/18 checks pass |
| Run test inventories | `python -m pytest VEGO-AI/tests scripts/tests tests/hlayer_offline -q` | 106 VEGO-AI tests, 89 research-infrastructure tests plus 7 subtests, and 39 offline H-layer tests pass |
| Build results dashboard | `python VEGO-AI/analysis/build_results_dashboard.py` | Dashboard with milestone summaries |

## A.7 RQ and hypothesis traceability

This table is a design-time traceability register. EXP-019 through EXP-027 are
registered protocols, not completed empirical results.

| Research item | Experiment path | Primary measure | Gate | Thesis location | Current evidence state |
| --- | --- | --- | --- | --- | --- |
| E-RQ1 / H1 | EXP-019, EXP-020, EXP-021 | Reviewer agreement, baseline error taxonomy | Two independent reviews and adjudicated labels; at least 20 safe rows for quantitative reporting | Chapters 3, 6, 7 | Pending expert input |
| E-RQ2 / H2 | EXP-021, EXP-022 | Routing precision/recall; retrieval relevance, scope, and conflict rate | Development labels only; same-pattern rows excluded from generalization-safe measures | Chapters 3, 5, 6, 7 | Blocked by EXP-020 |
| E-RQ3 / H3 | EXP-023, EXP-024, EXP-025 | Net correction, macro-F1 non-decline, exact McNemar test | One approved frozen policy; one-time eight-row holdout; external N >= 30 for a formal claim gate | Chapters 3, 6, 8, 9, 10 | Proposal - not approved |
| H4 | EXP-026 | Review time, repeated-question rate, and escalation quality | Ethics/consent approval and controlled reviewer study | Chapters 3, 6, 8, 9 | Proposal - not approved |
| Robustness | EXP-027 | Predeclared ablation and subgroup safety measures | Primary external analysis completed without policy retuning | Chapters 6, 8, 9 | Proposal - not approved |
