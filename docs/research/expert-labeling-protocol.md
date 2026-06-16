# Expert Labeling Protocol

Last updated: 2026-06-16 by Codex.

Purpose: collect independent expert labels for leakage-aware evaluation of VEGO-AI variability classification.

## Label Values

Use exactly one `expert_label` value per pattern:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

## Required Fields

Fill these fields for every reviewed pattern:

| Field | Meaning |
| --- | --- |
| `expert_label` | Expert classification using the allowed values. |
| `expert_rationale` | Short reason for the label. |
| `reviewer_id` | Stable anonymous reviewer identifier, for example `expert_01`. |
| `review_date` | Date of review in `YYYY-MM-DD` format. |
| `confidence` | Reviewer confidence, preferably `High`, `Medium`, or `Low`. |
| `notes` | Optional caveats, ambiguity, or extra context. |

## Labeling Context

Experts should judge each pattern using:

- pattern description,
- affected cases,
- related guideline,
- domain context,
- evidence text where available.

The full sheet may show original Agent 4 and memory-informed classifications for audit context. The blind sheet hides these fields and should be preferred when independent labels are needed.

## Bias And Leakage Rules

- Do not copy Agent 4 output as ground truth.
- Do not use `VEGO-AI/analysis/agentD_variability_classes_*.json` as expert labels.
- Do not use same-pattern Human Judgment Memory as generalization evidence.
- If the row is ambiguous, use `Undetermined / Needs Review` and explain why.
- Same-pattern labels may support mechanism validation only.
- Cross-setting and held-out labels are required for generalization claims.

## Minimum Evidence Threshold

- Fewer than 20 generalization-safe expert labels: report pilot evidence only.
- Zero generalization-safe labels: report `Accuracy improvement cannot be evaluated yet.`
- Preferred target: 30-50 labels, with more than one reviewer if possible.

## Files

Generated EXP-003 files are ignored by Git:

- `reports/generated/exp003/expert_labeling_sheet_full.csv`
- `reports/generated/exp003/expert_labeling_sheet_blind.csv`
- `reports/generated/exp003/labeling_instructions.md`

Run:

```powershell
.\scripts\build-exp003-error-analysis.ps1
```
