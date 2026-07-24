# 2026-07-15 Supervisor Action Register

Status: **Working register.** Rows preserve their origin and do not create commitments for Iris, Arnon, course staff, or external partners.

## Record interface

Every action record contains these fields:

`ID | origin | owner | due date | status | dependency | evidence link | next checkpoint`

Status vocabulary:

- `Draft prepared - acceptance pending`: an artifact exists, but supervisors have not accepted it.
- `Open - completion not evidenced`: the action was recorded, but this package does not contain completion evidence.
- `Pending decision`: work must wait for the named M-decision.
- `Parked`: intentionally outside the active framework-design sequence.
- `Done`: use only when completion is explicitly evidenced.

## Register

### July 1 attributed actions awaiting M-01 confirmation

These rows preserve the six actions exactly as the machine-derived July 1 record currently attributes them. They remain open to correction under M-01. When an action is accepted, create or update its operational `A-__` row below rather than rewriting this historical-origin row.

| ID | Origin | Owner | Due date | Status | Dependency | Evidence link | Next checkpoint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J1-A01 | July 1 transcript-derived action: prepare the H-layer skills map relative to Agents 1-4 and show involvement points | Ali | July 15 follow-up | Draft prepared - acceptance pending | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 21:19-21:42 | Confirm attribution, owner, due date, and required revisions. |
| J1-A02 | July 1 transcript-derived action: prepare prompt requirements without final prompt wording | Ali | July 15 follow-up | Draft prepared - acceptance pending | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 21:42-22:21 | Confirm attribution, owner, due date, and required revisions. |
| J1-A03 | July 1 transcript-derived action: continue the agentic HITL/generative-AI literature survey and identify the novelty gap | Ali | Mid-August presentation; submission timing to be externally confirmed | Open - completion not evidenced | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 23:03-27:30 | Confirm attribution and external course dates. |
| J1-A04 | July 1 transcript-derived action: ask Sigal and the Graduate Studies Authority about direct-track rules, credits, and steps | Ali | Not specified | Open - completion not evidenced | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 28:59-30:59 | Confirm attribution and assign a date, or close with completion evidence. |
| J1-A05 | July 1 transcript-derived action: invite Arnon to the July 15 meeting | Iris | Before the follow-up | Open - completion not evidenced | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 27:30-27:57 | Confirm whether the invitation was sent and accepted. |
| J1-A06 | July 1 transcript-derived action: keep a log of possible extension studies while reading | Ali | Ongoing | Open - completion not evidenced | M-01 confirmation | `2026-07-01-supervisor-meeting-iris.md`; transcript 33:05-33:57 | Confirm attribution and the desired checkpoint cadence. |

### Package and post-decision actions

