# EXP-029 — Frozen Candidate-Model Comparison

Status: **Blocked. Preregistered protocol only; no comparison has run.**

## Research question

Under a sealed, leakage-safe evaluation, does one preregistered candidate model
produce a different paired expert-agreement outcome from the frozen `gpt-4o`
condition while preserving the baseline and human-authority boundaries?

## Entry gate

All conditions are mandatory:

1. At least 20 generalization-safe, independently reviewed, adjudicated labels.
2. Reviewer agreement and disagreement adjudication complete.
3. Prompt, configuration, policy, and label-partition hashes frozen.
4. The sealed holdout has not been inspected for candidate selection.
5. Iris and Arnon approve the comparison and its claim boundary.
6. One candidate snapshot, evaluation criteria, and cost ceiling are recorded.
7. EXP-028 provenance capture passes for both conditions.

## Design

- Baseline condition: frozen `gpt-4o` protocol and the preserved Agent 4
  comparator.
- Candidate condition: one dated model snapshot chosen before output
  inspection.
- Identical prompts, parameters, inputs, retry policy, and parsing rules.
- Separate temporary output roots and `ModelExecutionManifest-v1` records.
- Paired evaluation on the sealed rows; no post-hoc policy or prompt changes.

## Metrics

- Primary: paired net correction against adjudicated labels.
- Secondary: accuracy, macro-F1, per-class precision/recall, paired correctness
  matrix, latency, token use, and bounded cost.
- Safety: parsing failures, missing fields, retry failures, subgroup harm,
  baseline hash drift, and unauthorized output writes.

## Decision rule

No candidate becomes the default automatically. Results are reported as
positive, null, mixed, or harmful according to the preregistered metrics.
Selection, if any, requires a new supervisor decision after the sealed result.

## Stop conditions

- Safe labels remain below 20.
- Reviewer agreement/adjudication is incomplete.
- A frozen hash differs or the holdout seal is broken.
- A candidate output requires a prompt, policy, or parser change.
- Cost, privacy, or baseline-safety limits are exceeded.

## Claim boundary

A favorable pilot would remain limited to the evaluated education-domain
sample. It would not prove generalization or authorize replacement of
`gpt-4o`, Agent 4, or the official baseline.
