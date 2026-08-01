# 5 August Supervisor Package Delivery and Access Record

Status: **NOT SHARED — NOT DELIVERED — ACCESS NOT TESTED**

Last updated: 2026-08-01

This is an evidence form. Its existence does not show Ali approval, external sharing, delivery, receipt, or recipient access. The source MIMIC/medical folder is outside this package and must remain viewer/read-only and unchanged.

## Authorization gate

| Check | State | Evidence |
| --- | --- | --- |
| Ali reviewed the exact package | NOT RECORDED | — |
| Ali approved external sharing | NOT RECORDED | — |
| Package contains no restricted data or private credentials | PASS — LOCAL AUTOMATED CONTENT CHECK; ALI REVIEW STILL REQUIRED | Final deck contains aggregate controls and source paths only; no patient row, credential, or private contact |
| Package permissions use least privilege | NOT TESTED | — |
| Source and working folders remain separate | NOT TESTED FOR DELIVERY | — |

Do not populate recipient sharing rows until Ali approves the exact hashed package.

## Exact package manifest

| Component | Path/link | Version | Bytes | SHA-256 | Review state |
| --- | --- | --- | ---: | --- | --- |
| PPTX | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx` | Local QA build; 21 slides | 96,137 | `E32ADF8B48FAC5DA4033E8259A8248384FC48A23326F569B9C7DB015EF34E9E3` | AUTOMATED QA PASS; ALI REVIEW PENDING |
| PDF | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf` | PowerPoint export; 21 pages | 332,486 | `83A99566411C5565800D83DEEBA255E2B5EB568EB25526AEA5FB89D0AA9F6D78` | AUTOMATED QA PASS; ALI REVIEW PENDING |
| Presenter notes | Embedded in PPTX | 21/21 source-linked notes | included above | same as PPTX | AUTOMATED SOURCE-MARKER CHECK PASS; HUMAN REHEARSAL PENDING |
| Bilingual appendix | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx` | 1,195 machine-preliminary rows | 146,350 | `7F72BC625374C225B8C450E6A9EE5F4A6D147988BF35AF3BC54D4F5FC7C3F295` | STRUCTURE PASS; DUAL REVIEW `0/1,195` |
| Decision worksheet | Core slides 11–12 plus [presentation checklist](./2026-08-05-supervisor-presentation-checklist.md) | Working decision interface | — | recorded through package/provenance hashes | BUILT; OUTCOMES `0/10` |
| Presentation manifest | [manifest](./2026-08-05-supervisor-presentation-manifest.md) | Current working package | — | record final document hash in provenance before sharing | LOCAL PACKAGE BUILT; EXTERNAL REVIEW PENDING |
| Citation/source manifest | 21 PPTX `[Sources]` note sections plus [provenance manifest](./2026-07-29-iris-supervisor-provenance-manifest.md) | Current working package | — | record final document hash in provenance before sharing | STRUCTURE PASS |
| Rehearsal record | [record](./2026-08-05-supervisor-rehearsal-record.md) | Automated preflight record | — | record final document hash in provenance before sharing | AUTOMATED PREFLIGHT PASS; HUMAN REHEARSAL NOT RUN |

- Repository revision: tracked closure package frozen in `18c0f2b1cf2170dec6ba7b6a4edfcd2869394051`; local ignored derivatives remain hash-bound in the provenance manifest
- Package freeze time: `NOT FROZEN`
- Offline-backup location and hash: `outputs/iris-closure-2026-08-01/VEGO-AI-August5-Supervisor-Package-local-backup.zip`; 477,215 bytes; SHA-256 `AAD3065C157A9C2056DAD687E26451A7D6941626AB9E7A77D177831F483420B3`; local only, not shared

## Delivery event

Delivery state: **NOT DELIVERED**

| Field | Recorded value |
| --- | --- |
| Authorized sender | PENDING |
| Authorized route | PENDING |
| Delivery time and timezone | NOT DELIVERED |
| Delivered package version/hash | NOT DELIVERED |
| Recipient list | PENDING |
| Delivery receipt/message ID | NOT DELIVERED |
| Permission level | NOT CONFIGURED |

## Recipient access tests

Access must be tested from each intended recipient account against the frozen package, not inferred from sender access.

| Recipient | Shared? | Link opens? | Expected files visible? | Permission correct? | Test time | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Iris Reinhartz-Berger | NO | NOT TESTED | NOT TESTED | NOT TESTED | — | — |
| Arnon Sturm | NO | NOT TESTED | NOT TESTED | NOT TESTED | — | — |

## Post-delivery integrity

| Check | State | Evidence |
| --- | --- | --- |
| Delivered hashes match Ali-approved package | NOT APPLICABLE — NOT DELIVERED | — |
| Both recipients acknowledge receipt/access | NOT APPLICABLE — NOT DELIVERED | — |
| Broken links or permission defects corrected and retested | NOT APPLICABLE — NOT TESTED | — |
| Source MIMIC/medical folder unchanged | NO DELIVERY-TIME CHECK RECORDED | — |
| Delivery event linked in decision/change record | NOT APPLICABLE — NOT DELIVERED | — |

- Final delivery verdict: `NOT DELIVERED`
- Final access verdict: `NOT TESTED`

Never use `sent`, `shared`, `delivered`, `received`, or `access confirmed` unless the corresponding row contains version-specific evidence.
