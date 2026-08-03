# 5 August Supervisor Presentation Rehearsal Record

Status: **AUTOMATED PREFLIGHT PASSED — HUMAN REHEARSAL NOT RUN**

Last updated: 2026-08-03

This is an evidence form, not proof of rehearsal. Complete it only during real review of the exact frozen package identified below. Any edit after the final rehearsal invalidates the result until affected slides are rerendered and rechecked.

## Package under test

| Field | Recorded value |
| --- | --- |
| PPTX path/version/SHA-256 | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx`; v10 local candidate; 21 slides; `7765132B6406796AFE802887A9CC69B9A903843BDCBEC606C517738D91421D24` |
| PDF path/version/SHA-256 | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf`; exact v10 native PowerPoint export; 21 pages; `A8E296911F734477ADD5005BF02C305DFCA4C9E897532DA510A3D629E700F7EC` |
| Notes path/version/SHA-256 | Embedded in the PPTX; 21/21 slides contain a `[Sources]` section; same PPTX hash above |
| Evidence appendix path/version/SHA-256 | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx`; machine-only review interface; `7F72BC625374C225B8C450E6A9EE5F4A6D147988BF35AF3BC54D4F5FC7C3F295` |
| Presentation manifest version/SHA-256 | [current working manifest](./2026-08-05-supervisor-presentation-manifest.md); final document hash belongs in the provenance manifest |
| Repository revision | `NOT FROZEN`; record the committed candidate revision only after human rehearsal corrections and RG-04 |
| Planned meeting duration/language | English 12-slide core; target maximum 11 minutes; appendix on demand; human timing not measured |

## Participants and run metadata

| Role | Name | Attendance/result |
| --- | --- | --- |
| Presenter | Ali Hamed | NOT RUN |
| Iris-role reviewer | `[name]` | NOT RUN |
| Arnon-role reviewer | `[name]` | NOT RUN |
| Recorder/timekeeper | `[name]` | NOT RUN |

- Start time: `NOT RUN`
- End time: `NOT RUN`
- Core duration: `NOT MEASURED`
- Discussion buffer: `NOT MEASURED`
- Run result: `NOT RUN`

## Render and visual QA

| Check | Result | Evidence/notes |
| --- | --- | --- |
| Every slide rendered after final edit | PASS — automated/local | Exact v10 candidate: 21/21 slides exported through PowerPoint at 1440×810, hash-bound in the [render manifest](./2026-08-05-supervisor-render-manifest.json), and locally inspected; montage reviewed |
| Overflow/clipping/overlap | PASS — automated/local | Presentation overflow test: `Test passed. No overflow detected.`; native-render defects found during QA were corrected and rerendered |
| Minimum readable typography | PASS — visual/local | Core and appendix inspected at full size; appendix action rows were split across two slides |
| Contrast, color, and table readability | PASS — visual/local | White/black base with blue, amber, red, and green status accents; all tables readable in PowerPoint-native renders |
| Hebrew right-to-left rendering | NOT APPLICABLE TO DECK | No Hebrew quotation or transcript text is embedded; the external ledger contains machine Hebrew and remains human-review pending |
| Titles, numbering, footers, links | PASS — automated/local | Core `1–12` and appendix `A1–A9` inspected after footer correction; 21/21 source-note sections present |
| PPTX/PDF visual parity | PASS — local | PDF was exported from the exact final PPTX by PowerPoint; both contain 21 pages/slides |
| Offline copy opens correctly | PASS — local only | PowerPoint opened the PPTX read-only and exported both PDF and final slide renders; no external-recipient test performed |

## Content and control QA

| Check | Result | Evidence/notes |
| --- | --- | --- |
| Twelve-slide core matches the controlled sequence | PASS — automated/local | Slides 1–12 implement purpose, progress, RQs, studies, novelty boundary, Plan A/B, literature, evidence, medical gates, timeline, decisions, and closeout |
| All baseline controls reachable through core/appendix | PASS — structure | Appendix contains 19 unique R IDs, 15 unique A IDs, and 10 unique Q IDs |
| Exact umbrella RQ and SQ1–SQ3 synchronized | PASS — exact local text extraction | The four verbatim strings in the v10 PPTX match the decision pack; supervisor approval remains separate. |
| Every result has a permitted claim state | PASS — local claim check | The deck separates established, preliminary, planned, blocked, and partner-dependent statements |
| EXP-005 `0/24`, medical `0/6`, and MIMIC `25/26` shown where relevant | PASS | Slide 8 shows all three boundaries; slide 9 repeats the medical no-go rule |
| No direct unreviewed transcript quotation | PASS — text inspection | No direct quotation is present |
| No unsupported named later-turn attribution | PASS — text inspection | No later-turn instruction is attributed to Iris; cover names identify meeting participants only |
| No restricted row, screenshot, credential, or private contact | PASS — local content review | Package contains aggregate controls and paths only; no patient row or credential is embedded |
| Every decision has a pause/read-back point | PASS — prepared interface | Slide 11 lists mandatory decisions; slide 12 requires read-back; actual outcomes remain `0/10` |
| Closeout has one task, owner, due date, evidence, and definition of done | PASS — prepared interface | Slide 12 contains all required closeout fields; real values must be recorded live |

## Timed rehearsal

Result: **NOT RUN**

| Slide/checkpoint | Planned seconds | Actual seconds | Issue/correction |
| --- | ---: | ---: | --- |
| P-01–P-02 | `[value]` | — | — |
| P-03–P-05 | `[value]` | — | — |
| P-06–P-08 | `[value]` | — | — |
| P-09–P-10 | `[value]` | — | — |
| P-11–P-12 | `[value]` | — | — |

## Adversarial Q&A rehearsal

Result: **NOT RUN**

Test questions must cover doctoral novelty/scale, why exactly three SQs, Plan B viability, absent EXP-005 labels, medical authorization, MIMIC `25/26`, official dates, partner status, literature completeness, and what evidence would change each blocked claim.

Use the prepared [12-question adversarial Q&A worksheet](./2026-08-05-supervisor-adversarial-qa-worksheet.md). Its existence does not change this section from `NOT RUN`.

| Question/topic | Reviewer | Answer evidence/boundary | Correction required |
| --- | --- | --- | --- |
| `[topic]` | `[name]` | `[record]` | `[yes/no and action]` |

## Defects and rerun control

Automated preflight defects closed before this record was updated:

| Defect ID | Severity | Slide/artifact | Required correction | Owner | Status | Rerun evidence |
| --- | --- | --- | --- | --- | --- | --- |
| REH-DEF-01 | High | Slides A2, A4, A6 | Replace unstable native appendix tables with deterministic text-and-grid layouts and shorten the claim-state title | Ali/Codex | CLOSED | 21/21 PowerPoint-native renders inspected after rebuild |
| REH-DEF-02 | Medium | Slide 7 | Shorten the literature title to prevent subtitle overlap | Ali/Codex | CLOSED | Native render clean; overflow test passed |
| REH-DEF-03 | Low | Slide 12 | Widen footer number box so `12` is not clipped | Ali/Codex | CLOSED | Native render displays `12`; overflow test passed |
| REH-DEF-04 | High | Slides A2, A4 and 11 | Rebuild clipped appendix-title runs and the two-digit slide-11 footer in native PowerPoint | Ali/Codex | CLOSED | Direct 1600x900 PowerPoint exports show both complete appendix titles and footer `11`; PDF parity and overflow test passed |
| REH-DEF-05 | Medium | Slide A7 | Qualify alignment as machine-only in the title so it cannot imply bilingual human review | Ali/Codex | CLOSED | Direct 1600x900 PowerPoint export shows “Machine alignment”; review remains visibly `0` |
| REH-DEF-06 | High | Slide 11 | Replace legacy approve/reject outcomes with `Confirm`, `Confirm with correction`, `Retire or supersede`, and `Defer` | Ali/Codex | CLOSED | v9 native render and exact PPTX text extraction show all four canonical outcomes; silence remains `Defer` |
| REH-DEF-07 | Major | Slides 10, 13 | R-04's appendix slide-mapping (`5,10`) disagreed with the presentation manifest (`P-04;P-06;P-10`) and neither slide set showed novelty/scale/feasibility/resources content; added a doctoral-adequacy caption to slide 10 and corrected the appendix mapping to `10` | Ali/Claude | CLOSED | v10 native render shows the caption on slide 10 and `10` in the R-04 appendix row; manifest updated to `P-10` |
| REH-DEF-08 | Minor | Slide 15 | Appendix `Slide` column omitted slide 2 for A-03/A-06 even though the manifest and slide 2 itself both reference them there | Ali/Claude | CLOSED | v10 native render shows `2,7` (A-03) and `2,10` (A-06) |
| REH-DEF-09 | Minor | Slide 18 | The `Verified/Awaiting/Partial/Open/Blocked` vocabulary used throughout the appendix tables and the slide-8 bar chart had no on-deck definition; the `Claim states` slide defined a different five-term vocabulary instead | Ali/Claude | CLOSED | v10 native render shows a control-status legend caption on slide 18 distinguishing the two vocabularies |

- Final rehearsal verdict: `NOT RUN`
- Automated preflight verdict: `PASS`
- Presenter approval: `PENDING`
- Iris-role review approval: `PENDING`
- Arnon-role review approval: `PENDING`
- Recorder/timekeeper approval: `PENDING`

This record may move to `PASS` only when the exact final package passes visual QA, timed rehearsal, adversarial Q&A, and defect reruns.
