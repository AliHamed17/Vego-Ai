# Accuracy Improvement Plan

Last updated: 2026-07-24 by Codex.

Status: evaluation-first path defined; EXP-005 remains at 0/24 safe labels;
EXP-019–EXP-027 are preregistered specifications; no accuracy-improvement claim
is allowed yet.

Canonical interface:
`docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json`.

## B0–B5 Evidence Ladder

| ID | Baseline | Current state | Gate |
| --- | --- | --- | --- |
| B0 | Frozen Agent 4 output | Implemented | Baseline hashes remain unchanged |
| B1 | Current reusable-human-judgment mechanism | Implemented; 0/27 classification changes | Mechanism and safety evidence only |
| B2 | Independent expert-labeled baseline | Pending expert input; 0/24 | EXP-019 calibration and EXP-020 adjudicated labels |
| B3 | Development-only deterministic candidate | Proposal — not approved | At least 3 correctable errors across 2 settings plus explicit approval |
| B4 | One-time 8-row sealed holdout | Blocked | Freeze B3 before opening |
| B5 | New external education batch | Proposal — not approved | Minimum 30, target 48, and every preregistered formal-claim criterion |

The ladder represents increasing evidence independence, not guaranteed accuracy
improvement.

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

- Paired net correction:
  `changed-and-correct - changed-and-wrong`.

Secondary metrics:

- accuracy and macro-F1 against independent expert labels
- per-class precision and recall
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

Formal improvement claim:

- external generalization-safe adjudicated N ≥ 30;
- candidate policy frozen before external data inspection;
- 10,000-replicate paired-bootstrap 95% net-correction interval excludes zero
  with seed `20260721`;
- exact McNemar `p < 0.05`;
- macro-F1 does not decline;
- no predefined class or setting subgroup shows material harm;
- baseline and protected-path hashes remain unchanged.

## Evaluation Path

1. Prepare EXP-003 full and blind labeling sheets from EXP-002.
2. Collect independent labels using `docs/research/expert-labeling-protocol.md`.
3. Run `.\scripts\build-exp003-error-analysis.ps1`.
4. Diagnose where original Agent 4 is wrong.
5. Compare original Agent 4 and M4B-1 against expert labels.
6. Run `.\scripts\build-policy-sensitivity-simulation.ps1` to compare candidate policy variants without changing the real pipeline.
7. Run `.\scripts\build-exp005-label-review.ps1` to prepare the supervisor/expert label package and validate filled labels.
8. If EXP-005 has enough safe labels and the real-label policy gate justifies it, update `docs/research/m4b1-policy-refinement-plan.md`.
9. Only after approval, implement a deterministic M4B-1.1 policy on a feature branch.

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

## EXP-004 Policy Sensitivity

EXP-004 provides a controlled policy-sensitivity harness:

- Script: `.\scripts\build-policy-sensitivity-simulation.ps1`
- Report: ignored `artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md`
- Generated matrix: ignored `reports/generated/policy_sensitivity/policy_sensitivity_matrix.csv`

The harness evaluates candidate M4B-1.1-style rules against synthetic truth scenarios. It does not change
current M4B-1 behavior and does not provide expert evidence.

Initial synthetic finding:

- Current M4B-1 remains at `+0.00 pp` because it changes no classifications.
- Aggressive policies can create synthetic gains when memory advice is assumed correct.
- The same aggressive policies can create synthetic losses when original Agent 4 is assumed correct.

Therefore, EXP-004 is useful for policy-risk screening, but real EXP-003 labels are still required before
any policy refinement or accuracy-improvement claim.

## EXP-005 Real-Label Gate

EXP-005 turns the next research step into a concrete expert-label workflow:

- Script: `.\scripts\build-exp005-label-review.ps1`
- Report: ignored `artifacts/EXP005_LABEL_REVIEW_PACKAGE.md`
- Generated package: ignored `reports/generated/exp005_label_review/`

The default run creates a blind label sheet, full audit sheet, label instructions, a prioritized "label these
first" supervisor summary, adjudication sheet, validation summary, evidence verdict, reproducibility manifest,
and a real-label policy gate. If a filled label sheet is later
provided with `-FilledLabelsSheet ... -RunDownstream`, the wrapper reruns EXP-003 and EXP-004-style outputs in
the EXP-005 generated folder.

Current expected initial status is still `Accuracy improvement cannot be evaluated yet` because real
generalization-safe labels have not been filled. EXP-005 is the required gate before M4B-1.1 or M4B-2 can be
considered.

