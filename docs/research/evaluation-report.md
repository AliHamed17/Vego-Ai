# Evaluation Of Reusable Human Judgment In VEGO-AI

Last curated update: 2026-06-17 00:45 +03:00 by Codex.

Status: EXP-001 mechanism/readiness evaluation complete; EXP-002/EXP-003 labeling and accuracy tooling generated; EXP-004 synthetic policy-risk screening complete; EXP-005 real-label gate package added; human labels still pending.

## Evaluation Position

VEGO-AI is now past the core implementation phase through M4B-1. The implemented artifact supports the claim that VEGO-AI can be extended with a reusable human-judgment layer that enables human-AI co-reasoning in domain model assessment without replacing the original AI decision pipeline.

The next work is empirical evaluation, not additional feature building.

## Frozen Implementation Anchors

| State | Anchor | Use |
| --- | --- | --- |
| Official baseline | `official-vego-ai-baseline` / `baseline/official-vego-ai` | Original VEGO-AI preservation. |
| M4B-1 implementation baseline | `research-state-m4b1-deterministic-comparison` / `944c922` | Primary implementation freeze for M1-M4A + dashboard + M4B-1. |
| Visualizer UX validated state | `research-state-visualizer-ux-clean` / `78b261e` | Model/result mismatch fix and read-only analysis UI. |
| Current coordination state | `main` / latest pushed commit | Memory, dashboard, and documentation sync. |

Do not move stable tags. Any future implementation work should use a new branch/PR and must not overwrite baseline outputs.

## Artifact Bundle

GitHub release:

- Tag: `research-state-m4b1-deterministic-comparison`
- Release title: `M1-M4A + Dashboard + M4B-1 (944c922)`
- ZIP asset: `vego-ai-M1-M4A-dashboard-M4B1-changes.zip`
- Manifest asset: `M1-M4A-dashboard-M4B1-manifest.md`

These assets are suitable for external technical review of the implemented prototype. They are not a substitute for empirical evaluation.

## Implemented Mechanism

```text
AI detects where human review is needed
  -> human feedback is captured structurally
  -> feedback becomes reusable Human Judgment Memory
  -> memory is retrieved as advisory evidence
  -> memory-informed comparison is generated in parallel
  -> original VEGO-AI output remains untouched
```

## Evaluation Questions And Measures

| Evaluation Question | What To Measure | Evidence Source |
| --- | --- | --- |
| Where does VEGO-AI need human review? | Number of review items, trigger reasons, review coverage. | M1 review queue outputs, dashboard counts. |
| How much feedback becomes reusable? | Resolved feedback count, `reusable=true` count, rationale completeness. | M2 resolved queue and feedback records. |
| Does memory retrieve relevant judgments? | Top-k relevance, match reasons, conflict status, human relevance rating. | M3 retrieval traces and M4A memory matches. |
| Does M4A advice help? | `advice_strength` distribution, reviewer usefulness rating, conflict warnings. | `memory_advice.json`, expert review notes. |
| Does M4B-1 differ from original? | `memory_informed_differs_from_original`, classification change meaning. | `memory_informed_comparison.json`. |
| Where is human still needed after memory? | `requires_human_review_after_memory`, conflict or moderate disagreement cases. | M4B-1 comparison records. |
| Does memory improve expert alignment? | Original vs memory-informed vs expert labels. | Expert label table and comparison outputs. |
| Does it generalize? | Leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert holdout results. | EXP-001 evaluation protocol and held-out outputs. |

## Initial EXP-001 Run

Command:

```powershell
.\scripts\build-exp001-evaluation.ps1
```

Input run:

- `VEGO-AI/runs/20260614-122150/human/`

Generated local outputs, ignored by Git:

- `reports/generated/exp001/exp001_evaluation_dataset.csv`
- `reports/generated/exp001/exp001_evaluation_table.md`
- `reports/generated/exp001/exp001_summary.json`
- `reports/generated/exp001/exp001_summary.md`

### Available Label Sources

| Source | Availability | Evaluation Role |
| --- | --- | --- |
| Agent D baseline classifications | Available for four settings | Original AI classification baseline, not expert truth. |
| M4B-1 memory-informed comparison | Available for four settings | Parallel comparison output. |
| Human Judgment Memory labels | Available for three `ucd_ch` patterns | Mechanism validation labels only; all are same-pattern. |
| Independent held-out expert labels | Not available yet | Required before accuracy/generalization claims. |

### Dataset Summary

| Measure | Value |
| --- | ---: |
| M4B-1 comparison rows | 27 |
| Settings covered | 4 |
| Expert-labeled rows available from reusable memory | 3 |
| Generalization-safe expert-labeled rows | 0 |
| Memory-informed classifications differing from original | 0 |
| Human-review-after-memory flags | 2 |
| Conflicting memory flags | 0 |

