# 5 August Supervisor Presentation and 44-Control Manifest

Status: **BUILT LOCALLY — AUTOMATED QA PASSED — HUMAN REVIEW/REHEARSAL/SHARING/ACCEPTANCE PENDING**

Last updated: 2026-08-03

- Audience: Iris Reinhartz-Berger, Arnon Sturm, and Ali Hamed
- Built format: 12-slide English core plus 9-slide evidence appendix, with presenter notes on all 21 slides
- Planned duration: maximum 11-minute core, subject to meeting confirmation
- Canonical current status: [master traceability register](../phd-proposal/master-traceability-register.md)
- Release control: [supervisor release gate and runbook](./2026-08-05-supervisor-release-gate-and-runbook.md)
- Current implementation evidence: [1 August implementation manifest](../phd-proposal/next-step-implementation-manifest-2026-08-01.md)

This manifest maps the `44` baseline controls (`19 R + 15 A + 10 Q`) to the built presentation. A mapping proves reachability in the local package; it does not prove human transcript review, live rehearsal, delivery, recipient access, supervisor decision, or acceptance.

## Package inventory

| Component | Required state before delivery | Current state | Version/hash/evidence |
| --- | --- | --- | --- |
| PPTX | Built from current controlled sources; Ali review still required before sharing | BUILT LOCALLY; 21 slides; v10 native render inspected; exact RQs, gap boundary, scientific crosswalk, canonical decision vocabulary, R-04/A-03/A-06 slide mapping, and control-status legend synchronized | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx`; 98,468 bytes; SHA-256 `7765132B6406796AFE802887A9CC69B9A903843BDCBEC606C517738D91421D24` |
| PDF | Exported from the exact v10 PPTX and visually checked | BUILT LOCALLY; 21 pages | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf`; 335,921 bytes; SHA-256 `A8E296911F734477ADD5005BF02C305DFCA4C9E897532DA510A3D629E700F7EC` |
| Presenter notes | Complete, timed, and source-linked | 21/21 source-linked notes; human timed rehearsal pending | PPTX contains 21 `[Sources]` sections |
| Bilingual evidence appendix | Human-reviewed before quotation or named attribution | BUILT AS MACHINE-ONLY REVIEW INTERFACE; `0` dual-reviewed rows; no direct quotations | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx`; SHA-256 `7F72BC625374C225B8C450E6A9EE5F4A6D147988BF35AF3BC54D4F5FC7C3F295` |
| Decision worksheet | D-RQ-01–D-RQ-10 ready for exact outcomes | BUILT in core and pre-read; `0/10` outcomes recorded | [presentation checklist](./2026-08-05-supervisor-presentation-checklist.md) |
| Source/citation manifest | Every `[Sources]` path resolves and is hash-bound to the exact local PPTX | Detached deterministic manifest; rerun after any deck or source edit; external facts retain their verification states | [hash-bound source manifest](./2026-08-05-supervisor-source-manifest.json) plus [source provenance](./2026-07-29-iris-supervisor-provenance-manifest.md) |
| Rendered-slide QA report | Every slide from the final local PPTX rendered, hash-bound, and inspected | PASS — local technical QA for exact v10 candidate; Ali review and human rehearsal remain pending | [verified local render manifest](./2026-08-05-supervisor-render-manifest.json), [pending template](./2026-08-05-supervisor-render-manifest.template.json); schema `schemas/iris-presentation-render-manifest-v1.schema.json` |
| Local offline backup | Exact PPTX, PDF, and review workbook; not a delivery event | STALE - invalidated by the corrected PPTX/PDF; rebuild required after human rehearsal and RG-04 freeze | Prior ZIP hash `AAD3065C157A9C2056DAD687E26451A7D6941626AB9E7A77D177831F483420B3`; must not be delivered |
| Delivery/access record | Ali authorization plus Iris/Arnon access tests | NOT SHARED / NOT TESTED | [delivery/access record](./2026-08-05-supervisor-delivery-access-record.md) |

## Built checkpoints, slide appendices, and evidence aliases

- `P-01`–`P-12` use the sequence in the [presentation checklist](./2026-08-05-supervisor-presentation-checklist.md).
- Built appendix slides are `A1`–`A2` requirements, `A3`–`A4` actions, `A5` open questions, `A6` claim states, `A7` bilingual alignment, `A8` scientific experiment crosswalk, and `A9` package gates.
- The coverage tables below also use documentary evidence aliases: `APP-A` = the A1–A5 R/A/Q control rows and current four-dimensional status; `APP-B` = A7 plus transcript/provenance and priority human-review ranges; `APP-C` = P-03–P-06 plus the RQ/legacy crosswalk and three-study contract; `APP-D` = A6 plus claim and external-fact registers; `APP-E` = P-07 plus literature schema, seed provenance, and search/screening state; `APP-F` = P-08–P-09 plus the MIMIC manifest, data zones, and G1–G6; `APP-G` = P-10–P-12 plus A9, RACI/RAID, official-process unknowns, milestones, and partner dependencies.

## Requirements coverage — 19/19 mapped

| ID | Planned checkpoint | Appendix/evidence anchor | Required live treatment | Decision or acceptance sought |
| --- | --- | --- | --- | --- |
| R-01 | P-03 | APP-A; APP-C | Show one umbrella RQ and exactly SQ1–SQ3 as provisional wording | D-RQ-01; D-RQ-02 |
| R-02 | P-04 | APP-A; APP-C | Map every SQ to method, evidence, artifact, metrics, contribution, dependency, and fallback | D-RQ-03 |
| R-03 | P-02; P-04 | APP-A; proposal skeleton | Show all six proposal areas and label incomplete sections honestly | Accept/correct proposal-coverage record |
| R-04 | P-10 | APP-G | Show the doctoral-adequacy caption (novelty/scale/feasibility/resources/schedule) and its per-dimension state | D-RQ-03–D-RQ-05; assign gaps |
| R-05 | P-01; P-10 | APP-G | State that this weekly deck is not the candidacy deck and official format remains unverified | Assign A-14/Q-08 owner |
| R-06 | P-02; P-12 | APP-A | Show dated writing/research delta while administration remains open | Accept/correct progress; choose one next task |
| R-07 | P-03; P-06 | APP-C | Demonstrate that every RQ is answerable without medicine | D-RQ-01–D-RQ-05 |
| R-08 | P-02; P-08; P-09 | APP-D | State software/modeling evidence boundary; show EXP-005 `0/24` and no medical result | D-RQ-07 |
| R-09 | P-06; P-09; P-10 | APP-F; APP-G | Show that medical people/data/authorization are not on the only completion path | D-RQ-04; D-RQ-05; D-RQ-10 |
| R-10 | P-06 | APP-C; APP-F | Show Plan A, Plan B, common RQs, dependencies, and proposed fallback rule | D-RQ-04–D-RQ-06 |
| R-11 | P-09 | APP-F | Show metadata/schema observations and stop boundary only; no elapsed-time claim | D-RQ-09 |
| R-12 | P-09 | APP-D; APP-F | State fail-closed VDI/local-offline-model boundary and unverified institutional policy | D-RQ-09; assign authority in D-RQ-10 |
| R-13 | P-10; P-12 | APP-G | Separate confirmed calendar recurrence from not-yet-run task-focused closeout cycle | Confirm ongoing cadence and one next task |
| R-14 | P-03; P-04; P-07; P-10 | APP-A; APP-C; APP-E | Show each next-package component and its exact completion/delivery state | Accept/correct package; unresolved work stays assigned |
| R-15 | P-07 | APP-E | Show one-paper-per-row structure and author/researcher separation | D-RQ-08 |
| R-16 | P-07 | APP-E | Show living taxonomy/gap workflow as prepared or actually executed, never conflated | D-RQ-08 |
| R-17 | P-10 | APP-G | Show source/working separation, private status, and missing supervisor access tests | D-RQ-10; later access evidence |
| R-18 | P-10 | APP-D; APP-G | Label September/October dates as working targets until official confirmation | Assign A-14/Q-08 owner and deadline |
| R-19 | P-10 | APP-E; APP-G | Distinguish Penina reuse plan from completed course deliverables and verify dates | Accept/correct reuse direction; assign date verification |

## Actions coverage — 15/15 mapped

| ID | Planned checkpoint | Appendix/evidence anchor | Required live treatment | Decision or acceptance sought |
| --- | --- | --- | --- | --- |
| A-01 | P-03; P-04 | APP-C | Present draft RQ/study contract without implying approval | D-RQ-01–D-RQ-03 |
| A-02 | P-07 | APP-E | Show protocol and actual search-log state separately | D-RQ-08; agree next executed search tranche |
| A-03 | P-02; P-07 | APP-E | Show workbook/seed evidence and remaining verification/screening work | Accept/correct narrow completion record |
| A-04 | P-10 | APP-G | Show private working area; state not supervisor-shared/access-tested | Ali authorization remains prerequisite; assign access test |
| A-05 | P-09; P-10 | APP-D; APP-F | Report call-time viewer-share statement and unresolved receipt/authority | Assign source-owner/receipt verification |
| A-06 | P-02; P-10 | APP-G | Show recurring-calendar evidence only | Accept/correct calendar record |
| A-07 | P-12 | APP-A; APP-G | Record completed evidence, one task, owner, due date, and definition of done | Explicit weekly closeout |
| A-08 | P-09 | APP-F | Show bounded metadata/schema audit and missing elapsed-time/human-review evidence | D-RQ-09 |
| A-09 | P-09; P-10 | APP-F; APP-G | Show medical readiness roles and G1–G6 as unpassed until evidenced | D-RQ-10; apply fallback rule |
| A-10 | P-06 | APP-C; APP-F | Present both plans and proposed automatic fallback | D-RQ-04–D-RQ-06 |
| A-11 | P-09 | APP-D; APP-F | Present constraints as meeting statements pending authority/model approval | Assign data/security owner in D-RQ-10 |
| A-12 | P-10 | APP-G | Show developed-draft milestone and current proposal delta | Accept/correct internal date and deliverable |
| A-13 | P-10 | APP-G | Show early-October target as provisional, with submission receipt required | Assign official-date verification |
| A-14 | P-10; P-11 | APP-D; APP-G | List deadline, reviewer count, nomination, committee, and format as unverified | D-RQ-10 assignment and dated inquiry |
| A-15 | P-10; P-11 | APP-D; APP-G | Show partner-loop commitment as unverified until invitation/minutes exist | D-RQ-10 assignment; no partner claim |

## Open-question coverage — 10/10 mapped

| ID | Planned checkpoint | Appendix/evidence anchor | Required live treatment | Decision or acceptance sought |
| --- | --- | --- | --- | --- |
| Q-01 | P-03; P-04 | APP-C | Show exact recommended four-string hierarchy | D-RQ-01–D-RQ-03 |
| Q-02 | P-06; P-09 | APP-C; APP-F | Decide medicine’s conditional role without assuming route/readiness | D-RQ-04; D-RQ-10 or Defer |
| Q-03 | P-06 | APP-C; APP-F | Confirm/correct Plan A/B boundary and fallback trigger | D-RQ-04–D-RQ-06 |
| Q-04 | P-07 | APP-E | Confirm/correct literature categories and synthesis fields | D-RQ-08 |
| Q-05 | P-09 | APP-D; APP-F | Keep MIMIC exploratory; ask for selection/license/access/ethics authority | D-RQ-09; D-RQ-10 or Defer |
| Q-06 | P-09 | APP-D; APP-F | State that no local/offline model is institutionally approved yet | Assign authority in D-RQ-10 or Defer |
| Q-07 | P-10 | APP-G | Separate calendar-confirmed from Drive-sharing/access-pending | Assign access test and deadline |
| Q-08 | P-10; P-11 | APP-D; APP-G | Ask for official-process verification owner, not transcript-derived policy | D-RQ-10 |
| Q-09 | P-09; P-10 | APP-D; APP-F | Show unfilled Clalit request and prerequisites without implying access | D-RQ-10 or Defer |
| Q-10 | P-10; P-11 | APP-D; APP-G | Request accountable confirmation of meeting, partners, and unclear mechanism | D-RQ-10 or Defer |

## Manifest acceptance checks

- [x] All `19` baseline requirements have a planned checkpoint and evidence anchor.
- [x] All `15` baseline actions have a planned checkpoint and evidence anchor.
- [x] All `10` baseline questions have a planned checkpoint and evidence anchor.
- [x] Every planned slide exists in the final PPTX and PDF.
- [x] Every control is reachable from the final core or appendix.
- [x] Every non-trivial deck assertion has a source note and current claim boundary; the detached manifest machine-binds each unique source path to its current bytes.
- [x] A `VERIFIED` local technical render manifest binds the candidate PPTX/PDF, all 21 PowerPoint-native rendered slides, montage, renderer, and local inspection; this is not Ali review or human rehearsal.
- [ ] Human-reviewed bilingual evidence supports any quotation or named later-turn attribution.
- [ ] Final hashes and automated QA are recorded, but Ali authorization, human rehearsal, delivery, and access tests remain pending.
- [ ] Meeting outcomes and corrections are propagated to the master register and affected artifacts.

The checked boxes certify local package construction, `44/44` reachability, and automated QA only. They do not certify human transcript review, rehearsal, delivery readiness, supervisor acceptance, or requirement closure.
