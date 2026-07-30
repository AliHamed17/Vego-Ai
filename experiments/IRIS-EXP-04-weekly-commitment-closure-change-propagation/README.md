# IRIS-EXP-04 — Weekly commitment closure and change propagation

## Status

- Structural protocol state: **PASS on 2026-07-30**
- First substantive weekly-cycle state: **pending a completed supervisor cycle**
- Execution state: **READY_PENDING_NEXT_MEETING**
- Runner:

  ```powershell
  python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-04
  ```

- Production impact: none

## Question

Does each weekly supervisor cycle close or explicitly carry forward the previous
commitment, capture Iris and Arnon's decisions without inferring acceptance,
propagate confirmed changes to every affected control artifact, and end with
exactly one verifiable next task?

## Inputs

- `docs/templates/weekly-supervisor-pre-read.md`
- `docs/templates/supervisor-decision-change-log.md`
- `docs/research/phd-proposal/decision-change-log.md`
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/three-study-contract.md`
- `docs/research/phd-proposal/claim-register.md`
- `docs/research/phd-proposal/resource-raci-raid-register.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- Current proposal, literature controls, presentation, schedule, and the
  previous and current weekly pre-reads.

## Procedure

1. Identify the previous meeting's single committed task, owner, due date,
   definition of done, evidence, and claim boundary.
2. Require one explicit result: `Accepted`, `Accepted with changes`, `Not
   accepted`, or `Deferred`. Silence, attendance, or document receipt is not
   acceptance.
3. For every new decision or record correction, require a stable ID, source,
   confidence, exact outcome, selected wording, approver, owner, evidence,
   due/gate, affected artifacts, superseded decision, and confirmation state.
4. Check the change-impact list across traceability, study contract, claim
   register, RACI/RAID, proposal/presentation, literature taxonomy, schedule,
   and weekly pre-read. Mark non-applicable targets explicitly rather than
   silently omitting them.
5. Preserve the prior wording and source; changes create new entries and name
   what they supersede.
6. Require propagation within 24 hours of a confirmed supervisor decision, or
   a dated blocker and owner.
7. Require exactly one next weekly task with an owner, due date/timezone,
   deliverable, definition of done, evidence boundary, dependencies, and
   fallback.
8. Emit structural findings without changing any project record.

## Outputs

- Read-only console verdict.
- Ignored combined validation result under
  `reports/generated/iris_requirements_closure/latest.json` and `latest.md`.
- Previous-commitment disposition finding.
- Per-decision change-propagation matrix.
- Orphan/stale-reference findings.
- Next-task completeness finding.

## Metrics

| Metric | Definition | Target |
| --- | --- | --- |
| Previous-commitment disposition | Prior single task has an explicit allowed result and evidence | `1/1` |
| Decision-record completeness | Decisions contain every required field | `100%` |
| Confirmation honesty | Draft/unconfirmed decisions not represented as confirmed | `100%` |
| Applicable propagation coverage | Applicable change-impact targets updated or linked | `100%` |
| Propagation lag | Confirmed decisions propagated or blocked with owner | `<=24 hours` |
| Orphan decisions | Decisions with no affected control/artifact link | `0` |
| Silent historical rewrites | Prior decisions or raw evidence overwritten | `0` |
| Stale superseded wording | Active artifacts still presenting superseded wording as current | `0` |
| Next weekly commitment | Complete, unique next task | Exactly `1` |

## Acceptance

The structural run passes only if all available records meet the targets. The
first substantive weekly-cycle result remains pending until an actual meeting
has a pre-read, explicit outcomes, a read-back, and post-meeting propagation.
An absent real cycle must be reported as `NOT YET EVALUABLE`, never as a pass.

## Dependencies

- One completed weekly meeting cycle with dated records.
- Current pre-read and decision/change templates.
- Stable cross-document IDs and an append-only decision history.
- `scripts/validate_iris_requirements_closure.py`.
- Human confirmation for supervisor decisions and transcript corrections.

## Claim boundary

A passing result supports process closure and change-control consistency for the
examined weekly cycle. It does not prove that the research deliverable is
scientifically correct, that Iris approved an unconfirmed decision, or that
future commitments will be completed.
