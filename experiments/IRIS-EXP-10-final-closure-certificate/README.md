# IRIS-EXP-10 — Final closure certificate

## Status

- Structural state: **PASS on 2026-08-01**
- Issuance eligibility: **not eligible**
- Certificate state: **NOT ISSUED**
- Production impact: none

## Question

Can a versioned, evidence-linked certificate demonstrate that the full current
control denominator passed call extraction, implementation, explicit
acceptance, external-authority verification, proposal approval, and authorized
submission without hiding an open or human-dependent gate?

## Inputs

- `docs/research/phd-proposal/iris-closure-certificate-template.md`
- `docs/research/phd-proposal/iris-closure-governance-control.md`
- `schemas/iris-authorized-submission-receipt-v1.schema.json`
- `docs/research/phd-proposal/authorized-submission-receipt.template.json`
- A future `docs/research/phd-proposal/authorized-submission-receipt.json` only
  after a real authorized submission occurs.
- Final results for `IRIS-EXP-01` through `IRIS-EXP-09`.
- Human-adjudicated Zoom ledger and transcript-review evidence.
- Final master traceability, closure, decision, claim, external-fact, and
  ongoing-control registers.
- Exact approved proposal and presentation package manifests.
- Authoritative university-process checklist and submission receipt.
- Final Git revision, worktree state, artifact hashes, and validator outputs.

## Procedure

1. Freeze the candidate evidence set and record its revision, timestamp,
   timezone, file hashes, and current control denominator.
2. Recount all stable controls, including items discovered during bilingual
   review. Reject a fixed `44` denominator if newer controls exist.
3. Require every control to have passed extraction and implementation and to
   end in exactly one allowed state: `Accepted`, `Accepted with ongoing
   control`, `Accepted after correction`, `Superseded by approved decision`,
   or `Not applicable by approved decision`.
4. Fail issuance for `Partial`, `Open`, `Blocked`, `Deferred`, unqualified
   `Rejected`, missing evidence, expired evidence, or silent acceptance.
5. Require every ongoing control to name its owner, cadence, next review date,
   expected evidence, and escalation rule.
6. Verify authoritative deadline/process evidence, supervisor approval of the
   final proposal, and a schema-valid `VERIFIED` submission receipt. Require an
   authorized route, zoned timestamp, receipt ID, exact submitted-package hash,
   external receipt-artifact hash, final certificate ID/hash binding, and
   explicit hashed authorization evidence. A filename containing `receipt` is
   never evidence.
7. Require structural, readiness, and closure validator modes to pass against
   the same frozen revision. Record the exact commands and outputs.
8. Have Ali review and sign the certificate, then obtain the designated
   supervisor/administrative confirmation. If any input changes, invalidate the
   certificate and rerun the complete protocol.

## Outputs

- Versioned closure certificate or an explicit `NOT ISSUED` report.
- Frozen evidence manifest and current denominator.
- Per-control final-state appendix.
- Validator-result and submission-receipt links.
- Invalidation history for any superseded certificate.

## Metrics

| Metric | Gate | Definition | Target |
| --- | --- | --- | --- |
| Certificate marker structure | Structure | Status, unresolved, review, acceptance, and submission fields exist | `5/5` |
| Honest unissued baseline | Structure | Template remains `NOT ISSUED` while gates are pending | `1/1` |
| Current control coverage | Closure | Controls included in the frozen denominator | `100%` |
| Allowed final states | Closure | Controls ending in one of the five closure-eligible states | `100%` |
| Blocking final states | Closure | Partial/open/blocked/deferred/unqualified-rejected controls | `0` |
| Assurance protocol results | Closure | IRIS-EXP-01 through IRIS-EXP-09 accepted at their required human/structural levels | `9/9` |
| External-authority verification | Closure | Deadline, process, permissions, and submission route supported by authoritative evidence | `100%` |
| Proposal approval and receipt | Closure | Final supervisor approval plus schema-valid authorized receipt | `2/2` |
| Receipt identity and route | Closure | Authorized route, zoned timestamp, receipt ID, submitter, and recipient authority | `100%` |
| Receipt/package integrity | Closure | Submitted package and external receipt artifact exist and match recorded SHA-256 values | `2/2` |
| Certificate binding | Closure | Receipt identifies and hashes the issued certificate; certificate records receipt ID and evidence hashes | `100%` |
| Submission authorization | Closure | Explicit authority, zoned timestamp, evidence path, and matching authorization-evidence hash | `100%` |
| Evidence-manifest integrity | Closure | Referenced existing artifacts with current hashes | `100%` |
| Validator modes | Closure | Structure, readiness, and closure pass on the frozen revision | `3/3` |
| Required sign-offs | Closure | Ali and designated external confirmation recorded | `100%` |

## Acceptance

The structural pass establishes only that an honest unissued template exists.
Issue the certificate only when every closure target passes on the same frozen
revision. Otherwise publish only `NOT ISSUED` with the exact blockers. Any new
instruction, corrected transcript meaning, changed artifact, expired approval,
or missing receipt invalidates an earlier certificate until the full protocol
passes again.

## Dependencies

- Completed IRIS-EXP-01 through IRIS-EXP-09.
- Human reviewer, supervisor, and administrative evidence that automation
  cannot create.
- Final proposal approval and an authorized submission receipt.
- Stable immutable evidence and an auditable invalidation process.

## Claim boundary

The certificate concerns the bounded July 29-to-submission closure program at
one recorded revision. It does not prove scientific truth beyond the cited
evidence, guarantee future outcomes, authorize medical processing, or replace
university records.
