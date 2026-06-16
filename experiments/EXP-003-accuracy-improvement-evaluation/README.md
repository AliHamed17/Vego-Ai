# EXP-003: Accuracy Improvement Evaluation

Status: tooling added; independent expert labels pending.

## Purpose

EXP-003 prepares blind/full expert-labeling sheets and evaluates original VEGO-AI Agent 4 and M4B-1 memory-informed comparison against independent labels.

The experiment does not implement M4B-1.1, M4B-2, Agent 4 changes, API calls, embeddings, or baseline-output rewrites.

## Inputs

- `reports/generated/exp002/expert_labeling_sheet.csv`
- `VEGO-AI/eval_output/<setting>/agentD_variability_classes*.json`
- `VEGO-AI/runs/20260614-122150/human/<setting>/memory_advice.json`
- `VEGO-AI/runs/20260614-122150/human/<setting>/memory_informed_comparison.json`

## Command

```powershell
.\scripts\build-exp003-error-analysis.ps1
```

## Generated Outputs

Generated outputs are ignored by Git:

- `reports/generated/exp003/expert_labeling_sheet_full.csv`
- `reports/generated/exp003/expert_labeling_sheet_blind.csv`
- `reports/generated/exp003/labeling_instructions.md`
- `reports/generated/exp003/error_analysis.csv`
- `reports/generated/exp003/error_analysis.md`
- `reports/generated/exp003/error_summary.json`
- `reports/generated/exp003/original_vs_expert.csv`
- `reports/generated/exp003/memory_informed_vs_expert.csv`
- `reports/generated/exp003/paired_comparison.csv`
- `reports/generated/exp003/accuracy_summary.json`
- `reports/generated/exp003/figures/`

## Strict Gate

If there are zero generalization-safe expert labels, accuracy improvement cannot be evaluated yet.

If there are fewer than 20 generalization-safe expert labels, report only pilot evidence.
