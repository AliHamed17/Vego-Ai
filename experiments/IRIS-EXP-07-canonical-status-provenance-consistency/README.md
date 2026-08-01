# IRIS-EXP-07 — Canonical status and provenance consistency

## Status

- Structural state: **PASS on 2026-08-01 for the preliminary ledger**
- Human/external truth state: **pending where identified by the registers**
- Full protocol state: **pending cross-view and external-authority closure**
- Run mode: read-only consistency audit
- Production impact: none

## Question

Do the immutable July 29 snapshots, current master state, derived supervisor
views, artifact hashes, and revision metadata agree about what was said, what
is current, what changed, and what remains unproved?

## Inputs

- `docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md`
- The July 29 requirements and action/question source registers.
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/decision-change-log.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- `docs/research/phd-proposal/claim-register.md`
- `docs/research/phd-proposal/external-fact-register.md`
- `docs/research/phd-proposal/iris-closure-governance-control.md`
- Current proposal, pre-read, presentation manifest, and Git revision.

## Procedure

1. Recompute hashes for every existing artifact listed in the provenance
   manifest and report stale, missing, or unexpected values.
2. Verify that July 29 source registers are labelled historical call-time
   snapshots and are not used as current-status authorities.
3. Require one active master row per stable control ID and compare its
   extraction, implementation, acceptance, and ongoing-control dimensions with
   every derived view.
4. Verify that every changed interpretation or decision has an append-only
   decision-log entry naming prior wording, new wording, source, approver,
   effective date, and affected artifacts.
5. Compare calendar, availability, deadline, partner, dataset, and access
   statements with the external-fact register. Fail any unverified meeting
   statement presented as confirmed current fact.
6. Verify that the recorded revision exists, that the worktree state is
   reported honestly, and that generated views do not claim a later revision
   than their inputs.
7. Report conflicts by control ID and artifact. Do not choose a substantive
   outcome automatically; use the authority order in the governance control.

## Outputs

- Hash and revision consistency report.
- Per-control cross-view status matrix.
- Stale/superseded wording and authority-conflict findings.
- External-fact verification mismatch report.
- Read-only pass/fail verdict.

## Metrics

| Metric | Gate | Definition | Target |
| --- | --- | --- | --- |
| Preliminary-ledger source hashes | Structure | Machine source and source-register hashes match the current ledger metadata | `100%` |
| Deterministic ledger regeneration | Structure | Tracked CSV/JSON match a clean deterministic regeneration | Exact match |
| CSV/JSON projection agreement | Structure | Control and review fields agree per segment | `1195/1195` |
| Existing-artifact hash freshness | Readiness | Existing tracked inputs with current hashes | `100%` |
| Canonical master uniqueness | Readiness | Active master rows per control ID | Exactly `1` |
| Status-dimension agreement | Readiness | Derived views matching the canonical master or explicitly dated as historical | `100%` |
| Unlogged current-wording changes | Closure | Current wording changes lacking a decision-log entry | `0` |
| Stale superseded statements | Closure | Derived artifacts presenting superseded wording as current | `0` |
| Unverified external facts presented as confirmed | Closure | Authority/deadline/partner/access claims without evidence | `0` |
| Revision/provenance contradictions | Closure | Invalid revision, impossible chronology, or falsely clean state | `0` |

## Acceptance

The structural pass applies only to the preliminary-ledger metrics. Full
acceptance requires every metric to meet its target. A conflict involving supervisor intent,
acceptance, or external authority remains a blocking finding until a human or
authoritative source resolves it; an automated audit cannot select the desired
interpretation.

## Dependencies

- Current provenance, master, decision, claim, and external-fact registers.
- Stable authority ordering and append-only historical records.
- Local access to the referenced source files and Git history.

## Claim boundary

A passing result demonstrates current-record consistency and provenance. It
does not validate the scientific quality of a claim, create supervisor
approval, or turn a partner-dependent or human-pending item into completion.
