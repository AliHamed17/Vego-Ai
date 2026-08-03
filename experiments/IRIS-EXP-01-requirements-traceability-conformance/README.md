# IRIS-EXP-01 — Requirements traceability conformance

## Status

- Protocol state: **runnable, automated, read-only**
- Execution state: **PASS on 2026-07-30**
- Runner:

  ```powershell
  python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-01
  ```

- Production impact: none

## Question

Does the July 29 control package preserve complete, bidirectional, and
evidence-bounded traceability for Iris's 19 requirements, 15 actions, and 10
open questions without representing open work as completed?

## Inputs

- `docs/research/meetings/2026-07-29-iris-requirements-register.md`
- `docs/research/meetings/2026-07-29-iris-supervisor-action-register.md`
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- `docs/research/phd-proposal/three-study-contract.md`
- `docs/research/phd-proposal/claim-register.md`
- `docs/research/phd-proposal/decision-change-log.md`
- `docs/research/meetings/2026-08-05-supervisor-pre-read.md`

The bilingual transcript supplies machine-derived source anchors. It is an
input for traceability, not a human-confirmed quotation source.

## Procedure

1. Parse the source registers and require exactly `R-01`–`R-19`,
   `A-01`–`A-15`, and `Q-01`–`Q-10`, with no duplicate or missing identifiers.
2. Match every source identifier to exactly one active row in the master
   traceability register.
3. Require each master row to contain an accountable owner, due date or gate,
   dependency, deliverable/evidence path, acceptance check, status, and claim
   boundary.
4. Verify that each row retains a source-register or transcript anchor and that
   each referenced artifact exists or is explicitly described as future
   evidence.
5. Verify cross-links from the current proposal, study contract, claim
   register, decision log, and supervisor pre-read back to the applicable
   control identifiers.
6. Reject a row whose status says complete when its acceptance evidence is
   absent, provisional, machine-derived only, partner-dependent, or awaiting
   supervisor confirmation.
7. Produce a deterministic finding for each identifier and an aggregate
   conformance verdict without modifying any source artifact.

## Outputs

- Read-only console verdict.
- Ignored combined validation result under
  `reports/generated/iris_requirements_closure/latest.json` and `latest.md`.
- The tracked closure audit supplies per-ID findings; the ignored run record
  supplies deterministic aggregate checks and exact missing/malformed IDs.
- Aggregate counts for requirements, actions, questions, and blocking gaps.

No output may be treated as a supervisor approval record.

## Metrics

| Metric | Definition | Target |
| --- | --- | --- |
| Requirement ID coverage | Unique source and master rows for `R-01`–`R-19` | `19/19` |
| Action ID coverage | Unique source and master rows for `A-01`–`A-15` | `15/15` |
| Open-question ID coverage | Unique source and master rows for `Q-01`–`Q-10` | `10/10` |
| Required-field completeness | Rows with owner, date/gate, dependency, evidence, acceptance, status, and boundary | `44/44` |
| Source-anchor coverage | Rows linked to an authoritative register or machine-evidence segment | `44/44` |
| Existing-or-future evidence classification | Evidence paths that exist or are explicitly future/pending | `44/44` |
| False-closure findings | Completed rows lacking acceptance evidence | `0` |
| Duplicate/orphan identifiers | Duplicate IDs or IDs present on only one side of the crosswalk | `0` |

## Acceptance

The automated result passes only when every metric meets its target and every
open or partner-dependent item remains visibly open. A failure identifies the
exact control ID and field; it is not waived by aggregate coverage.

## Dependencies

- Stable July 29 source-register identifiers.
- The current successor master register and proposal package.
- `scripts/validate_iris_requirements_closure.py`.
- Human bilingual/speaker review before any exact attribution or quotation is
  promoted beyond machine-derived evidence.

## Claim boundary

A passing result establishes structural coverage and internal consistency of
the control package. It does **not** establish that Iris confirmed every
machine-derived interpretation, that supervisors approved the proposal, or
that the substantive requirements and external dependencies are complete.
