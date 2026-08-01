# Iris Zoom-to-Submission Closure Certificate — Template v1.0

> **TEMPLATE ONLY — NOT ISSUED — DOES NOT CERTIFY CLOSURE**

- Template version: `1.0`
- Template updated: `2026-08-01`
- Certificate ID when issued: `IRIS-CLOSE-YYYYMMDD-vX.Y`
- Certificate lifecycle: `DRAFT / BLOCKED / ISSUED / INVALIDATED`
- Supersedes certificate: `None / ID`

Certificate status: **NOT ISSUED**

Unresolved controls: **Unknown**

Human review: **PENDING**

Supervisor acceptance: **PENDING**

Submission evidence: **PENDING**

Closure-mode issuance requires these stable markers to read `ISSUED`, `0`, `COMPLETE`, `CONFIRMED`, and `VERIFIED`, respectively, and all detailed gates below must agree.

Complete this template only from the canonical [master traceability register](./master-traceability-register.md), the adjudicated call ledger, authoritative external evidence, and signed acceptance records. Delete no unresolved item to improve the closure ratio.

## 1. Certified baseline

| Field | Required value |
| --- | --- |
| Repository revision | `[full commit SHA]` |
| Working tree state | `[clean / exact intended paths listed]` |
| Source recording SHA-256 | `[M4A hash]` |
| Source video SHA-256 | `[MP4 hash]` |
| Provenance-manifest version/hash | `[value]` |
| Master-register version/hash | `[value]` |
| Adjudicated-ledger version/hash | `[value]` |
| Proposal version/hash | `[value]` |
| Presentation package version/hashes | `[PPTX, PDF, notes, appendix, manifest]` |
| Institutional checklist/version | `[authoritative source]` |
| Authorized submission receipt record | `docs/research/phd-proposal/authorized-submission-receipt.json` |
| Submission route | `[PENDING]` |
| Submission timestamp with timezone | `[PENDING]` |
| Receipt ID | `[PENDING]` |
| Submitted package SHA-256 | `[PENDING]` |
| External receipt artifact SHA-256 | `[PENDING]` |
| Receipt certificate binding | `[certificate ID and final certificate SHA-256 from receipt record]` |
| Explicit submission authorization | `[authority, timestamp, evidence path, evidence SHA-256]` |

## 2. Denominator and disposition

- Baseline controls: `44` (`19 R + 15 A + 10 Q`)
- New controls discovered during human review: `[count and IDs]`
- Final denominator: `[count]`
- Closed controls: `[count]`
- Closure ratio: `[closed]/[denominator]`

| Final disposition | Count | Control IDs |
| --- | ---: | --- |
| Accepted | `[0]` | `[IDs]` |
| Accepted with ongoing control | `[0]` | `[IDs]` |
| Accepted after correction | `[0]` | `[IDs]` |
| Superseded by approved decision | `[0]` | `[IDs]` |
| Not applicable by approved Plan B or other decision | `[0]` | `[IDs]` |
| Partial | `[0]` | `[IDs]` |
| Open | `[0]` | `[IDs]` |
| Blocked | `[0]` | `[IDs]` |
| Deferred | `[0]` | `[IDs]` |
| Rejected without approved resolution | `[0]` | `[IDs]` |

Issuance gate: the five allowed closure rows must sum to the final denominator, and every disallowed row must equal `0`.

## 3. Call-extraction assurance

| Check | Required result | Recorded result | Evidence |
| --- | --- | --- | --- |
| Media identity | Source hashes match provenance | `[PENDING]` | `[link]` |
| Segment coverage | `1,195/1,195`, or approved corrected denominator | `[PENDING]` | `[ledger]` |
| Timeline coverage | Full `46:26.283`, with gaps explained | `[PENDING]` | `[timeline record]` |
| Reviewer A | Complete review with identity/date | `[PENDING]` | `[record]` |
| Reviewer B | Independent complete review with identity/date | `[PENDING]` | `[record]` |
| Adjudication | Zero unresolved substantive disagreements | `[PENDING]` | `[record]` |
| Speaker attribution | Every named quotation confirmed | `[PENDING]` | `[record]` |
| Orphan clauses | Zero substantive clauses without a disposition | `[PENDING]` | `[report]` |

## 4. Implementation and acceptance assurance

| Check | Required result | Recorded result | Evidence |
| --- | --- | --- | --- |
| Every control has four status dimensions | Pass | `[PENDING]` | `[master register]` |
| Every control has owner, evidence, due/gate, and acceptance check | Pass | `[PENDING]` | `[master register]` |
| Iris dispositions recorded | All applicable rows | `[PENDING]` | `[signed minutes/decision log]` |
| Arnon dispositions recorded | All applicable rows | `[PENDING]` | `[signed minutes/decision log]` |
| Silence handled as Deferred | Pass | `[PENDING]` | `[meeting record]` |
| Corrections propagated within controlled cycle | Zero stale affected artifacts | `[PENDING]` | `[change log/validator]` |
| Recurring controls have cadence and next review | Pass | `[PENDING]` | `[master register]` |

