# Iris Zoom-to-Submission Closure Governance Control

Status: **Active internal control; human adjudication, supervisor acceptance, and submission remain pending.**

Last updated: 2026-08-01

This document defines which record is authoritative, how status is represented, and what evidence is required before anyone can claim that the 29 July supervisor-call requirements are closed. It changes no production VEGO-AI interface or behavior.

## Authoritative record order

When two artifacts differ, use this order and record the reconciliation in the decision/change log:

1. The raw M4A, MP4, and `recording.conf` are immutable primary evidence.
2. The preserved Hebrew ASR and aligned machine translation are immutable machine-derived evidence.
3. A future dual-reviewed and adjudicated segment ledger, produced through the [separate human-review merge workflow](../meetings/2026-07-29-iris-zoom-human-review-workflow.md), is the authoritative interpretation of the call. Until it exists, the current transcript is machine-derived and quotations remain prohibited.
4. The [requirements register](../meetings/2026-07-29-iris-requirements-register.md) and [action/open-issue register](../meetings/2026-07-29-iris-supervisor-action-register.md) are immutable call-time extraction snapshots.
5. The [master traceability register](./master-traceability-register.md) is the only canonical current implementation and acceptance state.
6. The proposal, presentation, pre-read, closure audit, dashboards, and reports are derived views. They must be regenerated or corrected when the master changes.
7. A completed copy of the [closure-certificate template](./iris-closure-certificate-template.md) is the final signed closure record. The template itself is not a certificate.

The [provenance manifest](../meetings/2026-07-29-iris-supervisor-provenance-manifest.md) controls source identities, hashes, and transformation boundaries. The [external-fact register](./external-fact-register.md) controls claims from the call that require authority outside the recording.

## Stable identifiers and denominator

- The baseline denominator is `44`: `R-01`–`R-19`, `A-01`–`A-15`, and `Q-01`–`Q-10`.
- Existing identifiers are never renamed, reused, or renumbered.
- A newly discovered requirement, action, question, risk, or decision receives the next stable ID in its class and immediately increases the denominator.
- Splitting a compound control requires linked child IDs; the original row remains as a parent or is superseded explicitly.
- Duplicate controls may be superseded, but never silently deleted.
- Closure ratios always state both numerator and the current denominator, plus the register revision used.

## Four independent status dimensions

Each current-state row must carry all four dimensions. A value in one dimension never implies progress in another.

| Dimension | Allowed states | Evidence required to advance |
| --- | --- | --- |
| Extraction | `Machine-only`; `Reviewer A complete`; `Reviewer B complete`; `Disputed`; `Adjudicated` | Segment IDs and timestamps; reviewer identity/date; disagreement and adjudication record where applicable |
| Implementation | `Not started`; `Partial`; `Evidence ready`; `Acceptance check passed` | Versioned deliverable, evidence link, owner, date, hash when applicable, and the row-specific acceptance result |
| Acceptance | `Pending`; `Confirmed`; `Corrected`; `Retired or superseded`; `Not applicable`; `Deferred`; `Rejected` | Explicit accountable decision, exact wording/rationale, date, approver, and affected artifacts; silence is `Deferred` |
| Ongoing control | `Not recurring`; `Cadence pending`; `Active`; `Overdue`; `Closed by decision` | Cadence, owner, next review date, expected evidence, and latest-cycle result |

`Evidence ready` is not `Acceptance check passed`. `Acceptance check passed` is not supervisor acceptance. Calendar acceptance is not meeting-execution acceptance. A prepared or privately stored package is not delivered or access-tested.

## Final closure states

A row counts toward signed 100% closure only when its acceptance outcome is represented by one of these certificate dispositions:

- `Accepted`
- `Accepted with ongoing control`
- `Accepted after correction`
- `Superseded by approved decision`
- `Not applicable by approved Plan B or other decision`

`Partial`, `Open`, `Blocked`, `Deferred`, `Rejected`, missing evidence, and missing approver prevent issuance. `Rejected` requires corrective action or an approved superseding/not-applicable decision before closure.

## Controlled change workflow

1. Preserve the raw media, ASR, and machine translation unchanged.
2. Record extraction corrections by segment ID, original text, reviewed Hebrew/English, reviewer, date, and reason.
3. Add or update the master row; do not edit the substantive rows in the call-time snapshots.
4. Record the decision, rationale, approver, and superseded wording in the [decision/change log](./decision-change-log.md).
5. Propagate the approved change to every affected derived artifact.
6. Refresh hashes and revision metadata in the provenance manifest.
7. Run the applicable structure, readiness, and closure checks.
8. Invalidate any earlier closure certificate if the denominator, source identity, decision, or acceptance evidence changes.

## Evidence and claim boundaries

- Later unattributed transcript turns use `supervisor-side statement` until speaker adjudication is complete.
- Direct quotation requires reviewed Hebrew, reviewed English, confirmed speaker, timestamp, and adjudicator approval.
- External policy, deadline, access, privacy, data-volume, partner, and availability statements remain `Unverified meeting statement` until the external-fact register links authoritative evidence.
- EXP-005 remains blocked at `0/24` safe labels until real independent human labels exist.
- Medical readiness remains blocked until all six gates pass; source-folder visibility is not authorization to inspect patient rows.
- No package is `Delivered`, `Shared`, `Access tested`, `Accepted`, or `Submitted` without the corresponding record.

## Required closure package

The following evidence must exist before a certificate can be issued:

- complete segment disposition and bilingual/speaker adjudication record;
- master traceability register with all four status dimensions;
- external-fact register with no closure-critical unverified fact;
- exact presentation package and [44-control manifest](../meetings/2026-08-05-supervisor-presentation-manifest.md);
- completed [rehearsal record](../meetings/2026-08-05-supervisor-rehearsal-record.md) and [delivery/access record](../meetings/2026-08-05-supervisor-delivery-access-record.md);
- explicit Iris/Arnon decisions and propagation evidence;
- final proposal, institutional checklist, an actual verified receipt conforming to the [authorized-submission receipt schema](../../../schemas/iris-authorized-submission-receipt-v1.schema.json), and artifact hashes; and
- passing closure-mode validation with zero disallowed terminal states.

## Current declaration

The baseline controls are governed and traceable, but 100% closure is **not established**. The local August 5 presentation package and automated/render QA exist; human bilingual review, full speaker adjudication, Ali release approval, timed/adversarial rehearsal, authorized delivery/access tests, supervisor dispositions, external verification, and submission evidence remain separate gates.