### Distributions

| Distribution | Values |
| --- | --- |
| Settings | `cd_ch=4`, `cd_pw=7`, `ucd_ch=8`, `ucd_pw=8` |
| Advice strength | `none=19`, `weak=4`, `moderate=2`, `strong=2` |
| Leakage status | `none=19`, `cross_setting_memory_used=5`, `same_pattern_memory_used=3` |
| Rules applied | `no_memory_keep_original=19`, `weak_keep_original=4`, `moderate_disagreement_keep_original_require_review=2`, `strong_agreement_keep_original=2` |

### Expert Alignment

| Subset | Expert Labels | Original Matches | Memory-Informed Matches | Original Agreement | Memory-Informed Agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mechanism validation, includes same-pattern memory | 3 | 2 | 2 | 0.6667 | 0.6667 |
| Generalization-safe, excludes same-pattern memory | 0 | 0 | 0 | Not evaluable | Not evaluable |

### Initial Interpretation

This run shows that M4B-1 can aggregate the comparison table, preserve the original AI output, apply deterministic rules, track leakage, and flag cases requiring further human review. It does not show an accuracy improvement.

In this run, M4B-1 clarified review needs rather than changing classifications:

- No memory-informed classification differed from the original Agent 4 classification.
- Two moderate-disagreement cases were flagged for human review after memory.
- The only expert-labeled rows came from same-pattern Human Judgment Memory, so they are mechanism-validation evidence only.

Generalization is not evaluable yet because there are zero held-out or cross-setting expert labels.

## EXP-002 Expert Labeling Package

EXP-002 creates the missing evidence collection artifact: a human/expert labeling package for evaluating M4B-1 without relying on same-pattern memory leakage.

Command:

```powershell
.\scripts\build-exp002-labeling-package.ps1
```

Generated local outputs, ignored by Git:

- `reports/generated/exp002/expert_labeling_sheet.csv`
- `reports/generated/exp002/expert_labeling_sheet.md`
- `reports/generated/exp002/recommended_patterns_to_label.md`
- `reports/generated/exp002/exp002_summary.json`

### Initial Package Summary

| Measure | Value |
| --- | ---: |
| Labeling rows | 27 |
| Settings covered | 4 |
| Existing expert labels found | 3 |
| Generalization-safe candidate rows | 24 |
| Requires human review after memory | 2 |
| Memory-informed differs from original | 0 |
| Recommended labeling targets | 27 |

Setting distribution: `cd_ch=4`, `cd_pw=7`, `ucd_ch=8`, `ucd_pw=8`.

Original classification distribution: `Occasional Variability=18`, `Substantial Variability=9`.

Leakage distribution: `none=19`, `cross_setting_memory_used=5`, `same_pattern_memory_used=3`.

### Labeling Fields

The sheet consolidates:

- `setting`
- `pattern_id`
- `pattern_description`
- `affected_cases`
- `related_guideline_id`
- `original_agent4_classification`
- `original_confidence`
- `requires_human_review`
- `flag_for_guidelines_update`
- `memory_advice_strength`
- `memory_informed_classification`
- `memory_informed_differs_from_original`
- `requires_human_review_after_memory`
- `evaluation_leakage_status`
- `existing_expert_label`
- blank `expert_label`
- blank `expert_rationale`
- blank `reviewer_id`
- blank `reviewer_confidence`

### Labeling Protocol

Allowed `expert_label` values:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Minimum target: 20 labeled patterns.

Preferred target: 30-50 labeled patterns. If the current package has fewer than 30 rows, label all available rows and add more audited runs later.

Sampling should prioritize memory-related disagreement or review cases, medium/low confidence cases, guideline-update candidates, patterns with no memory, and cross-context memory candidates. Same-pattern rows remain visible for mechanism validation but must be excluded from generalization-safe accuracy claims.

## Dashboard Figures To Produce

Use the local results dashboard to prepare thesis tables and figures for:

- review queue counts,
- trigger reason distribution,
- feedback resolution counts,
- reusable feedback counts,
- memory item counts,
- advice strength distribution,
- memory match reasons,
- M4B-1 comparison differences,
- evaluation leakage status,
- human-review-after-memory cases.

Generated dashboard/evaluation files remain ignored under `VEGO-AI/reports/results_dashboard/` and `reports/generated/` until publishability is approved.

## Leakage Policy

Separate mechanism validation from generalization evaluation.

Same-pattern memory may demonstrate that the mechanism works, but it cannot prove generalization. If a memory item derived from the same pattern is used to evaluate that pattern, label the result:

