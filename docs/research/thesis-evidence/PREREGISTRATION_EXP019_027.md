# Preregistration — EXP-019 through EXP-027

Version: 1.0
Date frozen: 2026-07-24
Status: **Protocol draft awaiting supervisor approval. No outcome data inspected.**

## 1. Scope

This preregistration governs the empirical accuracy-evidence extension of the
VEGO-AI MSc thesis. It does not authorize a runtime change. All candidate
classifications remain parallel and experimental, and the original Agent 4
output remains read-only.

## 2. Units and partitions

- Evaluation unit: one anonymized variability-pattern row.
- Current safe candidate set: 24 rows.
- Calibration set: 3 same-pattern rows excluded from all generalization metrics.
- Development partition: 16 rows.
- Sealed holdout partition: 8 rows.
- External replication: minimum 30, target 48, newly collected education-domain rows.
- Partition membership is hidden from reviewers.
- Holdout labels remain sealed until a candidate policy is frozen.

The current private 16/8 mapping is preserved. If it must be regenerated before
label collection, the new mapping and seed are recorded once and frozen before
any label is inspected.

## 3. Review and adjudication

1. Two independent reviewers label each evaluation row.
2. Reviewers see neutral context, not Agent 4 output, memory advice, candidate
   output, leakage class, or partition assignment.
3. Required fields follow `GoldLabelRecord-v2`.
4. Cohen's kappa is computed from raw reviewer labels before adjudication.
5. Disagreements are adjudicated by a distinct adjudication role.
6. Raw reviewer files remain immutable; adjudicated records are stored separately.
7. Synthetic or AI-generated labels are rejected.

## 4. Label vocabulary

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Every label requires rationale, confidence, reviewer ID, and review date.

## 5. Research questions and hypotheses

| Question/hypothesis | Operational test |
| --- | --- |
| E-RQ1 / H1 | Baseline error taxonomy and review routing on the 16-row development partition |
| E-RQ2 / H2 | Blind retrieval relevance, scope, conflict, leakage, and missed-error audit |
| E-RQ3 / H3 | Paired net correction on frozen holdout and external data |
| H4 | Separate controlled human-effort study |

H3 and H4 are unproven. The study may produce null or negative findings.

## 6. Primary estimand

For each paired expert-labeled row:

- `changed-and-correct`: baseline wrong, candidate correct.
- `changed-and-wrong`: baseline correct, candidate wrong.
- `both-correct`: baseline and candidate correct.
- `both-wrong`: baseline and candidate wrong.

Primary estimand:

`net correction = changed-and-correct - changed-and-wrong`

The direction and magnitude are reported with a paired-bootstrap 95% confidence
interval. A candidate that changes zero rows has net correction zero by
construction.

## 7. Secondary measures

- Accuracy and macro-F1 for baseline and candidate.
- Per-class precision and recall.
- Confusion matrices.
- Review routing precision and recall.
- Retrieval hit rate, relevance, scope correctness, and conflict rate.
- Same-pattern, same-setting, cross-setting, and unknown leakage counts.
- Cohen's kappa, disagreement count, and adjudication count.
- EXP-026 review time, repeated-question rate, and reviewer confidence.

## 8. Statistical rules

- Proportion intervals: Wilson 95%.
- Paired-bootstrap replicates: 10,000.
- Paired-bootstrap seed: `20260721`.
- External paired significance test: exact McNemar.
- No multiple post-hoc policy variants are tested on the sealed holdout.
- No external-set tuning is permitted.
- Missing, blank, unknown-provenance, synthetic, or same-pattern rows are
  excluded from primary generalization metrics.

## 9. Gate interpretation

| Generalization-safe adjudicated N | Interpretation |
| ---: | --- |
| 0 | Not yet computable |
| 1-19 | Exploratory pilot only |
| 20-24 | Quantitative MSc pilot with small-sample limitations |
| Holdout 8 | One-time pilot, never a formal improvement claim |
| External 30-47 | Formal gate eligible if all criteria pass |
| External 48+ | Preferred external target; criteria still all required |

## 10. Policy-development gate

EXP-023 is permitted only if:

1. EXP-021 identifies at least three potentially correctable development errors.
2. Those errors span at least two settings.
3. EXP-022 shows the required advice is relevant, scope-correct, conflict-free,
   and generalization-safe.
4. Iris and Arnon approve one explicit `PolicyCandidateRecord-v1`.

If the gate fails, policy work stops and the null result is reported.

## 11. Formal improvement gate

A formal improvement statement is permitted only after EXP-025 if all are true:

- External generalization-safe adjudicated N is at least 30.
- The policy was frozen before external data inspection.
- Net-correction bootstrap interval excludes zero.
- Exact McNemar `p < 0.05`.
- Macro-F1 does not decline.
- No predefined class or setting subgroup shows material harm.
- Baseline and protected-path hashes are unchanged.
- All exclusions and missing data are reported.

Failure of any criterion means the formal improvement claim is not made.

## 12. Stopping rules

- Stop before analysis if safe N is zero.
- Stop policy development if EXP-021 does not meet the error-count and
  setting-coverage gate.
- Stop the holdout run if the policy or split hash differs from its frozen record.
- Stop external analysis if the policy changed after holdout inspection.
- Stop publication of quantitative results if reviewer provenance, leakage class,
  or source hashes are incomplete.
- Preserve and report negative, null, and harmful results.

## 13. Deviations

Any deviation is dated, justified, approved, and recorded before the affected
outcome is inspected. Deviations are never silently folded into the protocol.
