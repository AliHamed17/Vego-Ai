# EXP-002: Expert Label Expansion And Holdout Evaluation

## Record

- Experiment ID: EXP-002
- Title: Expert Label Expansion and Holdout Evaluation
- Owner: Ali Hamed
- Date started: 2026-06-14
- Date completed: Labeling package generated 2026-06-14; human labeling pending
- Status: Labeling package ready; expert labels pending
- Related research question: RQ4

## Purpose

EXP-002 creates a human/expert labeling package so M4B-1 can be evaluated without relying on same-pattern Human Judgment Memory leakage.

The experiment does not implement new VEGO-AI features. It prepares evidence collection for the empirical question:

> Does reusable Human Judgment Memory improve, match, or clarify VEGO-AI variability assessment when evaluated against independent expert labels?

## Boundary

This experiment must not:

- implement M4B-2,
- modify Agent 4,
- call an LLM or API,
- add embeddings,
- rewrite guidelines automatically,
- edit feedback from the GUI,
- overwrite baseline outputs.

## Inputs

- Local controlled run root: `VEGO-AI/runs/20260614-122150/human/`
- Agent D variability classifications from `VEGO-AI/analysis/agentD_variability_classes_*.json` when available.
- Agent D deviation patterns from `VEGO-AI/eval_output/*/agentD_deviation_patterns*.json` when available.
- M4A advice files: `memory_advice.json`.
- M4B-1 comparison files: `memory_informed_comparison.json`.
- Existing Human Judgment Memory labels, when present.

These source artifacts remain controlled/ignored unless separately audited and approved for publication.

## Method

Run:

```powershell
.\scripts\build-exp002-labeling-package.ps1
```

The generator builds one row per M4B-1 comparison pattern and joins available description, affected cases, guideline, original Agent 4 classification, memory advice, memory-informed comparison, leakage status, and any existing expert label.

## Generated Outputs

Generated outputs are ignored by Git:

- `reports/generated/exp002/expert_labeling_sheet.csv`
- `reports/generated/exp002/expert_labeling_sheet.md`
- `reports/generated/exp002/recommended_patterns_to_label.md`
- `reports/generated/exp002/exp002_summary.json`

## Current Package Summary

The first generated package contains:

| Measure | Value |
| --- | ---: |
| Labeling rows | 27 |
| Settings covered | 4 |
| Existing expert labels found | 3 |
| Generalization-safe candidate rows | 24 |
| Requires human review after memory | 2 |
| Memory-informed differs from original | 0 |
| Recommended labeling targets | 27 |

Distribution by setting:

| Setting | Rows |
| --- | ---: |
| `cd_ch` | 4 |
| `cd_pw` | 7 |
| `ucd_ch` | 8 |
| `ucd_pw` | 8 |

## Labeling Protocol

For each selected pattern, a reviewer should fill:

- `expert_label`
- `expert_rationale`
- `reviewer_id`
- `reviewer_confidence`

Allowed `expert_label` values:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Minimum target: 20 labeled patterns.

Preferred target: 30-50 labeled patterns. If the current local package has fewer than 30 rows, label all available rows and add more audited runs later.

## Sampling Priorities

Prioritize:

- memory-informed disagreement cases,
- `requires_human_review_after_memory` cases,
- medium/low confidence cases,
- guideline-update candidates,
- patterns with no memory,
- cross-setting or cross-domain memory candidates,
- a balanced mix of substantial, occasional, and undetermined/ambiguous patterns.

Same-pattern memory rows should remain visible, but they support mechanism validation only and must be separated from generalization-safe evaluation.

## Evaluation Use

After labels are filled, rerun EXP-001 or create the next evaluation pass using the completed expert-label sheet.

Report separately:

- mechanism validation, which may include `same_pattern_memory_used`;
- generalization-safe evaluation, excluding `same_pattern_memory_used`.

No accuracy-improvement claim is allowed until generalization-safe expert labels exist.
