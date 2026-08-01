# Iris Requirements Next-Step Implementation Manifest

Date: 1 August 2026

Status: **LOCAL IMPLEMENTATION TRANCHE COMPLETE; HUMAN AND EXTERNAL RELEASE GATES REMAIN OPEN**

This manifest records the automatable implementation completed for the
August 1-October 7 execution plan. It does not record human review, rehearsal,
supervisor acceptance, delivery, recipient access, expert labels, medical
authorization, proposal approval, or submission.

## 1. Authoritative execution interfaces

| Interface | Purpose | Current defensible state |
| --- | --- | --- |
| [Canonical execution board](./aug1-oct7-execution-control-board.json) and [operator guide](./aug1-oct7-execution-control-board.md) | Machine-readable dependency program, roles, evidence, acceptance checks, and fail-closed gates | Structure-valid; 29 packages currently comprise 18 blocked, 6 partial, and 5 planned packages; exact 44-control, 10 Iris-assurance, and 10 canonical-experiment denominators are enforced |
| [Execution-control workbook](../../../outputs/iris-next-step-2026-08-01-implementation/VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx) | Human-readable lead view of the program, with 16 aggregated work packages, role assignments, schedule, decisions, review batches, literature execution, medical gates, and acceptance tests | Generated and visually inspected; this companion view does not replace the canonical JSON board |
| [Supervisor release gate and runbook](../meetings/2026-08-05-supervisor-release-gate-and-runbook.md) | Ali review, rehearsals, freeze, authorized delivery, live decisions, and 24-hour propagation | Controlled template; RG-01 through RG-05 remain pending |
| [Zoom reviewer operations](../meetings/2026-07-29-iris-zoom-reviewer-operations.md) | Independent A/B review, calibration, priority ranges, full-media evidence, adjudication, and merge rules | Operational method complete; Reviewer A/B work remains unstarted |
| [Literature-search execution register](./literature-search-execution-register.md) | Frozen QL-01 through QL-05 queries and per-database execution evidence | Protocol ready; no database search or screening result is claimed |
| [Proposal v0.2 working draft](./proposal-v0.2-working-draft.md) | Developed proposal delta with explicit decisions and evidence boundaries | Working draft only; not approved, shared, or submission-ready |
| [University-process inquiry draft](./university-process-inquiry-draft.md) | Authoritative candidacy and submission questions | Draft only; not sent and no recipient is selected |

## 2. Generated workbook control

Workbook:
`outputs/iris-next-step-2026-08-01-implementation/VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx`

- SHA-256: `4A8AA5F7312AD45940BA5FA504496A5E6326EF2AC7C49395AC1E115011720EB6`
- Size: `26,564` bytes.
- Sheets: `Executive`, `Work_Packages`, `Role_Assignments`, `Schedule`,
  `Decision_Log`, `Human_Review`, `Literature_Search`, `Medical_Gates`,
  `Acceptance_Tests`, and `Controlled_Lists`.
- Formula/error inspection: zero matching formula-error cells.
- Visual inspection: all ten rendered sheets inspected.
- Traceability check: all `19` requirement IDs, `15` action IDs, and `10`
  question IDs appear across the executable work-package controls.
- Correction made during QA: schedule values were converted to explicit
  Asia/Jerusalem text so the 5 August meeting displays `09:00` instead of a
  UTC-shifted value.
- Evidence boundary: blank assignee, approver, access, result, and receipt
  cells are intentional human/external gates, not missing generated data.

## 3. Presentation correction and QA

Candidate deck:
`presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx`

- SHA-256: `35D351A2609AD354CAE3078A6ABDFEDA6837248B399A4A54DB725FE487D7686F`.
- Size: `100,216` bytes.
- Count: 21 slides, with a 12-slide core and 9-slide appendix.
- Automated padded-canvas overflow test: pass.
- Visual inspection: all 21 slides inspected.
- Defects found and corrected: the title runs on appendix slides 14 and 16
  clipped inconsistently in native rendering, and the slide 11 footer showed
  only one digit. The titles and footer were rebuilt and normalized in native
  PowerPoint, then exported directly for inspection. Slide 19 was also
  tightened to say explicitly that only machine alignment is complete.
- Native Microsoft PowerPoint PDF render was used to confirm both corrected
  appendix titles. The local PDF has SHA-256
  `F1FEFAD1F87E36F3A0823DE01C50F2C02D26D1B62ED2BB87768CC43CD2C12FF1` and
  size `332,495` bytes.
- Human timed rehearsal, adversarial rehearsal, Ali release approval, delivery,
  and Iris/Arnon access remain unrecorded and therefore blocked.

## 4. Validation interfaces added

| Validator | Purpose | Honest current result |
| --- | --- | --- |
| [`validate_aug1_oct7_execution_program.py`](../../../scripts/validate_aug1_oct7_execution_program.py) | Validates board structure, typed dependencies, evidence kinds/approver roles, readiness, and closure without creating evidence | Structure passes; readiness and closure fail while required evidence is pending |
| [`validate_iris_zoom_review_batches.py`](../../../scripts/validate_iris_zoom_review_batches.py) | Validates partial or complete independent reviewer returns and identities | Header-only templates are valid partial inputs; complete mode remains non-zero |
| Existing Iris closure validator | Validates the synchronized 44-control package | Structure remains expected to pass; readiness and closure remain non-zero until human/external gates close |

IRIS-EXP-08 additionally rejects the current offline ZIP: the status records
mark it stale and the ZIP member hashes do not match the corrected PPTX/PDF.
A filename or an outer ZIP hash alone cannot satisfy package readiness.

Focused tests cover board schemas and dependencies, fail-closed mode behavior,
reviewer batch schemas, ID ordering, independence, completeness, and invalid
input handling.

## 5. What remains blocked

The implementation does not change the evidence denominators:

- supervisor acceptance remains `0/19`;
- research decisions remain `0/10`;
- dual transcript review remains `0/1,195` for each reviewer;
- EXP-005 safe labels remain `0/24`;
- medical readiness remains `0/6`;
- recipient access remains untested;
- literature searches and screening remain not run;
- the university inquiry remains not sent;
- no proposal approval or authorized submission receipt exists.

No restricted patient row was inspected or copied. No external message,
Drive share, permission change, partner request, or submission was made.

## 6. Immediate human handoff

1. Ali reviews the exact candidate package and records RG-01.
2. Ali names Reviewer B, the bilingual adjudicator, the two rehearsal-role
   reviewers, the recorder/timekeeper, EXP reviewers/adjudicator, university
   inquiry owner, and Plan B replication owner.
3. The named team runs both complete rehearsals; every deck correction then
   triggers a new render, inspection, hash, and rehearsal cycle.
4. Only after Ali authorizes the exact version are delivery and recipient
   access tests performed.
5. The 5 August meeting records explicit D-RQ outcomes; silence is `Defer`.
6. Human call review and literature execution continue to the 12 August
   evidence target without being represented as already completed.
