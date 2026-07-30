# IRIS-EXP-03 — Claim-language and evidence-boundary audit

## Status

- Protocol state: **runnable, automated, read-only**
- Execution state: **PASS on 2026-07-30**
- Runner:

  ```powershell
  python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-03
  ```

- Production impact: none

## Question

Does every material statement in the supervisor-facing package use a registered
claim state, evidence source, limitation, and permitted strength, with no
unsupported accuracy, generalization, effort, medical, partner, novelty,
deadline, approval, or transcript-attribution language?

## Inputs

- `docs/research/phd-proposal/claim-register.md`
- `docs/research/phd-proposal/proposal-v0.1.md`
- `docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`
- `docs/research/meetings/2026-08-05-supervisor-pre-read.md`
- `docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- `docs/research/phd-proposal/three-study-contract.md`
- `docs/research/phd-proposal/master-traceability-register.md`
- Candidate presentation and presenter notes when available.

## Procedure

1. Extract quantitative, comparative, novelty, doctoral-adequacy, approval,
   completion, generalization, human-effort, medical, partner, deadline, and
   transcript-attribution statements from every supervisor-facing input.
2. Map each material statement to a current claim-register ID and one allowed
   state: `Established`, `Preliminary`, `Planned`, `Blocked`, or
   `Partner-dependent`.
3. Compare wording strength with the claim's permitted formulation, evidence,
   evidence needed, owner, and boundary.
4. Require every preliminary, planned, blocked, or partner-dependent statement
   to expose the relevant limitation or gate close enough for a reviewer to
   interpret it correctly.
5. Fail positive accuracy, macro-F1, generalization, effort-reduction, medical
   performance, patient-benefit, partner-commitment, dataset-selection,
   supervisor-approval, literature-completion, or official-deadline statements
   when the register says they are not established.
6. Fail exact transcript quotation or confident speaker attribution while
   bilingual/speaker review remains pending.
7. Report each finding with file, line, candidate claim ID, current state, and
   required correction. Do not rewrite the reviewed documents.

## Outputs

- Read-only console verdict.
- Ignored combined validation result under
  `reports/generated/iris_requirements_closure/latest.json` and `latest.md`.
- Claim-to-statement matrix.
- Release-blocking findings with exact locations and permitted alternatives.
- Counts by claim state and risk family.

## Metrics

| Metric | Definition | Target |
| --- | --- | --- |
| Material-claim registration | Material statements mapped to a claim ID | `100%` |
| State-vocabulary validity | Mapped states using the five allowed values | `100%` |
| Evidence/boundary completeness | Non-established statements with evidence need and visible limitation/gate | `100%` |
| Over-strength positive claims | Statements exceeding their registered state | `0` |
| Closed-gate contradictions | Positive claims for EXP-005, medical readiness, completed literature, partner commitment, or official deadlines | `0` |
| Unreviewed exact quotations/attributions | Direct meeting quotations or certain attribution before human review | `0` |
| Unregistered high-risk statements | High-risk statements lacking a claim-register row | `0` |

## Acceptance

Every metric must meet its target. Any unregistered or over-strength material
claim blocks supervisor-package release until the text is corrected or a new
claim row with legitimate evidence and approval is added.

## Dependencies

- A current, internally consistent claim register.
- Stable supervisor-facing source files.
- `scripts/validate_iris_requirements_closure.py`.
- Human review for semantic context, paraphrase quality, and any proposed
  evidence-state change.

## Claim boundary

A passing audit shows that the reviewed language matches the registered
evidence boundaries. It does not independently validate the truth, scientific
quality, completeness, or supervisor acceptance of the underlying evidence.
