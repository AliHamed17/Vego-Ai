# 5 August Supervisor Package Delivery and Access Record

Status: **NOT SHARED — NOT DELIVERED — ACCESS NOT TESTED**

Last updated: 2026-08-03

This is an evidence form. Its existence does not show Ali approval, external
sharing, delivery, receipt, or recipient access. The source MIMIC/medical
folder is outside this package. Its metadata inventory, ACL/viewer-only
permission, and purpose-specific research authorization are independent
checks; only the metadata inventory was corroborated on 3 August.

## Authorization gate

| Check | State | Evidence |
| --- | --- | --- |
| Ali reviewed the exact package | NOT RECORDED | — |
| Ali approved external sharing | NOT RECORDED | — |
| Package contains no restricted data or private credentials | PASS — LOCAL AUTOMATED CONTENT CHECK; ALI REVIEW STILL REQUIRED | Final deck contains aggregate controls and source paths only; no patient row, credential, or private contact |
| Package permissions use least privilege | NOT TESTED | — |
| Source and working folders remain separate | PASS — METADATA-LEVEL LOCATION CHECK | [3 August boundary record](../governance/drive-boundary-verification-2026-08-03.md) |
| Source ACL/viewer-only permission | NOT VERIFIED | Accountable permission record required |
| Named-user research authorization | NOT VERIFIED | Purpose-specific authorization/DUA and ethics/privacy determination required |

Do not populate recipient sharing rows until Ali approves the exact hashed package.

## Exact package manifest

| Component | Path/link | Version | Bytes | SHA-256 | Review state |
| --- | --- | --- | ---: | --- | --- |
| PPTX | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx` | v10 local QA build; 21 slides | 98,468 | `7765132B6406796AFE802887A9CC69B9A903843BDCBEC606C517738D91421D24` | LOCAL TECHNICAL QA PASS; ALI REVIEW PENDING |
| PDF | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf` | Exact v10 PowerPoint export; 21 pages | 335,921 | `A8E296911F734477ADD5005BF02C305DFCA4C9E897532DA510A3D629E700F7EC` | LOCAL TECHNICAL QA PASS; ALI REVIEW PENDING |
| Presenter notes | Embedded in PPTX | 21/21 source-linked notes | included above | same as PPTX | AUTOMATED SOURCE-MARKER CHECK PASS; HUMAN REHEARSAL PENDING |
| Bilingual appendix | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx` | 1,195 machine-preliminary rows | 146,350 | `7F72BC625374C225B8C450E6A9EE5F4A6D147988BF35AF3BC54D4F5FC7C3F295` | STRUCTURE PASS; DUAL REVIEW `0/1,195` |
| Decision worksheet | Core slides 11–12 plus [presentation checklist](./2026-08-05-supervisor-presentation-checklist.md) | Working decision interface | — | recorded through package/provenance hashes | BUILT; OUTCOMES `0/10` |
| Presentation manifest | [manifest](./2026-08-05-supervisor-presentation-manifest.md) | Current working package | — | record final document hash in provenance before sharing | LOCAL PACKAGE BUILT; EXTERNAL REVIEW PENDING |
| Citation/source manifest | [Detached hash-bound source manifest](./2026-08-05-supervisor-source-manifest.json) generated from all 21 PPTX `[Sources]` note sections | Current local candidate; rerun after any deck/source edit | self-contained exact deck/source hashes | Deterministic check required before freeze | STRUCTURE INTERFACE READY; FINAL FREEZE PENDING |
| Render manifest | [Verified local record](./2026-08-05-supervisor-render-manifest.json), [pending template](./2026-08-05-supervisor-render-manifest.template.json), and `schemas/iris-presentation-render-manifest-v1.schema.json` | Exact v10 PPTX/PDF plus 21 native PNGs and montage | self-contained artifact hashes | Local technical inspection only | PASS — RELEASE/REHEARSAL STILL PENDING |
| Rehearsal record | [record](./2026-08-05-supervisor-rehearsal-record.md) | Automated preflight record | — | record final document hash in provenance before sharing | PRIOR AUTOMATED PREFLIGHT RECORDED; FINAL HASH-BOUND QA AND HUMAN REHEARSAL NOT RUN |

- Repository revision: `NOT FROZEN`; the corrected candidate must be bound to a committed revision at RG-04
- Package freeze time: `NOT FROZEN`
- Offline-backup state: `STALE / INVALIDATED`; the prior ZIP at `outputs/iris-closure-2026-08-01/VEGO-AI-August5-Supervisor-Package-local-backup.zip` predates the corrected PPTX/PDF and must be rebuilt after rehearsal and RG-04; it is local and was not shared

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
| Source metadata inventory still matches controlled baseline | NO DELIVERY-TIME CHECK RECORDED | Metadata-level recheck only; do not infer content integrity |
| Source ACL/viewer-only permission still correct | NO DELIVERY-TIME CHECK RECORDED | Accountable permission record required |
| Named-user research authorization is current | NO DELIVERY-TIME CHECK RECORDED | Purpose-specific authorization evidence required |
| Delivery event linked in decision/change record | NOT APPLICABLE — NOT DELIVERED | — |

- Final delivery verdict: `NOT DELIVERED`
- Final access verdict: `NOT TESTED`

Never use `sent`, `shared`, `delivered`, `received`, or `access confirmed` unless the corresponding row contains version-specific evidence.
