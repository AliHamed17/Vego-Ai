# Independent Evidence Execution Program

Status: **Evaluation-ready; pending two independent human reviewers.**

This program turns the six requested value questions into measurements without
copying VEGO-AI output into the ground truth.

## Current fact

- Candidate evaluation rows: **24**.
- Independent reviewer returns: **0 of 2**.
- Adjudicated safe labels: **0 of 24**.
- Original Agent 4 and current M4B-1 classification differences: **0 of 27**.
- Accuracy, macro-F1, routing precision/recall, and generalization: **not yet
  computable**.

Package readiness is not performance evidence. No software command in this
repository creates expert labels.

## What will be measured

| Question | Independent reference | Primary measures | Positive evidence gate |
| --- | --- | --- | --- |
| Better classification | Two blind reviews plus human adjudication | Accuracy, macro-F1, balanced accuracy, class precision/recall | At least 20 safe adjudicated labels |
| Better paired result | Same gold row evaluated by B0 and a frozen comparator | Candidate-only correct, baseline-only correct, net correction, exact McNemar | Frozen policy and unseen data |
| Unseen-pattern generalization | Sealed eight-row pilot, followed by external education replication | Macro-F1, net correction, subgroup results | No policy tuning after opening; external replication for a formal claim |
| Lower human effort | Counterbalanced EXP-026 task study | Time, review count, repeated questions, correctness, confidence | Same participants/tasks or equivalent randomized groups |
| Better than the paper | Reconstructed historical comparator only when inputs and labels are equivalent | Same metric definition, cohort, labels, and baseline | Otherwise `Not directly comparable` |
| Best H-layer topology | Contract-equivalent EXP-034 runs | Parity, latency, memory, handoffs, failures, authority preservation | Pareto result; M-02 human decision still required |
| Best routing rule | Independent routing-need and priority judgments | Precision, recall, F1, high-priority recall, workload | Adjudicated routing targets and frozen rule |

## Execution order

1. Iris and Arnon record reviewer-role, consent/ethics, anonymity, transfer,
   retention, and adjudicator decisions.
2. Build the local blinded package:

   ```powershell
   python scripts\build_independent_evidence_package.py --refresh
   python scripts\build_independent_evidence_package.py --check
   ```

3. Send Reviewer 1 and Reviewer 2 only their own calibration page and the
   reviewer instructions. Never send `private/`.
4. Preserve both calibration returns unchanged. Discuss vocabulary problems and
   freeze the instruction version before evaluation.
5. Send each reviewer only their own 24-item evaluation page.
6. Preserve both raw JSON returns unchanged and validate them:

   ```powershell
   python scripts\validate_independent_evidence_returns.py `
     --reviewer-1 <reviewer-1-return.json> `
     --reviewer-2 <reviewer-2-return.json>
   ```

7. Record observed agreement and Cohen's kappa before adjudication.
8. A human adjudicator completes every blank adjudication field. The raw
   reviewer fields must not be edited.
9. Freeze the gold set:

   ```powershell
   python scripts\freeze_independent_gold_labels.py `
     --reviewer-1 <reviewer-1-return.json> `
     --reviewer-2 <reviewer-2-return.json> `
     --adjudication <completed-adjudication-workbook.csv>
   ```

10. Run development-only measurement:

    ```powershell
    python scripts\evaluate_independent_ground_truth.py `
      --gold reports/generated/independent_evidence_v1/gold/gold_labels.csv `
      --stage development
    ```

11. Use the 16 development rows for error characterization and one
    preregistered deterministic routing/classification proposal only if the
    entry gate is satisfied.
12. Open the eight-row holdout once, only after the candidate is accepted and
    frozen. The holdout is a pilot, not proof.
13. Test the same frozen approach on an external education batch before a
    generalization claim.

## Human authority and privacy

- Reviewer IDs must be pseudonyms, not names or email addresses.
- Reviewer returns, private mappings, adjudication, and gold labels remain local
  and ignored.
- Raw returns are immutable. Corrections occur through adjudication records.
- Reviewer pages work offline and make no network request.
- Reviewer-facing pages hide Agent 4 output, memory output, leakage status, and
  development/holdout assignment.
- AI, synthetic fixtures, same-pattern memory, and the historical analysis copy
  are prohibited as independent ground truth.

## Interpretation rules

- Safe N=0: every empirical performance field is null.
- Safe N=1–19: descriptive pilot reporting only.
- Safe N=20–24: quantitative MSc reporting is eligible with small-sample
  limitations.
- A positive number is not automatically a positive claim. Report uncertainty,
  paired regressions, and class-level harm.
- Current M4B-1 changes no classification, so it cannot improve classification
  accuracy over B0. A later frozen proposal is required before a positive
  classification delta is even possible.
- Negative and null results remain valid research results.

## Local outputs

All generated evidence and reviewer material is ignored:

`reports/generated/independent_evidence_v1/`

The tracked repository contains only schemas, validators, empty-package
infrastructure, tests, and this protocol.

