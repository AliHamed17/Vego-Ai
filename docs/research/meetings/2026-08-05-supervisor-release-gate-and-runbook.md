# 5 August Supervisor Release Gate and Meeting Runbook

Prepared by: Ali

Meeting: 5 August 2026, 09:00-10:00 Asia/Jerusalem

Status: **CONTROLLED INTERNAL RUNBOOK - NO RELEASE, DELIVERY, ACCESS TEST, REHEARSAL, OR SUPERVISOR OUTCOME IS RECORDED BY THIS FILE**

This runbook controls the exact August 5 supervisor package from Ali's final
review through rehearsal, release, the live decision meeting, and the 24-hour
closeout. It does not replace the existing
[delivery/access record](./2026-08-05-supervisor-delivery-access-record.md),
[rehearsal record](./2026-08-05-supervisor-rehearsal-record.md),
[presentation checklist](./2026-08-05-supervisor-presentation-checklist.md), or
[decision pack](../phd-proposal/2026-08-05-rq-decision-pack.md).

## 1. Binding release rule

The package may be shared only after gates RG-01 through RG-05 pass in order.
Evidence must be recorded against the exact final files and hashes. A prepared
form, a local automated pass, or sender access is not evidence of human review,
delivery, or recipient access.

| Gate | Accountable owner | Required evidence | Current state |
| --- | --- | --- | --- |
| RG-01 - exact-package review | Ali | Ali reviews the exact PPTX, PDF, notes, evidence appendix, pre-read, RQ pack, proposal draft, and workbook rows; claim and restricted-data checks pass | Pending - not recorded |
| RG-02 - timed rehearsal | Ali; named Iris-role and Arnon-role reviewers; timekeeper | Dated four-role rehearsal of the 12-slide core; core duration is no more than 11 minutes; issues and corrections are recorded | Pending - not run |
| RG-03 - adversarial rehearsal | Ali; same or independently named reviewers | The prepared adversarial questions are answered using evidence boundaries; every correction is recorded | Pending - not run |
| RG-04 - final freeze | Ali | Corrections are applied; all slides are rerendered and inspected; PPTX/PDF parity and links pass; final repository revision, time, sizes, and SHA-256 values are recorded | Pending - candidate package is not frozen |
| RG-05 - authorized delivery and access | Ali | Ali authorizes the route and least-privilege permissions; delivery is version-specific; Iris and Arnon independently open the expected files; source/working separation is rechecked | Pending - not shared, delivered, or tested |

Any package edit after RG-02 or RG-03 invalidates the rehearsal evidence. Rerun
the complete preflight, both human rehearsals, the render inspection, and the
hash freeze before release.

## 2. Exact candidate package under control

These are candidate paths, not a released package. The final values belong in
the delivery/access record after RG-04.

