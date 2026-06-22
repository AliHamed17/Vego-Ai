# EXP-005 Real-Label Accuracy Evaluation And Policy Gate

Status: label-review package tooling added; real expert labels pending.

## Purpose

EXP-005 is the gate between synthetic policy sensitivity and any future accuracy-improvement claim. It prepares supervisor/expert labeling materials, validates filled labels, and compares candidate deterministic policies only against real, generalization-safe expert labels.

This experiment does not modify Agent 4, M4B-1 production behavior, M4B-2, baseline outputs, `VEGO-AI/eval_output`, LLM/API behavior, embeddings, or bundled artifacts.

## Command

```powershell
.\scripts\build-exp005-label-review.ps1
```

Optional filled-label rerun:

```powershell
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet reports\generated\exp005_label_review\exp005_label_review_blind.csv -RunDownstream
```

Use the optional form only after a human reviewer fills labels.

## Reviewer Reliability

Use `exp005_label_review_blind.csv` for the first independent review. After first-pass labels exist, use
`exp005_adjudication_sheet.csv` for reviewer-2 labels or supervisor adjudication.

Single-reviewer results are preliminary. Strong evidence requires reviewer-2 agreement or adjudicated labels
for disputed rows.

## Generated Outputs

All outputs are ignored by Git:

- `reports/generated/exp005_label_review/exp005_label_review_blind.csv`
- `reports/generated/exp005_label_review/exp005_label_review_full.csv`
- `reports/generated/exp005_label_review/exp005_adjudication_sheet.csv`
- `reports/generated/exp005_label_review/labeling_instructions.md`
- `reports/generated/exp005_label_review/label_these_first.md`
- `reports/generated/exp005_label_review/label_validation_summary.json`
- `reports/generated/exp005_label_review/real_label_policy_gate.csv`
- `reports/generated/exp005_label_review/real_vs_synthetic_policy_gate.md`
- `reports/generated/exp005_label_review/evidence_verdict.md`
- `reports/generated/exp005_label_review/reproducibility_manifest.json`
- `reports/generated/exp005_label_review/reproducibility_manifest.md`
- `artifacts/EXP005_LABEL_REVIEW_PACKAGE.md`

## Strict Gate

- `0` generalization-safe labels: accuracy improvement cannot be evaluated yet.
- `1-19` generalization-safe labels: pilot evidence only.
- `20+` generalization-safe labels: quantitative evaluation can be reported, still with validity threats.
- Preferred target: 30-50 safe labels across audited runs.

No M4B-1.1 or M4B-2 implementation is justified until EXP-005 labels show a real, leakage-safe reason for a deterministic policy change.

## Stable Evidence Tagging

Do not tag intermediate labeling attempts. Tag only a stable evidence state after the downstream rerun, health
checks, protected-path diff, and supervisor/reviewer interpretation pass.
