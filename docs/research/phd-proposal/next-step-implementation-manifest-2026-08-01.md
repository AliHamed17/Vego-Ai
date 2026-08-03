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
| [Execution-control workbook](../../../outputs/iris-next-step-2026-08-01-implementation/VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx) | Human-readable lead view of the program, with all 29 canonical work packages, the dynamic 44-control acceptance register, experiment crosswalk, all 19 roles, schedule, decisions, review batches, literature execution, medical gates, and acceptance tests | Generated from tracked sources and visually inspected; no conflicting aggregate work-package namespace remains, and this companion view does not replace the canonical JSON board |
| [Supervisor release gate and runbook](../meetings/2026-08-05-supervisor-release-gate-and-runbook.md) | Ali review, rehearsals, freeze, authorized delivery, live decisions, and 24-hour propagation | Controlled template; RG-01 through RG-05 remain pending |
| [Zoom reviewer operations](../meetings/2026-07-29-iris-zoom-reviewer-operations.md) | Independent A/B review, calibration, priority ranges, full-media evidence, adjudication, and merge rules | Operational method complete; Reviewer A/B work remains unstarted |
| [Literature-search execution register](./literature-search-execution-register.md) | Frozen QL-01 through QL-05 queries and per-database execution evidence | Protocol ready; no database search or screening result is claimed |
| [Proposal v0.2 working draft](./proposal-v0.2-working-draft.md) | Developed proposal delta with explicit decisions and evidence boundaries | Working draft only; not approved, shared, or submission-ready |
| [University-process inquiry draft](./university-process-inquiry-draft.md) | Authoritative candidacy and submission questions | Draft only; not sent and no recipient is selected |

## 2. Generated workbook control

Workbook:
`outputs/iris-next-step-2026-08-01-implementation/VEGO-AI-Iris-Next-Step-Execution-Control-2026-08-01.xlsx`

- Builder: [`build_iris_execution_control_workbook.mjs`](../../../scripts/build_iris_execution_control_workbook.mjs).
- SHA-256: `6FF4A5E3CAD7108ECC2E4C087972A9BBC252379A82DB3B1584294109741E521E`.
- Size: `82,512` bytes.
- Sheets: `Executive`, `Work_Packages`, `Control_Acceptance`,
  `Experiment_Crosswalk`, `Role_Assignments`, `Schedule`, `Decision_Log`,
  `Human_Review`, `Literature_Search`, `Medical_Gates`, `Acceptance_Tests`,
  and `Controlled_Lists`.
- Formula/error inspection: `134` formula cells and zero matching
  formula-error values after native Excel recalculation.
- Visual inspection: all `12` sheets were rendered and inspected at full
  resolution; no overlap or clipping defect was observed.
- Canonical coverage: `29/29` work packages, `44/44` controls (`19` R, `15` A,
  `10` Q), `19/19` roles, `10/10` Iris-assurance experiments, `10/10`
  canonical scientific experiments, and `6/6` proposal-only SCI aliases.
- Call-review scheduling coverage: the 16 priority/remainder batches cover
  `S-0001` through `S-1195` exactly once, with zero gaps or duplicates. This
  is a work-allocation check, not evidence that any human review occurred.
- The dynamic acceptance sheet initializes all 44 final states to `Pending`;
  closure remains `0/44`, and newly discovered stable controls increase the
  denominator instead of being hidden.
- Due values are real Excel date/time cells. `Asia/Jerusalem` remains a
  separate visible timezone field, and overdue state is formula-driven from
  `NOW()` without treating working targets as authoritative deadlines.
- All data sheets have Excel tables/filters, every sheet has persisted freeze
  panes, and all eight controlled-list inputs use visible STOP error alerts.
- Evidence boundary: blank assignee, approver, access, result, and receipt
  cells are intentional human/external gates, not missing generated data.

## 3. Presentation correction and QA

Candidate deck:
`presentations/VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx`

- SHA-256: `4233EEA0AD7FCF3FF183A0FCDAEA7C80FD797262B92F307D8CD15EEC4EF256A1`.
- Size: `100,686` bytes.
- Count: 21 slides, with a 12-slide core and 9-slide appendix.
- Automated padded-canvas overflow test: pass.
- Visual inspection: all 21 slides inspected.
- Defects found and corrected: the title runs on appendix slides 14 and 16
  clipped inconsistently in native rendering, and the slide 11 footer showed
  only one digit. The titles and footer were rebuilt and normalized in native
  PowerPoint, then exported directly for inspection. Slide 19 was also
  tightened to say explicitly that only machine alignment is complete. The
  3 August v9 freeze also synchronizes the four verbatim canonical RQ strings,
  the staged medical fallback, ASR internal-gap boundary, scientific
  experiment crosswalk, and the `Confirm`/correction/supersede/defer decision
  vocabulary.
- Native Microsoft PowerPoint PDF render was used to confirm both corrected
  appendix titles. The local PDF has SHA-256
  `50D9F116AA46DED88A67E0F1147FB9FCD3612CE2CCF0130BCDFFB0F0C64AF175` and
  size `333,836` bytes.
- Human timed rehearsal, adversarial rehearsal, Ali release approval, delivery,
  and Iris/Arnon access remain unrecorded and therefore blocked.

## 4. Validation interfaces added

| Validator | Purpose | Honest current result |
| --- | --- | --- |
| [`validate_aug1_oct7_execution_program.py`](../../../scripts/validate_aug1_oct7_execution_program.py) | Validates board structure, typed dependencies, evidence kinds/approver roles, readiness, and closure without creating evidence | Structure passes; readiness and closure fail while required evidence is pending |
| [`validate_iris_zoom_review_batches.py`](../../../scripts/validate_iris_zoom_review_batches.py) | Validates partial or complete independent reviewer returns and identities | Header-only templates are valid partial inputs; complete mode remains non-zero |
| Existing Iris closure validator | Validates the synchronized 44-control package | Latest integrated `--all --mode structure` run remains non-zero for the separately tracked IRIS-EXP-03 wording alignment and IRIS-EXP-07 provenance/revision reconciliation; readiness and closure also remain non-zero until human/external gates close |

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