## EXP-005 Synthetic Trial

A synthetic-only EXP-005 trial was run to exercise the downstream evidence pipeline without editing the real
blind label sheet:

- Synthetic report: ignored `artifacts/SYNTHETIC_EXP005_TRIAL_REPORT.md`
- Synthetic outputs: ignored `reports/generated/exp005_synthetic_trial/`
- Synthetic reviewer ID: `SYNTHETIC_NOT_HUMAN`
- Design-only interpretation: `docs/research/m4b1-synthetic-policy-candidate-review.md`

Synthetic result:

| Measure | Value |
| --- | ---: |
| Synthetic labels | 27 |
| Synthetic generalization-safe labels | 24 |
| Current M4B-1 classification changes | 0 / 27 |
| Generalization-safe original accuracy | 79.17% |
| Generalization-safe memory-informed accuracy | 79.17% |

The synthetic trial confirms that current M4B-1 still has no accuracy delta because it changes no classifications.
Synthetic policy variants can suggest which deterministic rules deserve later review, but they are not evidence
of real accuracy improvement.

## Strategic Hardening Review

The strategic review in `docs/research/strategic-review-and-hardening-plan.md` keeps the accuracy-improvement path constrained to evidence first:

- Current implementation baseline is `main` at `0976c05`.
- Current EXP-005 status is 27 rows, 24 generalization-safe candidates, 0 supplied labels, 0 complete valid labels, and 0 generalization-safe valid labels.
- Current M4B-1 has 0 / 27 memory-informed classifications differing from original Agent 4, so no accuracy delta is possible under the implemented policy.
- EXP-004 synthetic policy results remain risk screening only.
- Same-pattern labels remain mechanism validation only.
- Add a second reviewer or supervisor adjudication before treating EXP-005 results as strong evidence.

No policy refinement is allowed until real EXP-005/EXP-020 labels identify at
least three potentially correctable development errors across at least two
settings, EXP-022 confirms relevant and safe advice, and the supervisors approve
one specific `PolicyCandidateRecord-v1`.

## EXP-019–EXP-027

The evidence path is now split into:

1. EXP-019 reviewer calibration using three excluded same-pattern rows.
2. EXP-020 two-reviewer labeling and adjudication of the 24 safe rows.
3. EXP-021 baseline error analysis on 16 development rows.
4. EXP-022 routing and retrieval validity.
5. EXP-023 one deterministic policy candidate, only if the entry gate passes.
6. EXP-024 one-time evaluation on eight sealed rows.
7. EXP-025 external education-domain replication, minimum 30 and target 48.
8. EXP-026 controlled human-effort study.
9. EXP-027 post-primary ablation and robustness.

Detailed rules:
`docs/research/thesis-evidence/PREREGISTRATION_EXP019_027.md`.

## Evidence Rerun Manifest

Every EXP-005 rerun generates ignored manifest/verdict artifacts under `reports/generated/exp005_label_review/`:

- `evidence_verdict.md`
- `reproducibility_manifest.json`
- `reproducibility_manifest.md`

Use these files to record commit hash, label counts, protected-path diff status, generated outputs, and required validation commands. Stable evidence tags are allowed only after the manifest, health checks, and supervisor/reviewer interpretation are reviewed.

## HITL Resource Pack

The curated resource pack in `literature/hitl-resource-pack/` supports the accuracy-improvement path by documenting Human-AI collaboration literature, governance sources, and candidate labeling/data-quality tools.

Use the pack for:

- EXP-005 reviewer workflow design.
- Supervisor discussion of human oversight, adjudication, and label quality.
- Future consideration of Label Studio, Argilla, modAL, or cleanlab after real labels exist.

Do not treat resource-pack tools or literature as evidence that VEGO-AI accuracy improved. Accuracy remains blocked until EXP-005 has enough real, generalization-safe expert labels.

## Non-Negotiable Boundaries

- Do not modify Agent 4.
- Do not call OpenAI/API.
- Do not overwrite `VEGO-AI/eval_output`.
- Do not use Agent 4 output as expert truth.
- Do not use same-pattern memory as generalization evidence.
- Do not implement M4B-2 or embeddings before deterministic evaluation is complete.
- Do not implement M4B-1.1 until EXP-005 has at least 20 generalization-safe labels and the supervisor/reviewer approves a specific deterministic policy change.