```text
same_pattern_memory_used
```

Use the following for stronger evidence:

- leave-one-pattern-out,
- cross-setting,
- cross-domain,
- cross-diagram,
- expert-only holdout.

## Allowed Claims After Initial EXP-001 Run

The project can claim:

- VEGO-AI now has a staged reusable human-judgment layer.
- Human review can be selectively triggered and persisted.
- Human feedback can be captured structurally.
- Reusable Human Judgment Memory can be stored with provenance.
- Memory can be retrieved as advisory evidence without changing AI output.
- M4B-1 can produce a non-destructive memory-informed comparison artifact.
- M4B-1 can identify memory-related cases that still require human review.
- The current local EXP-001 run supports mechanism/readiness evaluation, not accuracy improvement.

## Claims Not Yet Allowed

Do not claim yet:

- memory improves VEGO-AI accuracy,
- memory-informed classification is better,
- reusable judgment generalizes across domains/settings,
- M4B-1 should replace Agent 4 output.

Those require EXP-001/C4B evidence with leakage status and expert-label comparison.
The first EXP-001 run does not provide that evidence because it has zero generalization-safe expert-labeled rows.

## Evaluation Execution Checklist

1. Select audited inputs and confirm publishability status.
2. Define expert label fields and adjudication process.
3. Generate or collect review queue, feedback, memory, advice, and comparison artifacts.
4. Record exact code tag/commit, settings, commands, and output paths.
5. Label every M4B-1 comparison with `evaluation_leakage_status`.
6. Compare original Agent 4, memory-informed comparison, and expert labels.
7. Produce dashboard tables/figures.
8. Write limitations and validity threats before making claims.

## Current Verdict

Engineering state: strong.

Research prototype: strong.

MSc potential: strong.

Empirical evidence: incomplete.

Best next move: fill the EXP-002 expert-labeling sheet, then rerun EXP-001 or the next evaluation pass with leakage-aware expert-label partitions.

## Strict Evaluation Pass (original vs memory-informed) — 2026-06-16

Read-only strict re-evaluation. Deliverables (Git-ignored): `reports/generated/evaluation_comparison/`
(`original_vs_memory_informed.csv/.md`, `evaluation_summary.json`) and
`artifacts/EVALUATION_STRICT_REVIEW.md`. No baseline/Agent-4/eval_output change; no API/LLM.

### Decisive new finding — no independent benchmark exists

`VEGO-AI/analysis/agentD_variability_classes_<setting>.json` are **byte-identical** to the Agent 4 output in
`VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json` — every field (classification, confidence,
justification) matches for **all 27 patterns / 4 settings (0 differences)**. Therefore `analysis/` is a
**copy of Agent 4 output, not author-corrected ground truth**, and must **not** be used as a benchmark
(doing so grades Agent 4 against itself). The paper's "author-judged" classes reflect author *agreement*
with Agent 4, which is not an independent label set.

### Provenance integrity

Every `original_agent4_classification` in the four `memory_informed_comparison.json` files equals the
committed `eval_output` value (**27/27 rows, 0 mismatches**). The comparison faithfully preserves the baseline.

### Strict results

| Question | Answer |
| --- | --- |
| Independent benchmark? | No (`analysis/` duplicates Agent 4) |
| Expert labels | 3 (ucd_ch, from memory), all `same_pattern_memory_used` |
| Generalization-safe labeled rows | 0 |
| Memory-informed differs from original | 0 / 27 |
| Accuracy (all labeled, n=3) | original 0.667 = memory-informed 0.667 |
| Paired: original-wrong→memory-correct | 0 |
| Requires human review after memory | 2 |

### Verdict (strict, combined A+C+D)

No accuracy improvement is proven or currently measurable: no independent benchmark, memory-informed never
differs from the original, and zero generalization-safe expert labels. The demonstrated value is
**traceability, reusable human judgment, and safer human-review escalation**, under a verified
non-destructive boundary. Do not claim "better than baseline." Required before any accuracy/generalization
claim: held-out expert labels (≥20 safe; ideally 30–50; ≥2 raters for κ) via EXP-002, then a leakage-aware
original-vs-memory-informed-vs-expert comparison on safe rows only.

## Accuracy Improvement Path — 2026-06-16

Accuracy improvement work is now gated by `docs/research/accuracy-improvement-plan.md` and
`docs/research/expert-labeling-protocol.md`.

EXP-003 adds label preparation and evaluation tooling only:

- `.\scripts\build-exp003-error-analysis.ps1`
- `VEGO-AI/analysis/evaluate_accuracy_improvement.py`
- ignored outputs under `reports/generated/exp003/`

