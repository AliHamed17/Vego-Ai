# Accuracy Improvement Plan

Last updated: 2026-06-16 by Codex.

Status: evaluation-first path defined; no accuracy-improvement claim is allowed yet.

## Baseline

The accuracy baseline is original VEGO-AI Agent 4 variability classification from:

- `VEGO-AI/eval_output/cd_ch/agentD_variability_classes__cd_ch.json`
- `VEGO-AI/eval_output/cd_pw/agentD_variability_classes.json`
- `VEGO-AI/eval_output/ucd_ch/agentD_variability_classes.json`
- `VEGO-AI/eval_output/ucd_pw/agentD_variability_classes_ucd_pw.json`

Reference baseline identifiers:

- Git tag / branch: `official-vego-ai-baseline`, `baseline/official-vego-ai`
- Baseline commit: `2eeccb1`
- Current rule: `eval_output` is read-only and must not be overwritten.

Current baseline summary from the strict evaluation:

| Metric | Value |
| --- | ---: |
| Settings | 4 |
| Student model result files | 179 |
| Agent 4 variability patterns | 27 |
| Occasional Variability | 18 |
| Substantial Variability | 9 |
| Generalization-safe expert-labeled rows | 0 |
| M4B-1 rows differing from original | 0 / 27 |

`VEGO-AI/analysis/agentD_variability_classes_*.json` must not be treated as independent ground truth because the strict evaluation found it duplicates Agent 4 output.

## Accuracy Target

Primary metric:

- Accuracy and macro-F1 of variability classification against independent expert labels.

Secondary metrics:

- changed-and-correct
- changed-and-wrong
- requires-human-review-after-memory
- memory advice relevance
- leakage-safe performance
- traceability/provenance completeness

Reporting gate:

- `0` generalization-safe expert labels: report `Accuracy improvement cannot be evaluated yet.`
- `1-19` generalization-safe expert labels: report pilot evidence only.
- `20+` generalization-safe expert labels: report quantitative results, still with validity threats.
- Preferred target: 30-50 labels across audited runs.

## Evaluation Path

1. Prepare EXP-003 full and blind labeling sheets from EXP-002.
2. Collect independent labels using `docs/research/expert-labeling-protocol.md`.
3. Run `.\scripts\build-exp003-error-analysis.ps1`.
4. Diagnose where original Agent 4 is wrong.
5. Compare original Agent 4 and M4B-1 against expert labels.
6. If data justifies it, write `docs/research/m4b1-policy-refinement-plan.md`.
7. Only after approval, implement a deterministic M4B-1.1 policy on a feature branch.

## Candidate Improvement Strategies

Strategy A: better escalation only.

- Do not change classification.
- Measure whether `requires_human_review_after_memory` identifies baseline errors.

Strategy B: deterministic conservative correction.

- Produce parallel memory-informed classification only.
- Allow a proposed change only when strong memory advice is explicit, conflict-free, leakage-safe, and supported by expert-labeled evidence.

Strategy C: threshold tuning.

- Tune advice strength, confidence gates, leakage restrictions, conflict handling, and escalation thresholds.
- Use leave-one-pattern-out if labels are small.

Strategy D: expert-rule refinement.

- Use expert labels to improve deterministic rules, not LLM behavior.
- Keep ambiguous, conflict, and guideline-update cases as review/escalation unless evidence supports a classification change.

Strategy E: future LLM mode.

- M4B-2 remains blocked until deterministic evaluation is complete.

## Non-Negotiable Boundaries

- Do not modify Agent 4.
- Do not call OpenAI/API.
- Do not overwrite `VEGO-AI/eval_output`.
- Do not use Agent 4 output as expert truth.
- Do not use same-pattern memory as generalization evidence.
- Do not implement M4B-2 or embeddings before deterministic evaluation is complete.
