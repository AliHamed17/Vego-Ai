# 2026-07-15 Supervisor Decision Package Index

Audience: Iris and Arnon  
Meeting format: 20-minute presentation followed by 20 minutes of decision discussion  
Status: **Working package. No decision or deliverable is approved until an explicit outcome and approver are recorded.**

## Purpose

This package supports two separate tasks:

1. correct or confirm the machine-derived July 1 record without changing the raw recording or ASR; and
2. record the remaining H-layer decisions using one shared decision-register interface.

The earlier HTML meeting deck and its open-question list are superseded by this index and the sources below. They are legacy working artifacts, not authoritative decision records.

## Required chronology separation

| Stream | Contents | Authority |
| --- | --- | --- |
| July 1 record | Local recording and ASR, selected Hebrew evidence, D1-D12 English paraphrases, attributed actions | Historical source pending participant correction/confirmation |
| July 4-10 working layer | Architecture options, S1-S7/E1-E15 formalization, provisional specifications, scaffolds, and historical offline results | Later author work; not attributable to Iris or Arnon |
| July 15 decisions | M-01 through M-06 outcomes, rationale, approver, owner, and due date | Authoritative only after explicit meeting read-back |

## Authoritative Markdown sources

| Interface | Source |
| --- | --- |
| Canonical machine-derived record and D1-D12 matrix | `2026-07-01-supervisor-meeting-iris.md` |
| Timestamped Hebrew evidence appendix | `2026-07-01-supervisor-evidence-appendix.md` |
| Raw-source inventory, hashes, and privacy policy | `2026-07-01-supervisor-provenance-manifest.md` |
| Single decision-register interface | `2026-07-15-supervisor-decision-register.md` |
| July 1 and post-decision action tracking | `2026-07-15-supervisor-action-register.md` |
| Dated chronology and offline-evidence annex | `2026-07-15-supervisor-follow-up-annex.md` |
| Two-page pre-read source | `2026-07-15-supervisor-executive-pre-read.md` |
| During/after-meeting capture source | `2026-07-15-post-meeting-capture-template.md` |
| Output versions, paths, hashes, and generation record | `2026-07-15-decision-package-manifest.md` |

The decision register is the source of truth for decision wording. Deck, pre-read, worksheet, and post-meeting capture fields must not introduce additional decision IDs or open questions.

## Decision agenda

| ID | Required decision | Priority |
| --- | --- | --- |
| M-01 | Confirm or correct D1-D12 and the six attributed July 1 actions | Mandatory |
| M-02 | Select the H-layer decomposition while keeping H1/H2/H3 visible | Mandatory |
| M-03 | Select passive observation scope, active routing triggers, pilot dosage, and cap policy | Mandatory |
| M-04 | Select H-Verify source order and convergence bound | Mandatory |
| M-05 | Set human authority, timeout behavior, reviewer roles, and implementation-authorization boundary | Mandatory |
| M-06 | Set MSc-question timing and the future-work boundary | If time permits |

Allowed decision outcomes are `Accepted`, `Accepted with changes`, `Rejected`, and `Deferred`. Pre-meeting rows use `Not yet recorded` only as a placeholder, never as an outcome.

## Shareable outputs

The generated package consists of:

- one separate 23-slide PPTX: 12 decision slides plus 11 evidence/reference appendices;
- a rendered PDF of that deck;
- a two-page pre-read and decision worksheet PDF; and
- matching copies in `C:\Users\ahamed\Claude\Projects\vego-ai`.

Use `2026-07-15-decision-package-manifest.md` for exact paths and SHA-256 hashes. The raw recording and full ASR remain local and are never copied into the shareable folder.

## Evidence and claim boundaries

- `threshold_sev2` is a replay-based pilot candidate, not an approved default.
- Bundling supports only a modest observed workload reduction in the cited setting.
- EXP-009 and EXP-010 are assumption-driven synthetic rule tests, not validation against real expert mistakes.
- EXP-005 remains the parked real-label gate; supplied real labels remain at zero and must never be invented or auto-filled.
- EXP-012 remains outside the main decision story.
- Recorded experiment values and test counts are historical unless the output manifest explicitly records a rerun.
- No package artifact claims improved accuracy, demonstrated generalization, or clinical performance.
- MediVARIA and domain-parameterized specifications remain proposed future-work directions.

## Runtime and approval boundary

This is a documentation and decision-support package. It does not change runtime APIs, Agents 1-4, Agent 4 behavior, schemas, frozen baselines, protected framework paths, evaluation outputs, or EXP-005 labels. Detailed specifications remain provisional; the July 10 prototype is retired historical scaffolding, not runnable evidence. Approval of a decision document is not authorization to edit live runtime paths; M-05 requires a separately approved allowed-touch list and later implementation authorization.

## Meeting close and follow-up

Read back every M-decision with outcome, rationale, approver, owner, due date, affected artifacts, and confirmation status. Silence or ambiguity is recorded as `Deferred`. Within 24 hours, issue corrected minutes, update both registers, revise only provisional artifacts required by accepted decisions, and regenerate the shareable outputs and manifest.
