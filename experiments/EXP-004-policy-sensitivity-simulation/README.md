# EXP-004 Policy Sensitivity Simulation

Status: Tooling ready; synthetic-only initial run.

## Purpose

EXP-004 explores whether candidate M4B-1.1 style policies could produce measurable accuracy deltas under
controlled synthetic labels. It is a policy-risk and evaluation-pipeline experiment only.

It does not modify Agent 4, M4B-1, M4B-2, baseline outputs, `VEGO-AI/eval_output/`, LLM/API behavior, or
embeddings.

## Command

```powershell
.\scripts\build-policy-sensitivity-simulation.ps1
```

## Inputs

- `reports/generated/exp003/expert_labeling_sheet_full.csv`

## Outputs

Generated and ignored:

- `reports/generated/policy_sensitivity/policy_sensitivity_summary.json`
- `reports/generated/policy_sensitivity/policy_sensitivity_matrix.csv`
- `reports/generated/policy_sensitivity/policy_sensitivity_predictions.csv`
- `reports/generated/policy_sensitivity/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md`
- `artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md`

## Interpretation Rule

Synthetic results are not expert evidence. A positive synthetic delta only means the evaluator can detect a
policy effect if future approved rules change classifications. It does not prove VEGO-AI accuracy improved.

Policy implementation remains blocked until EXP-003 has at least 20 generalization-safe expert labels,
error analysis shows where Agent 4 is wrong, and the supervisor/reviewer approves a specific deterministic
policy refinement.