The EXP-003 gate is strict: if there are zero generalization-safe expert labels, the report must say
`Accuracy improvement cannot be evaluated yet.` If there are fewer than 20 safe expert labels, any accuracy
or macro-F1 result is pilot evidence only. No M4B-1 policy refinement, M4B-2, Agent 4 change, LLM/API call,
embedding path, or baseline overwrite is approved by this plan.

## Results And Accuracy Report - 2026-06-16

A full local report was generated at `artifacts/RESULTS_AND_ACCURACY_FULL_REPORT.md` from the existing
EXP-001, EXP-002, EXP-003, strict comparison, and dashboard summaries. The report is intentionally ignored by
Git under the artifact policy.

Strict conclusion: VEGO-AI has improved research traceability, explainability, human-review routing,
reusable judgment structure, dashboard visibility, and non-destructive comparison. It has not yet proven
classification accuracy improvement. Current evidence remains: 27 comparison rows, 3 same-pattern expert
labels, 0 generalization-safe expert-labeled rows, 0/27 memory-informed classification changes, and the
EXP-003 gate status `Accuracy improvement cannot be evaluated yet.`

## Synthetic Accuracy Simulation: Policy Sensitivity Check - 2026-06-16

A synthetic-only simulation report was generated at `artifacts/SYNTHETIC_ACCURACY_SIMULATION_REPORT.md`
with detailed outputs under ignored `reports/generated/synthetic_accuracy_simulation/`.

The synthetic simulation was used only to validate the evaluation pipeline and explore the sensitivity of
future memory-informed policies. It does not provide expert evidence. Under the current M4B-1 policy,
memory-informed classifications remain identical to the original Agent 4 classifications, so no accuracy
delta is possible. Counterfactual policies show that measurable improvement would require allowing memory
advice to modify the parallel classification under controlled conditions. Therefore, real expert labels are
still required before any accuracy-improvement claim can be made.

Do not report the synthetic `+16.67 pp` upper-bound scenario as an actual result. It is only a counterfactual
stress test showing that the evaluator can detect a delta if a future approved policy changes classifications.

## EXP-004 Policy Sensitivity Experiment - 2026-06-16

EXP-004 adds a reusable policy-sensitivity harness:

```powershell
.\scripts\build-policy-sensitivity-simulation.ps1
```

Generated local outputs, ignored by Git:

- `reports/generated/policy_sensitivity/policy_sensitivity_summary.json`
- `reports/generated/policy_sensitivity/policy_sensitivity_matrix.csv`
- `reports/generated/policy_sensitivity/policy_sensitivity_predictions.csv`
- `reports/generated/policy_sensitivity/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md`
- `artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md`

Initial synthetic run:

| Finding | Value |
| --- | ---: |
| Rows | 27 |
| Generalization-safe rows | 24 |
| Memory suggestions available | 8 |
| Safe memory disagreements | 4 |
| Current M4B-1 synthetic delta | `+0.00 pp` |
| Best upper-bound synthetic delta under `all_memory_truth` | `+16.67 pp` |
| Worst aggressive-policy synthetic loss under `original_truth` | `-16.67 pp` |

Interpretation: current M4B-1 still cannot improve accuracy because it changes no classifications. Candidate
policies are useful for risk screening only. Aggressive policies can look good when synthetic labels assume
memory advice is correct, but they also create false-change risk when original Agent 4 is correct. No policy
variant should be implemented before real EXP-003 expert labels show where Agent 4 is wrong and whether memory
advice would have corrected those errors.

## EXP-005 Real-Label Accuracy Gate - 2026-06-17

EXP-005 adds the supervisor/expert labeling gate:

```powershell
.\scripts\build-exp005-label-review.ps1
```

Generated local outputs, ignored by Git:

- `reports/generated/exp005_label_review/exp005_label_review_blind.csv`
- `reports/generated/exp005_label_review/exp005_label_review_full.csv`
- `reports/generated/exp005_label_review/label_these_first.md`
- `reports/generated/exp005_label_review/label_validation_summary.json`
- `reports/generated/exp005_label_review/real_vs_synthetic_policy_gate.md`
- `artifacts/EXP005_LABEL_REVIEW_PACKAGE.md`

The blind sheet hides original Agent 4 and memory-informed classifications for unbiased expert labeling. The
full sheet preserves audit context. The validation gate remains strict:

- `0` safe labels: `Accuracy improvement cannot be evaluated yet.`
- `1-19` safe labels: pilot evidence only.
- `20+` safe labels: quantitative evaluation can be reported, still with validity threats.

EXP-005 is now the required gate before any M4B-1.1 policy refinement or M4B-2 work. Synthetic EXP-004 results
can guide risk discussion, but they cannot justify an accuracy claim or classifier change without real labels.