## 5. External, medical, and research-evidence gates

| Check | Required result | Recorded result | Evidence |
| --- | --- | --- | --- |
| Closure-critical external facts | Verified, corrected, or retired | `[PENDING]` | `[external-fact register]` |
| University dates/process | Authoritatively verified | `[PENDING]` | `[official source]` |
| EXP-005 claims | Real-label gate honored | `[PENDING]` | `[experiment evidence]` |
| Medical route | `6/6` gates passed, or approved Plan B disposition | `[PENDING]` | `[readiness scorecard/decision]` |
| Restricted-data boundary | No unauthorized row-level or online-model use | `[PENDING]` | `[audit record]` |
| MIMIC status | Expected/present manifest reconciled or explicitly retired | `[PENDING]` | `[audit/decision]` |

## 6. Presentation, delivery, and submission gates

| Check | Required result | Recorded result | Evidence |
| --- | --- | --- | --- |
| 44-or-expanded control manifest | Every control reachable | `[PENDING]` | `[presentation manifest]` |
| Render/visual QA | Every slide inspected after final edit | `[PENDING]` | `[QA report]` |
| Timed and adversarial rehearsal | Both passed | `[PENDING]` | `[rehearsal record]` |
| Ali authorization | Exact package approved before sharing | `[PENDING]` | `[delivery record]` |
| Iris and Arnon access tests | Both passed | `[PENDING]` | `[delivery/access record]` |
| Supervisor decisions propagated | Pass | `[PENDING]` | `[decision/change log]` |
| Proposal approval | Explicit and version-specific | `[PENDING]` | `[approval evidence]` |
| Authorized submission | Schema-valid `VERIFIED` receipt record with route, zoned timestamp, receipt ID, package hash, external receipt hash, certificate binding, and hashed authorization evidence | `[PENDING]` | `[authorized-submission-receipt.json]` |

## 7. Validation record

| Mode/check | Command or method | Timestamp | Result | Evidence/log hash |
| --- | --- | --- | --- | --- |
| Structure | `python scripts/validate_iris_requirements_closure.py --all --mode structure` | `[time]` | `[PENDING]` | `[value]` |
| Readiness | `python scripts/validate_iris_requirements_closure.py --all --mode readiness` | `[time]` | `[PENDING]` | `[value]` |
| Closure | `python scripts/validate_iris_requirements_closure.py --all --mode closure` | `[time]` | `[PENDING]` | `[value]` |
| Evidence consistency | `[current project command]` | `[time]` | `[PENDING]` | `[value]` |
| Links/tables/diff | `[commands]` | `[time]` | `[PENDING]` | `[value]` |

Command names above are certificate fields, not evidence that those modes exist or passed. Record the actual implemented commands and outputs at issuance.

## 8. Exceptions and residual obligations

- Approved exceptions: `[None / list with decision IDs]`
- Ongoing controls: `[IDs, owner, cadence, next review, evidence expected]`
- Residual risks accepted by: `[names, date, exact rationale]`
- Known limitations: `[list]`

An exception cannot waive raw-source integrity, honest claim boundaries, explicit acceptance, restricted-data authorization, or authorized submission evidence.

## 9. Sign-off

| Role | Name | Decision | Date/time | Evidence/signature locator |
| --- | --- | --- | --- | --- |
| Lead/repository owner | Ali Hamed | `[PENDING]` | `[time]` | `[locator]` |
| Supervisor | Iris Reinhartz-Berger | `[PENDING]` | `[time]` | `[locator]` |
| Supervisor | Arnon Sturm | `[PENDING]` | `[time]` | `[locator]` |
| Institutional/process authority | `[name]` | `[PENDING]` | `[time]` | `[locator]` |
| Medical/data authority, if Plan A | `[name / N/A by approved Plan B]` | `[PENDING]` | `[time]` | `[locator]` |

## Certificate statement

Use this statement only after every gate above passes:

> Against the source identities, final denominator, artifact versions, explicit dispositions, and submission evidence recorded in this certificate, all controlled requirements, actions, and open questions from the 29 July 2026 supervisor call have an approved terminal disposition. This statement does not claim scientific performance beyond the separately cited evidence and remains valid only for the recorded versions.

If any source, denominator, decision, acceptance record, proposal version, or submission record changes, set certificate status to `INVALIDATED` and issue a new version after revalidation.