| ID | Origin | Owner | Due date | Status | Dependency | Evidence link | Next checkpoint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-01 | July 1 transcript-derived action: prepare H-layer skills map and prompt requirements | Ali | 2026-07-15 | Draft prepared - acceptance pending | M-01 confirmation and M-02 through M-05 decisions | `../h-layer/skills-map.md`; `../h-layer/prompt-requirements.md`; transcript 21:19-22:21 | Present the two deliverables; record requested revisions before assigning a new due date. |
| A-02 | July 1 transcript-derived action: separate framework and evaluation views | Ali with documentation agents | 2026-07-15 | Draft prepared - acceptance pending | M-01 and M-02 | `../../architecture/framework-diagram.md`; `../../architecture/evaluation-diagram.md`; transcript 13:03-13:09 and 22:36-22:59 | Confirm the split and the chosen H1/H2/H3 representation. |
| A-03 | July 1 transcript-derived action: progress the agentic/generative-AI HITL literature survey | Ali | Mid-August 2026 presentation; written submission timing to be reconfirmed | Open - completion not evidenced | M-01 confirmation of course timing and scope | `../literature-review-taxonomy.md`; transcript 23:03-27:30 | Confirm the course deadline and the gap-statement deliverable at the July 15 read-back. |
| A-04 | Operational mapping for J1-A04: ask Sigal / Graduate Studies Authority about direct-track requirements, credits, and milestones | Ali | Not specified; assign only after M-01 confirmation | Open - completion not evidenced | J1-A04 and M-01 | `../phd-extension-ideas.md`; transcript 28:59-30:59 | Assign a calendar date or close with evidence after M-01. |
| A-05 | July 15 meeting operation: review and correct D1-D12 and attributed actions | Ali records; Iris and Arnon confirm | During 2026-07-15 meeting | Pending decision | M-01 | `2026-07-15-supervisor-decision-register.md`; enhanced July 1 evidence matrix | Complete the D1-D12 correction log before moving from record review to architecture decisions. |
| A-06 | July 15 meeting operation: update architecture and skill groupings to the selected decomposition | Ali | Within 24 hours of M-02, unless a different date is assigned | Pending decision | M-02 | `2026-07-15-supervisor-decision-register.md`; `../h-layer/skills-map.md` | Confirm that diagrams and specifications show the same agent/skill boundary. |
| A-07 | July 15 meeting operation: revise routing, dosage, bundling, and workload-cap policy | Ali | Within 24 hours for decision wording; specification date assigned in M-03 outcome | Pending decision | M-03 | `2026-07-15-supervisor-decision-register.md`; EXP-006/007/008 docs; provisional `../h-layer/dosage-and-triage-spec.md` | Record selected mode, severity threshold, routed trigger set, and cap policy. |
| A-08 | July 15 meeting operation: revise H-Verify source order and convergence policy | Ali | Within 24 hours for decision wording; protocol date assigned in M-04 outcome | Pending decision | M-04 | `2026-07-15-supervisor-decision-register.md`; provisional `../h-layer/hverify-anti-sycophancy-spec.md`; EXP-009/010 docs | Record source set, deterministic/semantic order, round bound, and adjudication owner. |
| A-09 | July 15 meeting operation: record the phase-one authority matrix | Ali drafts; Iris and Arnon approve roles | Within 24 hours for recorded policy | Pending decision | M-05 | `2026-07-15-supervisor-decision-register.md`; provisional S4/S6/S7 specs | Name who may review low-risk items, who adjudicates conflicts, and what happens on timeout. |
| A-10 | Post-decision governance: prepare a proposed allowed-touch list for any live listener hooks | Ali | Date to be assigned only if M-05 authorizes preparation | Pending decision | M-05 explicit authorization; separate implementation approval still required | `../h-layer/listener-hook-catalog.md`; redirect-plan governance boundary | Submit the list for review; do not change protected runtime paths as part of this action. |
| A-11 | July 15 meeting operation: align MSc question timing and future-work framing | Ali | Date assigned in M-06 outcome | Pending decision | M-06 | `2026-07-15-supervisor-decision-register.md`; thesis/control documents; MediVARIA planning draft | Keep education as the empirical scope and record whether research-question wording changes now or after architecture approval. |
| A-12 | Post-meeting: issue corrected minutes and update decision/action registers | Ali | Within 24 hours of meeting end | Pending decision | M-01 through M-06 read-back | `2026-07-15-post-meeting-capture-template.md` | Send corrected minutes for confirmation; do not alter the raw transcript or ASR. |
| A-13 | Post-meeting: regenerate the shareable PPTX/PDF/pre-read package and update hashes/manifest | Ali with artifact tooling | Within 24 hours after outcomes are incorporated | Pending decision | A-12 and recorded source versions | Package manifest and generated exports | Verify rendered outputs, then record new hashes and generation time. |
| A-14 | Parked evaluation: collect real EXP-005 labels only from authorized human experts | Authorized expert(s), owner to be scheduled separately | No date assigned | Parked | Framework stabilization and expert availability; real-label protocol | `../expert-labeling-protocol.md`; EXP-005 gate | Resume only when a real labeling session is explicitly scheduled; never invent or auto-fill labels. |

## Ownership rule

If Iris or Arnon does not explicitly accept an action assigned to them, record the owner as `TBD` rather than inferring ownership. “Within 24 hours” applies to documentation updates after the meeting; it does not authorize runtime edits, clinical work, or evaluation execution.
