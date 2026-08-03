# IRIS-EXP-09 — Supervisor acceptance and propagation

## Status

- Structural state: **PASS on 2026-08-01**
- Real supervisor outcome state: **pending**
- Acceptance evidence state: **not available**
- Production impact: none

## Question

Does the real supervisor cycle give every July 29 control and requested
decision an explicit outcome, preserve exact corrections, and propagate each
confirmed change to all affected current artifacts within 24 hours?

## Inputs

- Exact delivered package and delivery/access record from IRIS-EXP-08.
- Dated meeting record, decision worksheet, and end-of-call read-back.
- Written post-meeting confirmation or correction from Iris and Arnon.
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/decision-change-log.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- Current proposal, RQ pack, three-study contract, claim register, RACI/RAID,
  presentation manifest, schedule, and weekly pre-read.

## Procedure

1. Freeze the exact presented package and record the meeting date, participants,
   evidence source, and package hash.
2. Capture each `D-RQ-01` through `D-RQ-10` outcome as `Confirm`, `Confirm with
   correction`, `Retire or supersede`, or `Defer`. Silence remains `Defer`.
3. For every requirement, action, question, and newly discovered control,
   record the applicable final-state proposal, exact correction if any,
   approver, rationale, owner, due date/gate, evidence, and ongoing-control
   terms. Do not infer acceptance from attendance, receipt, or lack of comment.
4. Read back the exact RQ wording, Plan A/B boundary, claim limitations,
   owners, due dates, and exactly one next task before the meeting ends.
5. Obtain written confirmation or correction. Preserve both the live note and
   the later confirmation as separate evidence.
6. Create append-only decision/change entries and propagate each confirmed
   change to every applicable current artifact within 24 hours. Explicitly mark
   non-applicable targets.
7. Detect stale superseded wording, orphan decisions, and falsely closed rows;
   rerun structural/readiness assurance after propagation.

## Outputs

- Per-decision supervisor outcome record.
- Per-control acceptance/disposition matrix.
- Written-confirmation evidence links.
- Change-impact and propagation-lag report.
- End-of-call read-back and single-next-task record.

## Metrics

| Metric | Gate | Definition | Target |
| --- | --- | --- | --- |
| Decision-prompt structure | Structure | Worksheet exposes `D-RQ-01` through `D-RQ-10` | `10/10` |
| Propagation-schema structure | Structure | Decision log contains required change-impact fields | `100%` |
| Decision outcomes | Closure | `D-RQ-01` through `D-RQ-10` with an explicit allowed outcome | `10/10` |
| Control disposition coverage | Closure | Current controls with explicit supervisor disposition or still-visible blocker | `100%` |
| Silent acceptance | Closure | Controls closed because no objection was recorded | `0` |
| Written confirmation linkage | Closure | Confirmed/corrected decisions linked to written evidence | `100%` |
| Applicable propagation | Closure | Affected current artifacts updated or explicitly not applicable | `100%` |
| Propagation lag | Closure | Confirmed changes propagated or blocked with owner | `<=24 hours` |
| Stale superseded wording | Closure | Current artifacts presenting superseded text as active | `0` |
| Orphan decisions | Closure | Decisions lacking a control and affected-artifact link | `0` |
| Next commitment | Closure | Complete, unique next task | Exactly `1` |

## Acceptance

The structural pass establishes only that the worksheet and propagation schema
are ready. The full process passes when every available outcome is honest and fully
propagated. Program closure still fails while any control is `Partial`, `Open`,
`Blocked`, or `Deferred`. A rejected proposal also remains open until it is
corrected, superseded by an approved alternative, or formally ruled not
applicable.

## Dependencies

- A real meeting using the package accepted by IRIS-EXP-08.
- Iris and Arnon as decision authorities for their respective decisions.
- Written confirmation or correction evidence.
- Stable IDs, append-only decision history, and current impact targets.

## Claim boundary

A passing process result does not imply that every substantive control was
accepted. It proves only that real outcomes were captured and propagated
honestly; the per-control states determine closure eligibility.