| Component | Candidate path or record | Required release state |
| --- | --- | --- |
| Presentation | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx` | Exact final hash recorded; 21 slides; 12-slide core plus appendix |
| PDF | `presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf` | Exact final hash recorded; page count and visual parity checked |
| Presenter notes | Embedded in the PPTX | All slides retain a source section and reviewed presenter notes |
| Evidence appendix | `outputs/iris-closure-2026-08-01/Iris_Zoom_Review_Ledger_2026-07-29.xlsx` | Machine-only/human-review boundary remains explicit |
| Pre-read | [Supervisor pre-read](./2026-08-05-supervisor-pre-read.md) | Ali-approved exact version; not described as sent until delivery evidence exists |
| Decision interface | [RQ decision pack](../phd-proposal/2026-08-05-rq-decision-pack.md) | D-RQ-01 through D-RQ-10 visible and pending before the meeting |
| Package manifest | [Presentation manifest](./2026-08-05-supervisor-presentation-manifest.md) | All current 44 controls remain reachable |
| Offline backup | Path and hash from the delivery/access record | Opens locally; remains separate from delivery evidence |

## 3. Ali exact-package review

Complete before the first human rehearsal.

- [ ] The umbrella RQ and SQ1-SQ3 match the decision pack exactly.
- [ ] Study 1, Study 2, and Study 3 map one-to-one to SQ1, SQ2, and SQ3.
- [ ] Plan A remains a gated medical extension and Plan B remains a complete non-medical path.
- [ ] EXP-005 is shown as `0/24`; no accuracy, effort-reduction, superiority, or generalization claim is present.
- [ ] Medical readiness is shown as `0/6`; no row-level medical work or institutional approval is implied.
- [ ] MIMIC is shown as exploratory `25/26`; no patient-row inspection is implied.
- [ ] No direct machine-derived quotation or uncertain named attribution appears.
- [ ] Literature status says protocol ready and searches not run.
- [ ] September and October dates are labeled working targets pending official confirmation.
- [ ] No restricted row, credential, private contact, or partner commitment appears.
- [ ] The exact package contains the expected source links and opens offline.

Review record:

| Field | Value |
| --- | --- |
| Reviewer | Ali |
| Review date/time and timezone | Pending |
| Candidate revision and hashes | Pending |
| Defects found | Pending |
| Corrections required | Pending |
| Ali approval to enter rehearsal | Pending |

## 4. Rehearsal 1 - timed narrative

Purpose: prove that the English 12-slide core can be delivered clearly in no
more than 11 minutes while preserving pauses for the live decision discussion.

| Field | Required or recorded value |
| --- | --- |
| Presenter | Ali |
| Iris-role reviewer | Pending name |
| Arnon-role reviewer | Pending name |
| Recorder/timekeeper | Pending name |
| Exact PPTX/PDF hashes | Pending |
| Start/end and timezone | Pending |
| Measured core duration | Pending; pass is `<= 11:00` |
| Result | NOT RUN |

Pass checks:

- [ ] The opening states that the meeting record is machine-derived and human review is pending.
- [ ] Completed evidence, planned work, blocked work, and partner-dependent work are separated.
- [ ] Slides 3-4 preserve the exact one-plus-three hierarchy and study map.
- [ ] Slides 8-9 state `0/24`, `0/6`, and `25/26` without qualification drift.
- [ ] The presenter reaches D-RQ-01 through D-RQ-10 with adequate discussion time.
- [ ] The core completes in no more than 11 minutes.
- [ ] Every defect has an owner and correction; the full rehearsal is rerun after any package edit.

## 5. Rehearsal 2 - adversarial decision and Q&A

Use the existing
[adversarial Q&A worksheet](./2026-08-05-supervisor-adversarial-qa-worksheet.md).
The reviewer must challenge at least these boundaries:

1. Why exactly three subquestions and three studies?
2. What is novel, and what remains only a candidate gap?
3. Can Plan B answer every RQ without a medical partner?
4. Why are effectiveness claims blocked at EXP-005 `0/24`?
5. What evidence would justify an effort-reduction or generalization claim?
6. Why does MIMIC `25/26` not establish dataset selection or authorization?
7. Why is medical work NO-GO at `0/6`?
8. Which official candidacy dates and rules remain unverified?
9. What is actually known about partner status and access?
10. What literature work has actually run, versus only being prepared?
11. What exact decision is requested from each supervisor?
12. What single task closes the meeting?

| Field | Value |
| --- | --- |
| Date/time and timezone | Pending |
| Participants | Pending |
| Exact package hashes | Pending |
| Questions completed | `0/12` |
| Defects/corrections | Pending |
| Result | NOT RUN |

Pass requires `12/12` questions addressed with evidence-honest wording, zero
unresolved high-severity defect, and a complete rerun after any package edit.

## 6. August 4 final freeze, delivery, and access form

Target completion: **4 August 2026, 18:00 Asia/Jerusalem**. This is an internal
control target, not evidence that release occurred.

### Freeze

| Field | Recorded value |
| --- | --- |
| Final repository revision | Pending |
| Freeze date/time and timezone | Pending |
| PPTX path, bytes, SHA-256 | Pending |
| PDF path, bytes, SHA-256 | Pending |
| Appendix path, bytes, SHA-256 | Pending |
| Backup path, bytes, SHA-256 | Pending |
| Final render and link check | Pending |
| Ali final release authorization | Pending |

### Delivery

| Field | Recorded value |
| --- | --- |
| Authorized sender | Pending |
| Authorized route | Pending |
| Recipient list | Pending |
| Permission level per recipient | Pending |
| Delivery time and timezone | NOT DELIVERED |
| Delivered version/hash | NOT DELIVERED |
| Receipt or message ID | NOT DELIVERED |

### Independent recipient access tests

| Recipient | Link opens | Expected files visible | Permission correct | Test time | Evidence |
| --- | --- | --- | --- | --- | --- |
| Iris Reinhartz-Berger | Not tested | Not tested | Not tested | Pending | Pending |
| Arnon Sturm | Not tested | Not tested | Not tested | Pending | Pending |

Before RG-05 passes, verify that the Ali-owned working area remains separate
from the viewer/read-only MIMIC source folder and that no restricted data has
entered the released package.

## 7. August 5 60-minute run of show

Ali is the presenter and recorder unless a separate recorder is named. Iris and
Arnon are the academic decision authorities. Silence is recorded as `Defer`,
never as approval.

| Time | Minutes | Activity | Decision/evidence output |
| --- | ---: | --- | --- |
| 09:00-09:04 | 4 | Open, purpose, machine-record caveat, and desired outcome | Confirm agenda and decision vocabulary |
| 09:04-09:10 | 6 | Evidence-backed progress since July 29 | Separate local completion from human/external gates |
| 09:10-09:20 | 10 | Umbrella RQ, exactly three SQs, and study mapping | D-RQ-01, D-RQ-02, D-RQ-03 |
| 09:20-09:30 | 10 | Plan A, Plan B, answerability, and August 26 fallback | D-RQ-04, D-RQ-05, D-RQ-06 |
| 09:30-09:36 | 6 | Current claim boundary and preliminary evidence | D-RQ-07; retain `0/24` |
| 09:36-09:43 | 7 | Literature taxonomy and execution protocol | D-RQ-08; distinguish ready protocol from unrun searches |
| 09:43-09:49 | 6 | MIMIC boundary and medical readiness | D-RQ-09; retain `25/26`, `0/6`, and no-row rule |
| 09:49-09:54 | 5 | Medical, partner, Penina, and university-process ownership | D-RQ-10 plus named owners/deadlines |
| 09:54-09:58 | 4 | Exact decision read-back | Correct wording, rationale, owner, due date, affected artifacts |
| 09:58-10:00 | 2 | Close with exactly one primary next task | Task, owner, due date/timezone, definition of done, evidence, dependency, fallback |

Mandatory live outcomes are D-RQ-01 through D-RQ-05 and D-RQ-07. Any other
deferred decision must have a named owner and written-response deadline.

## 8. D-RQ outcome capture

Allowed meeting outcomes are `Confirm`, `Confirm with correction`, `Retire or
supersede`, or `Defer`. A correction or supersession must preserve the exact
replacement wording and rationale. A rejection
must identify the required resolution or superseding decision.

| ID | Decision | Iris outcome/correction | Arnon outcome/correction | Rationale | Owner/deadline | Affected artifacts |
| --- | --- | --- | --- | --- | --- | --- |
| D-RQ-01 | Umbrella-RQ wording | Pending | Pending | Pending | Pending | RQ pack, proposal, deck, master views |
| D-RQ-02 | Exactly SQ1-SQ3 | Pending | Pending | Pending | Pending | RQ pack, proposal, study contract |
| D-RQ-03 | Three-study mapping | Pending | Pending | Pending | Pending | Study contract, proposal, methods |
| D-RQ-04 | Plan A/Plan B interpretation | Pending | Pending | Pending | Pending | Proposal, RAID, timeline |
| D-RQ-05 | All questions answerable under Plan B | Pending | Pending | Pending | Pending | RQs, Study 3, fallback resources |
| D-RQ-06 | August 26 fallback checkpoint | Pending | Pending | Pending | Pending | RAID, schedule, decision log |
| D-RQ-07 | Evidence-boundary wording | Pending | Pending | Pending | Pending | Claim register, proposal, presentation |
| D-RQ-08 | Literature scope and method | Pending | Pending | Pending | Pending | Search register, workbook, proposal |
| D-RQ-09 | Metadata/schema-only MIMIC boundary | Pending | Pending | Pending | Pending | Medical audit, proposal, scorecard |
| D-RQ-10 | Medical and university-process owners | Pending | Pending | Pending | Pending | RACI/RAID, inquiry, medical gates |

## 9. One-task closeout

| Field | Recorded value |
| --- | --- |
| Primary task | Pending live decision |
| Owner | Pending |
| Due date/time and timezone | Pending |
| Definition of done | Pending |
| Evidence expected | Pending |
| Dependencies | Pending |
| Fallback if blocked | Pending |

## 10. Within 24 hours after the meeting

Ali owns the closeout unless the meeting explicitly assigns another owner.

1. Produce evidence-linked minutes and send them only after Ali reviews the exact text.
2. Request written confirmation or correction from Iris and Arnon; silence remains `Defer`.
3. Record decisions in the decision/change log with exact wording and affected artifacts.
4. Propagate approved changes to the RQ pack, study contract, proposal, claims, schedule, presentation, and derived views.
5. Mark superseded wording; do not silently delete history.
6. Rerun structure and readiness validation and report every human/external gate that remains non-zero.
7. Archive the exact presented package only after Ali reviews and authorizes the archive record.
8. Record the next weekly commitment and its evidence check.

The meeting closes decisions; it does not by itself complete transcript
adjudication, literature execution, EXP-005, medical readiness, university
verification, proposal approval, or submission.
