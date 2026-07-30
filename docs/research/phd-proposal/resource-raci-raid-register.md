# PhD Proposal Resource, RACI, and RAID Register

Last updated: 2026-07-30
Status: Internal execution control; named external roles, permissions, and dates remain unverified unless linked evidence is recorded.

Verified implementation snapshot:

- Working branch: `docs/iris-july29-phd-execution`.
- Meeting-evidence baseline commit: `3d0beca`.
- Private Ali-owned Drive root: [VEGO-AI PhD workspace](https://drive.google.com/drive/folders/1Och2Vlux87uqk6QZy0F4xr2WhfzY_cd-) with nine specified subfolders; not shared externally.
- Literature workbook: [native Google Sheet](https://docs.google.com/spreadsheets/d/1tVAM10bxlmL7_8SbgDgN5BRfAR2f5Q4pGvQmx-Ypp4A/edit) in `03_Literature_Review`.
- Recurring VEGO calendar series: accepted by Ali, Iris, and Arnon.

## Non-negotiable Plan A checkpoint

Plan A is the medical-enabled evaluation path. Plan B is the protected non-medical path.

At **2026-08-26 23:59 Asia/Jerusalem**, the six medical entry gates **G1–G6** must each have a documented owner, evidence path, and feasible date. If any gate lacks one of those controls:

1. Plan B becomes the active execution baseline automatically on 2026-08-27.
2. Proposal drafting, literature work, and Studies 1–2 continue without delay.
3. Study 3 uses the non-medical replication contract.
4. Plan A moves to `Partner-dependent future option`; it is not described as committed.
5. No extra meeting or approval is required to activate Plan B.
6. Plan A can reopen only through a logged supervisor decision, completion of G1–G6, the required downstream controls, governance approval, and an explicit schedule-impact review.

This is an internal project-control date, not a date attributed to the July 29 meeting and not a formal university deadline.

Silence, expected access, a shared-folder link, a verbal expression of interest, or a meeting invitation does not satisfy a readiness gate.

## RACI definitions and roles

| Code | Meaning |
| --- | --- |
| R | Responsible for producing the work and evidence. |
| A | Accountable for accepting the result or authorizing the decision. |
| C | Consulted before the result is finalized. |
| I | Informed of status or outcome. |

| Role key | Role | Current state | Authority or responsibility |
| --- | --- | --- | --- |
| ALI | Ali, research lead/student | Filled | Proposal drafting, literature work, evidence traceability, execution coordination, weekly pre-read. |
| IRIS | Iris, supervisor and medical-partner sponsor | Filled | Academic direction, proposal review, medical/partner coordination, meeting cadence. |
| ARNON | Arnon, supervisor/methodological reviewer | Filled | Research design, question/study review, evidence/claim boundary, feasibility review. |
| CLIN | Named clinical lead | **Unfilled** | Medical use-case ownership, clinical validity, reviewer recruitment, safety boundary. |
| CREV | Clinical reviewers/domain experts | **Unfilled** | Independent domain review and adjudication for any medical study. |
| DGO | Data controller/privacy/security authority | **Unfilled** | Data-purpose approval, license/access, privacy/security, storage, export, retention, incident rules. |
| ETH | Ethics/IRB/legal authority | **Unfilled** | Formal determination or approval for proposed dataset, participants, and study. |
| VDI | VDI/local-model technical owner | **Unfilled** | Approved compute, network isolation, model/runtime installation, access/logging, operational evidence. |
| PART | Clalit or other medical partner decision owner | **Unfilled/unconfirmed** | Written collaboration, access, data, people, schedule, and environment commitments. |
| R1/R2 | Independent software/modeling reviewers | **Unfilled** | Blind EXP-005 and later evaluation labels. |
| ADJ | Adjudicator | **Unfilled** | Resolves reviewer disagreement without contaminating blind review. |
| EXT | External non-medical replication owner/panel | **Unfilled** | Plan B independent corpus, setting, and reviewers. |
| GRAD | Graduate Studies/Sigal/authorized university contact | **Unconfirmed contact path** | Official candidacy dates, committee/reviewer rules, submission process. |
| DRIVE | Shared Drive/source owner | Ali owns the private working root; MIMIC/source owner remains **unverified** | Ali controls working-root sharing; source owner controls viewer-only source protection and source permissions. |

## RACI matrix

| Workstream or decision | ALI | IRIS | ARNON | CLIN/CREV | DGO/ETH | VDI | PART | R1/R2/ADJ or EXT | GRAD/DRIVE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Master traceability, claim, and RAID controls | R | A | C | I | I | I | I | I | I |
| Umbrella RQ, SQ1–SQ3, and three-study contract | R | A | A | C for Plan A | C | I | I | C for feasibility | I |
| Full proposal drafting and integration | R | A | A | C for clinical wording | C for governance wording | C for infrastructure wording | I | C for study feasibility | C for formal process |
| Literature protocol, Excel matrix, and Penina reuse | R | A | C | C for medical corpus | I | I | I | I | I |
| Study 1 selective-intervention architecture | R | A | A | C if medically stress-tested | I | I | I | C for scenario/requirements review | I |
| Study 2 governed knowledge-reuse lifecycle | R | A | A | I | C for consent/privacy | I | I | C when real judgment records are evaluated | I |
| EXP-005 claim-gate decision | R | A | A | I | C | I | I | R for independent evidence | I |
| Plan A readiness and medical-route decision | R | A | A | R/C | A | R | A | I | I |
| MIMIC bounded familiarization | R | A | C | C | A | C | I | I | DRIVE informed |
| Clalit use-case brief and partner meeting | R | A | C | C | C | C | A | I | I |
| Study 3 evaluation/transfer and Plan B external non-medical setting | R | A | A | I | C as applicable | I | I | R for labels/adjudication or external evidence | I |
| Restricted-data/local-LLM operating approval | C | I | I | C | A | R | C | I | I |
| Shared source/working-folder separation | R | A | I | I | C | I | I | I | DRIVE A/R |
| Official candidacy process and deadlines | R | C | C | I | I | I | I | I | GRAD A |
| Weekly meeting pre-read and one-task closeout | R | A | C | I as needed | I as needed | I as needed | I as needed | I as needed | I |
| Candidacy presentation | R | A | A | C if Plan A active | C | I | I | I | GRAD C |
| Proposal/deck claim-release check | R | A | A | C for clinical claims | A for data/governance claims | C | C for partner claims | C for empirical claims | C for formal-date claims |

## Resource readiness register

| Resource ID | Resource | Needed for | Current evidence/state | Owner | Readiness check | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RES-01 | Existing VEGO-AI baseline and software/modeling artifacts | Studies 1–3, preliminary results | Repository and thesis artifacts exist. | ALI | Exact version, provenance, and claim scope are cited. | Available; exact proposal snapshot pending |
| RES-02 | M1–M4B-1/H-layer research artifacts | Studies 1–2 | Implemented/planned mechanism documentation exists. | ALI | Current artifact inventory and evidence boundary pass review. | Available with claim limits |
| RES-03 | EXP-005 human labels | Study 3 evaluation claims | **0/24 independent generalization-safe labels.** | R1/R2/ADJ unfilled | Two reviewers calibrated; 24 rows labeled; disagreement adjudicated; leakage checks pass. | Missing; claim gate blocked |
| RES-04 | Literature-review protocol | R-14–R-16, Penina, novelty | `Search_Log` protocol is ready in the native Sheet; searches have not been executed. | ALI | Search sources, queries, dates, inclusion/exclusion, deduplication, quality, screening, and synthesis are executed and documented. | Partial: protocol ready; execution open |
| RES-05 | Excel/native literature matrix | Next meeting, living literature resource | [Native Google Sheet](https://docs.google.com/spreadsheets/d/1tVAM10bxlmL7_8SbgDgN5BRfAR2f5Q4pGvQmx-Ypp4A/edit) in `03_Literature_Review`: six tabs, five native tables/dropdowns, six seeded paper rows. | ALI | Required three field groups, row-level source validation, final taxonomy/data dictionary, ongoing screening, and author/researcher separation pass review. | Initial tranche implemented; ongoing |
| RES-06 | Penina course deliverables | R-19 and proposal literature reuse | Task exists; presentation/written survey not evidenced complete. | ALI | Official due date, completed deliverables, and proposal reuse map are recorded. | Missing/open |
| RES-07 | Shared PhD working folder | Collaboration and artifact exchange | [Private Ali-owned Drive root](https://drive.google.com/drive/folders/1Och2Vlux87uqk6QZy0F4xr2WhfzY_cd-) with all nine specified subfolders; not shared externally. | ALI/DRIVE | Ali approves contents/permissions; Iris and Arnon pass access tests; source folder is viewer/read-only; working area stays separate. | Private structure implemented; sharing/access pending |
| RES-08 | MIMIC source/index/schema resources | Bounded familiarization only | Viewer resources reported/shared; usage authorization unresolved. | DRIVE/DGO | Inventory, owner, license, purpose, permitted users/actions, and storage rules are written. | Viewer access reported; use unverified |
| RES-09 | Named clinical use case and field | Plan A Study 3 | No final field/use case selected. | CLIN/PART/IRIS | One-page approved use case identifies user, workflow, input, output, human authority, exclusions, and evaluation goal. | Missing |
| RES-10 | Named clinician lead and reviewer panel | Plan A | No evidenced named clinical lead/reviewers. | IRIS/PART | Names, roles, availability, independence/adjudication, and written participation confirmation exist. | Missing |
| RES-11 | Medical partner commitment | Plan A | Discussion only; no finalized commitment/access evidence. | PART/IRIS | Signed or written commitment covers people, data, environment, schedule, and responsibilities. | Partner-dependent |
| RES-12 | Data license/purpose/access authorization | Plan A/MIMIC/Clalit | Not evidenced. | DGO/PART | Authoritative written decision states allowed purpose, users, storage, processing, exports, retention, and publication. | Missing |
| RES-13 | Ethics/privacy/legal determination | Plan A | Existing repo ethics file does not cover the proposed clinical work. | ETH/DGO | Protocol/dataset-specific determination or approval is recorded with identifier, dates, and conditions. | Missing |
| RES-14 | Approved VDI environment | Restricted Plan A work | Mentioned in meeting; operational approval/configuration evidence absent. | VDI/DGO | Named environment, access list, network controls, storage, logging, backup, incident response, and verification evidence exist. | Missing/unverified |
| RES-15 | Approved local/offline LLM runtime | Restricted Plan A work | No institutionally approved model/runtime recorded. | VDI/DGO | Named model/runtime approved in writing and verified with prohibited connectivity disabled. | Missing |
| RES-16 | Medical data contract and study protocol | Plan A | Candidate questions exist; no approved protocol. | ALI/CLIN/DGO/ETH | Minimum data, schema/version, temporal context, labels, metrics, exclusions, stop rules, and authority are approved. | Missing |
| RES-17 | Independent non-medical corpus/context | Plan B Study 3 | Existing baseline available; second independent context not selected. | ALI/EXT | Authorized corpus/setting and independent reviewer plan are recorded with provenance and schedule. | Open; selection required |
| RES-18 | Formal university process/deadline evidence | R-05, R-18, submission | Transcript guidance only. | GRAD | Written authoritative response covers date, reviewers, nomination, committee, presentation, and submission route. | Missing/open |
| RES-19 | Confirmed weekly calendar recurrence | R-13 | Recurring VEGO series accepted by Ali, Iris, and Arnon. | IRIS/ALI | Maintain visible recurrence and capture each meeting’s task/decision read-back. | Available/confirmed |
| RES-20 | Proposal writing capacity and milestone buffer | September/October targets | Ali owns work; exact review turnaround and university deadline unknown. | ALI/IRIS/ARNON | Weekly capacity, review turnaround assumptions, critical path, and buffer are accepted. | Partial |

## Plan A six-gate readiness contract

| Gate | Required control/evidence | Accountable owner | Checkpoint role | Current status |
| --- | --- | --- | --- | --- |
| G1 — use-case | Precise clinical workflow, problem owner, unit of analysis, intended input/output, current baseline, non-goals, and measurable success/failure criteria. | IRIS + CLIN/PART + ALI | Owner, evidence path, and feasible completion date required by 2026-08-26. | Blocked/open |
| G2 — people | Named clinician/domain expert, data custodian, privacy/ethics owner, VDI administrator, supervisor, methods reviewer, responsibilities, availability, and escalation route. | IRIS + PART; institutional owners | Owner, role acceptance, evidence path, and feasible completion date required by 2026-08-26. | Blocked/open |
| G3 — authorization | Individual project-specific permission for every researcher, including exact data source, approved purpose, training/DUA or partner authority, least privilege, and expiry. | DGO/PART | Authoritative evidence path and feasible completion date required by 2026-08-26. Shared-folder visibility is not evidence. | Blocked/open |
| G4 — ethics/privacy | Written project determination covering MIMIC/Clalit use, derivatives, retention, publication, disclosure, and incident handling. | ETH/DGO/PART | Named approver, evidence path, and feasible completion date required by 2026-08-26. | Blocked/open |
| G5 — environment | Approved VDI, storage, compute, logging, egress controls, offline/no-telemetry tools, and explicit local-LLM approval or no-LLM decision. | VDI/DGO | Owner, control evidence, tool decision, and feasible completion date required by 2026-08-26. | Blocked/open |
| G6 — protocol | Approved cohort, inclusion/exclusion, outcome, case/activity/timestamp mapping, missingness, leakage controls, statistics, stop rules, and supervisor/clinical/methods review. | IRIS + ARNON + CLIN + methods reviewer | Exact version, approvals, evidence path, and feasible completion date required by 2026-08-26. | Blocked/open |

Current checkpoint forecast: **Plan B default is expected unless G1–G6 each has the required owner, evidence path, and feasible completion date by the checkpoint.** Passing all six gates is necessary but not sufficient for a pilot or export; the scorecard's downstream integrity, pilot, and disclosure controls still apply.

## Plan B activation checklist

When the automatic fallback fires:

1. record `Plan B active` in the supervisor decision/change log;
2. keep the domain-neutral RQ and SQ1–SQ3 unchanged;
3. mark medical work `Partner-dependent future option`;
4. remove medical access from the proposal critical path;
5. select the independent software/modeling replication context and owner;
6. preserve Studies 1–2 and all evidence gates;
7. update schedule, resource plan, Study 3 publication target, and risk register; and
8. retain the Plan A readiness evidence for possible later reopening without implying commitment.

## RAID register

| ID | Type | Description | Probability / impact | Owner | Mitigation or action | Trigger / due | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | Risk | Medical partner, clinicians, data, permissions, or infrastructure do not materialize in time. | High / High | IRIS; external owners unfilled | Keep questions domain-neutral; run the mandatory readiness review; activate Plan B automatically. | Any G1–G6 gate lacks owner, evidence path, or feasible completion date on 2026-08-26 | Open; controlled by fallback |
| RSK-02 | Risk | Medical familiarization becomes a domain-learning rabbit hole and delays the proposal. | Medium / High | ALI | Metadata/schema-first time box; record unknowns; stop without analysis or full download. | Sanity check exceeds agreed time or moves beyond shape/gap assessment | Open |
| RSK-03 | Risk | Software/modeling metrics are misrepresented as medical evidence or as validated improvement. | Medium / High | ALI; IRIS/ARNON accountable | Binding claim register and pre-release claim audit. | Any unsupported comparative/medical sentence | Open |
| RSK-04 | Risk | EXP-005 implementation readiness is confused with empirical benefit. | High / High | ALI | Keep 0/24 visible; block accuracy/generalization/workload claims until the human gate passes. | Any positive effectiveness claim before accepted labels | Active blocker |
| RSK-05 | Risk | Restricted or patient data is copied from source/VDI into Git, general Drive, or an online model. | Low / Critical | DGO/VDI unfilled | Fail closed; viewer-only source; approved environment; access/logging; no online endpoints. | Any proposed copy/export/model call without written approval | Open; zero tolerance |
| RSK-06 | Risk | Literature review is too broad, unsystematic, or unable to support novelty. | Medium / High | ALI | Lock protocol, taxonomy, matrix, quality criteria, and gap-to-contribution synthesis; weekly bounded batches. | Search expands without protocol or synthesis progress | Open |
| RSK-07 | Risk | Authors’ conclusions and researcher interpretation are mixed. | Medium / Medium | ALI | Separate workbook fields and audit sampled rows. | Any row lacks source/interpretation separation | Open |
| RSK-08 | Risk | Machine-ASR/translation or uncertain speaker attribution becomes a false requirement or quotation. | Medium / High | ALI; supervisors confirm | Preserve raw artifacts; bilingual correction log; no direct English quotes before review. | Requirement disputed or direct quotation proposed | Open |
| RSK-09 | Risk | Multiple “active” legacy plans create conflicting priorities and dates. | High / High | ALI; IRIS accountable | Use the master traceability register and three-study contract as proposal controls; log supersession/absorption explicitly. | Conflicting task/date/RQ appears | Open |
| RSK-10 | Risk | Formal university dates differ from September/early-October working targets. | Medium / High | GRAD; ALI | Confirm policy early; keep internal buffer; log schedule change. | Authoritative response differs from assumptions | Open |
| RSK-11 | Risk | Reviewer or adjudicator availability delays EXP-005 and Study 3 evaluation. | High / High | IRIS/ARNON; R1/R2/ADJ unfilled | Nominate roles, calibrate, estimate effort, protect blind/holdout process; keep mechanism claims bounded if delayed. | Roles not filled by study start | Open |
| RSK-12 | Risk | Weekly meetings become status-only and do not advance writing. | Medium / Medium | ALI/IRIS | Pre-read requires evidence, proposal delta, one next task, and decision read-back. | Meeting closes without one accepted task and due date | Open |
| RSK-13 | Risk | Plan A reopens after fallback and silently displaces Plan B milestones. | Medium / High | IRIS/ARNON | Require completed G1–G6, downstream controls as applicable, a logged decision, and schedule-impact review; no silent replacement. | New partner/access evidence after 2026-08-26 | Controlled |
| RSK-14 | Risk | Penina work and proposal literature work diverge or duplicate effort. | Medium / Medium | ALI | One corpus/matrix; explicit reuse map; different deliverable narratives with common provenance. | Separate unlinked source lists appear | Open |
| ASM-01 | Assumption | September draft and early-October submission are working targets, not verified formal deadlines. | — | ALI/GRAD | Verify through A-14; label dates correctly until then. | Before formal schedule lock | Open assumption |
| ASM-02 | Assumption | Wednesday 09:00 is the intended weekly slot. | — | IRIS/ALI | Confirm calendar and timezone. | Immediate | Unverified |
| ASM-03 | Assumption | Existing software/modeling work is sufficient to seed preliminary results and Studies 1–2. | — | ALI/ARNON | Select exact artifacts and verify version/provenance. | Proposal evidence freeze | Partially supported |
| ASM-04 | Assumption | A suitable independent software/modeling replication context can be obtained for Plan B. | — | ALI/EXT | Identify at least two candidates and secure one authorized path. | Plan B Study 3 planning | Open assumption |
| ASM-05 | Assumption | Viewer access to MIMIC/source resources will remain available for bounded familiarization. | — | DRIVE | Confirm owner, permissions, and use restrictions. | Before sanity check | Unverified |
| ISS-01 | Issue | Final umbrella RQ and SQ1–SQ3 wording is not supervisor-approved. | — | ALI/IRIS/ARNON | Review working wording and record exact decision. | Next confirmed meeting | Open |
| ISS-02 | Issue | Plan A/Plan B boundary is internally defined but not supervisor-confirmed. | — | ALI/IRIS/ARNON | Review contract and record accepted/changed boundary. | Next proposal iteration | Open |
| ISS-03 | Issue | Initial literature workbook exists, but searches are unexecuted and the final taxonomy/data dictionary and row-level validation are not accepted. | — | ALI | Execute Search_Log protocol, validate seed rows, continue screening, and review schema. | Next confirmed meeting | Partially resolved |
| ISS-04 | Issue | No formal candidacy deadline, reviewer count, nomination process, or committee rule is evidenced. | — | GRAD/ALI | Obtain authoritative written answer. | Before formal planning/submission claim | Open |
| ISS-05 | Issue | No final Clalit use case, next meeting, retrieval-mechanism definition, or second partner is evidenced. | — | IRIS/PART | Issue one-page brief and capture partner decision/minutes. | Before partner commitment claim | Open |
| ISS-06 | Issue | No approved clinical lead, reviewers, data permission, ethics path, VDI, or local model. | — | External roles unfilled | Establish G1–G6 owners/evidence paths/feasible completion dates or default to Plan B; all six gates must pass before any later row-level medical work. | 2026-08-26 | Open; fallback-protected |
| ISS-07 | Issue | Calendar recurrence is confirmed, but the private shared-workspace structure has not been shared with or access-tested by supervisors. | — | ALI/DRIVE | Ali reviews and authorizes sharing; Iris and Arnon pass access tests; record evidence. | Immediate | Partially resolved |
| ISS-08 | Issue | Penina course due date and completion status are unverified. | — | ALI | Confirm date and create a course/proposal reuse schedule. | Immediate | Open |
| DEP-01 | Dependency | Supervisor review and decisions are required for question wording, study scope, claims, and Plan A/Plan B. | High | IRIS/ARNON | Use focused weekly decision requests and change log. | Weekly | Active |
| DEP-02 | Dependency | Independent reviewers/adjudicator are required for EXP-005 and strong Study 3 evaluation evidence. | High | IRIS/ARNON | Nominate and calibrate without compromising blindness. | Before label collection | Unfilled |
| DEP-03 | Dependency | Graduate Studies is authoritative for candidacy rules and deadlines. | High | GRAD | Obtain written response; reconcile schedule. | Before formal milestone lock | Open |
| DEP-04 | Dependency | Medical partner, clinical experts, data/governance, and VDI owners are required for Plan A. | Critical | IRIS/PART/DGO/ETH/VDI | Establish G1–G6 readiness controls by checkpoint and pass all six before row-level access. | 2026-08-26 | Unfilled/partner-dependent |
| DEP-05 | Dependency | An authorized independent non-medical context is required for Plan B Study 3. | Medium | ALI/EXT | Candidate selection and access plan. | During Plan B planning | Open |

## Weekly maintenance

At each supervisor meeting:

1. update only rows whose evidence changed;
2. link the evidence rather than narrating unsupported progress;
3. assign every new issue/dependency a named owner or mark the role unfilled;
4. show the Plan A gate count and days remaining to 2026-08-26;
5. report Plan B readiness in parallel;
6. select one next task with a measurable acceptance check; and
7. record decisions in the supervisor decision/change log.
