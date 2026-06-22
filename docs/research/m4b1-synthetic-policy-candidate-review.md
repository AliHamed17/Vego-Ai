# M4B-1 Synthetic Policy Candidate Review

Last updated: 2026-06-22 by Codex.

Status: design-only review from synthetic EXP-005 trial. No classifier behavior change is approved.

## Purpose

This note records what the synthetic EXP-005 trial suggests about possible future M4B-1.1 deterministic policies.

It is not real evidence. The labels were generated synthetically with reviewer ID `SYNTHETIC_NOT_HUMAN`. Use this note only to prioritize later review after real EXP-005 labels exist.

## Source

Generated, ignored local artifacts:

- `artifacts/SYNTHETIC_EXP005_TRIAL_REPORT.md`
- `reports/generated/exp005_synthetic_trial/`

The real EXP-005 gate remains separate:

- `reports/generated/exp005_label_review/exp005_label_review_blind.csv`

## Synthetic Trial Summary

| Measure | Synthetic value |
| --- | ---: |
| Rows | 27 |
| Generalization-safe rows | 24 |
| Same-pattern rows | 3 |
| Current M4B-1 classification changes | 0 / 27 |
| All-row original accuracy | 77.78% |
| All-row memory-informed accuracy | 77.78% |
| Generalization-safe original accuracy | 79.17% |
| Generalization-safe memory-informed accuracy | 79.17% |

Interpretation: current M4B-1 cannot improve classification accuracy because it does not change classifications. Its current value is traceability, advisory evidence, review escalation, and non-destructive comparison.

## Candidate Policies To Revisit After Real Labels

| Candidate | Synthetic safe delta | Synthetic changed rows | Risk | Design-only interpretation |
| --- | ---: | ---: | --- | --- |
| `current_v1` | 0.00 pp | 0 | Low | Keep as the current non-destructive baseline. |
| `escalation_only` | 0.00 pp | 0 | Low | Useful if the thesis emphasizes review routing, not accuracy correction. |
| `moderate_strong_safe_any_decision` | +4.35 pp | 1 | Medium | Lowest-change candidate worth inspecting after real labels. |
| `any_memory_safe_no_guideline_update` | +8.70 pp | 2 | Medium-high | Potentially useful but needs strong evidence that memory corrections are reliable. |
| `any_memory_safe_any_decision` | +17.39 pp | 4 | High | Too aggressive without real labels and adjudication. |

Synthetic gains are policy-risk signals only. They must not be presented as real accuracy improvement.

## Required Gate Before Any M4B-1.1 Work

Do not implement a policy refinement unless all of the following are true:

- EXP-005 has at least 20 generalization-safe real expert labels.
- The real-label policy gate shows positive improvement over original Agent 4.
- Changed-and-wrong cases are zero or explicitly accepted by the supervisor.
- Same-pattern rows are excluded from generalization claims.
- A second reviewer or supervisor adjudication is available for disputed rows.
- Protected paths remain unchanged until a reviewed feature branch is approved.

Protected paths:

```powershell
git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval
```

## Current Decision

No M4B-1.1 implementation. No M4B-2. No Agent 4 changes. No LLM/API calls. No embeddings. No baseline or `eval_output` overwrite.

The next real research action remains real EXP-005 label collection.
