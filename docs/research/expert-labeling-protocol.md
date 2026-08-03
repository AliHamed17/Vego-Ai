# Expert Labeling Protocol

Last updated: 2026-06-29 by Codex.

Purpose: collect independent expert labels for leakage-aware evaluation of VEGO-AI variability classification.

Supervisor approval pack: `docs/research/supervisor-label-approval-pack.md`.

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

## Fast Interactive Labeling (EXP-005)

Instead of opening `exp005_label_review_blind.csv` in Excel, an interactive terminal tool
presents each pattern one at a time (description, affected cases, related guideline,
priority) and prompts for the required fields with keyboard shortcuts:

```powershell
.\scripts\label-exp005-interactive.ps1
```

Or directly: `python scripts/exp005_interactive_labeler.py [--reviewer-id expert_01]`.

- Writes to `reports/generated/exp005_label_review/exp005_label_review_filled.csv` by
  default (does not overwrite the blind template).
- Resumable: quit any time with `q`; rerunning picks up exactly where you left off without
  losing already-entered labels. `s` skips a row for now.
- Produces the same schema `-FilledLabelsSheet` expects, so once done, run:
  `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <output> -RunDownstream`.
- This tool does not supply, suggest, or infer any label itself; it only speeds up entry of
  a real reviewer's own judgment. The bias/leakage rules below still apply in full.

## Reviewer Workflow

Use this workflow unless the supervisor explicitly approves a different reviewer plan:

1. Supervisor reviews and approves `docs/research/supervisor-label-approval-pack.md`.
2. Reviewer 1 fills the first blind sheet only.
3. Reviewer 2 independently fills the second blind sheet, or the supervisor uses the adjudication sheet after reviewer 1 labels exist.
4. Disagreements are adjudicated into the final gold-label file.
5. The filled sheet is rerun through EXP-005; generated verdicts, accuracy summaries, and Chapter 7 are updated only after that rerun.

First-pass reviewer files:

- `reports/generated/exp003/annotation_package/blind_sheet_reviewer1.csv`
- `reports/generated/exp003/annotation_package/blind_sheet_reviewer2.csv`
- `reports/generated/exp005_label_review/exp005_label_review_blind.csv`

Adjudication and audit files:

- `reports/generated/exp005_label_review/exp005_adjudication_sheet.csv`
- `reports/generated/exp003/annotation_package/annotation_sheet_audit.csv`
- `reports/generated/exp003/annotation_package/gold_labels.csv`

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

## Reviewer-2 And Adjudication Protocol

Use the first-pass blind sheet for independent expert labels. After first-pass labels exist, use the EXP-005
adjudication sheet for reliability and supervisor decisions.

Reviewer-2 fields:

- `reviewer_2_label`
- `reviewer_2_rationale`
- `reviewer_2_id`
- `reviewer_2_date`
- `reviewer_2_confidence`

Adjudication fields:

- `agreement_status`
- `adjudicated_label`
- `adjudicated_rationale`
- `adjudicator_id`
- `adjudication_date`
- `adjudication_notes`

Interpretation:

- Single-reviewer results are preliminary.
- Reviewer-2 agreement strengthens label reliability.
- Disagreements should be adjudicated before strong accuracy/generalization claims.
- Inter-rater agreement can be reported only when enough reviewer-2 labels exist.

## Files

Generated EXP-003 files are ignored by Git:

- `reports/generated/exp003/expert_labeling_sheet_full.csv`
- `reports/generated/exp003/expert_labeling_sheet_blind.csv`
- `reports/generated/exp003/labeling_instructions.md`

Run:

```powershell
.\scripts\build-exp003-error-analysis.ps1
```

Generated EXP-005 files are ignored by Git:

- `reports/generated/exp005_label_review/exp005_label_review_blind.csv`
- `reports/generated/exp005_label_review/exp005_adjudication_sheet.csv`
- `reports/generated/exp005_label_review/evidence_verdict.md`
- `reports/generated/exp005_label_review/reproducibility_manifest.json`

Run:

```powershell
.\scripts\build-exp005-label-review.ps1
```

After a human fills labels, rerun with:

```powershell
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream
```

Close the filled CSV before rerunning the command, especially if it was edited in Excel.
