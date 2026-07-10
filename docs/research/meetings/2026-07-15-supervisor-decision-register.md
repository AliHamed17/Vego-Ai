# 2026-07-15 Supervisor Decision Register

Status: **Working decision source for Iris and Arnon; no decision is approved until its outcome and approver are recorded.**

Purpose: provide the single document-level decision interface used by the July 15 deck, executive pre-read, decision worksheet, and post-meeting record. Runtime APIs and VEGO-AI behavior are outside this register.

## Evidence and chronology rules

- **July 1 record:** transcript-derived and machine-generated. Timestamps point to `docs/video1832857678.transcript.he.txt`; English wording is a paraphrase unless a reviewed quotation is explicitly identified.
- **July 4-10 work:** working drafts, provisional specifications, a now-retired historical prototype scaffold, and offline design/mechanism evidence produced after the meeting. None is attributed to Iris or Arnon; the retired scaffold is not runnable evidence.
- **July 15 decision:** a recommendation becomes approved only when `Outcome`, `Rationale`, and `Approver` are completed from the meeting record.
- Attribution confidence in this register concerns speaker attribution in the machine transcript, not confidence that a proposal is correct.
- Allowed recorded outcomes: `Accepted`, `Accepted with changes`, `Rejected`, or `Deferred`. Before the meeting, `Not yet recorded` is a placeholder only; it is not an outcome.

## Record interface

Every decision record contains these fields:

`ID | July 1 basis | timestamp | attribution confidence | post-meeting evidence | recommendation | alternatives | exact decision requested | selected value | decision date | outcome | rationale | approver | owner | due date | affected artifacts | confirmation status`

## M-01 - Confirm the July 1 record

| Field | Value |
| --- | --- |
| ID | M-01 |
| July 1 basis | D1-D12 and the attributed action items in the machine-transcript-derived meeting record. The recording begins with an on-record recap of earlier unrecorded discussion; that recap still requires participant confirmation. |
| timestamp | D1-D12 collectively span 00:02:38-00:33:57; use the row-level timestamps in the enhanced July 1 evidence matrix. |
| attribution confidence | Medium overall: speaker turns and context are usable for review, but neither wording nor attribution has been human-confirmed. |
| post-meeting evidence | The July 4 notes, redirect plan, skills map, diagrams, and later package expose places where transcript directives and later proposals had been blended. |
| recommendation | Review D1-D12 one by one; accept, correct, qualify, or defer each row and each attributed action without editing the raw ASR. Keep the notes labeled canonical machine-derived notes until Iris and Arnon confirm them. |
| alternatives | Accept the record unchanged; accept with listed corrections; defer uncertain rows for focused transcript review. |
| exact decision requested | Do Iris and Arnon accept, correct, qualify, or defer each D1-D12 row and the attributed July 1 actions, including speaker attribution? |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali records corrections; Iris and Arnon confirm their attributed statements. |
| due date | 2026-07-15 meeting; corrected minutes issued within 24 hours. |
| affected artifacts | `2026-07-01-supervisor-meeting-iris.md`, evidence appendix, provenance manifest, this register, action register, deck, and pre-read. |
| confirmation status | `Needs transcript verification` until explicit participant confirmation is captured. |

## M-02 - H-layer decomposition

| Field | Value |
| --- | --- |
| ID | M-02 |
| July 1 basis | D3: use H1/H2/H3 and decide whether they are separate agents or skills; the earlier discussion also distinguished listen/decide/frame from feedback integration. |
| timestamp | 04:24-05:34 and 13:25-14:08. |
| attribution confidence | Medium: the functional split and open architecture choice are contextually clear in machine ASR, not yet participant-confirmed. |
| post-meeting evidence | July 4 `skills-map.md` defines S1-S7 and compares Option A (three H-agents), Option B (Observer + Integrator), and Option C (one H-agent with seven skill modules). These options and the recommendation are later design work. |
| recommendation | Accept Option B: an Observer owns H1/S1-S3 and an Integrator owns H2+H3/S4-S7; keep H1/H2/H3 visibly separated as skill groupings in all diagrams and specifications. |
| alternatives | Option A: three independent H1/H2/H3 agents. Option C: one H-agent with S1-S7 modules. |
| exact decision requested | Approve Option B, or select A/C; in all cases, confirm that H1/H2/H3 remain visible groupings rather than disappearing behind an implementation boundary. |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali updates the framework documents after approval. |
| due date | 2026-07-15. |
| affected artifacts | `h-layer/skills-map.md`, `h-layer/prompt-requirements.md`, `architecture/framework-diagram.md`, later detail specifications, and deck. |
| confirmation status | `Open choice`; Option B is a post-meeting recommendation, not a July 1 directive. |

## M-03 - Observation, active routing, and dosage

| Field | Value |
| --- | --- |
| ID | M-03 |
| July 1 basis | D1-D2 call for continuous listening across both communication circles and earlier intervention; D6 requires configurable dosage and warns against making progress depend on expert availability. |
| timestamp | 00:00-04:24, 14:08-17:29, and 19:51-21:19. |
| attribution confidence | Medium: continuous observation, configurable modes, and the availability concern are clear in context but await participant confirmation. |
| post-meeting evidence | The atomically recorded offline iteration 009 records 481 captured + 20 explicit gaps = 501 ObservationRecords. `11 queue items / 481 heterogeneous reconstructed lifecycle events` is a count ratio only; no event-level visibility inference or linkage exists. `threshold_sev2` event load 0.799, transaction load 0.796, weighted coverage 0.981, and high-severity coverage 1.0; the aggregate coverage >=0.8/load <=0.5 target remains unmet. Uniform K30/K35 capture is 0.75/0.85. These are offline metric/contract and Pareto results, not quality evidence or approved defaults. The run identity stays in the experiment ledger so this decision-source hash does not depend circularly on a manifest that itself binds this snapshot. |
| recommendation | Passively observe E1-E14. Initially route only guideline churn, significant uncertainty, recurring ambiguity, and source conflicts. Pilot `threshold_sev2`; use adaptive per-setting caps rather than one uniform cap, subject to monitoring and supervisor review. |
| alternatives | `every_decision`; `first_n_then_auto`; a stricter severity threshold; `silent`; a uniform review cap instead of adaptive per-setting limits. |
| exact decision requested | Approve full passive observation plus the limited active-routing trigger set; approve `threshold_sev2` as the replay-based pilot candidate; choose adaptive per-setting limits or a uniform cap. |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali revises the provisional S1-S3 specifications and experiment plan after approval. |
| due date | 2026-07-15. |
| affected artifacts | `h-layer/listener-hook-catalog.md`, `h-layer/dosage-and-triage-spec.md`, EXP-006/007/008 documentation, framework diagram, and deck. |
| confirmation status | `Open choice`; E1-E14, `threshold_sev2`, bundling, and cap policy are July 4-10 constructs, not July 1 decisions. |

## M-04 - H-Verify sources and convergence

| Field | Value |
| --- | --- |
| ID | M-04 |
| July 1 basis | D9 requires source-grounded questioning rather than blind compliance or flat contradiction; D10 requires bounded interaction and escalation. |
| timestamp | 17:29-19:58, with the no-infinite-triggering concern also at 05:22-05:34. |
| attribution confidence | Medium: the anti-sycophancy and convergence intent is clear in context; exact wording and speaker attribution remain unconfirmed. |
| post-meeting evidence | July 4-10 drafts propose four source families: Language Template, Reference Guidelines, domain description, and prior judgments. The provisional S5 design runs deterministic checks before semantic checks and proposes two question rounds before human adjudication. EXP-009/010 are assumption-driven synthetic rule tests: four seeded conflicts were detected under their encoded rules, and the two-round sweep resolved or escalated its synthetic cases. They do not validate behavior on real expert mistakes. |
| recommendation | Check all four source families; run deterministic checks first and semantic checks second; allow at most two question rounds, then escalate to explicit human adjudication. |
| alternatives | Start with a smaller source subset; use one round; use three rounds. Any semantic/LLM-assisted implementation remains separately gated. |
| exact decision requested | Approve the four-source set, deterministic-before-semantic order, and a maximum of two question rounds before human adjudication, or record the selected source subset/round bound. |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali revises the provisional S5 requirements and experiment protocols after approval. |
| due date | 2026-07-15. |
| affected artifacts | `h-layer/hverify-anti-sycophancy-spec.md`, `h-layer/prompt-requirements.md`, EXP-009, EXP-010, and deck. |
| confirmation status | `Open choice`; the source set, check order, two-round bound, and synthetic tests were produced after July 1. |

## M-05 - Human authority, timeout behavior, and implementation authorization

| Field | Value |
| --- | --- |
| ID | M-05 |
| July 1 basis | D5 says the expert is a real person; D6 says expert availability must not block progress; D7 makes the human interface part of the framework. |
| timestamp | 05:35-08:15 and 14:08-17:29. |
| attribution confidence | Medium: the real-human and non-blocking requirements are contextually clear but not yet participant-confirmed. |
| post-meeting evidence | July 4 prompt requirements and July 10 S4/S6/S7 specifications are provisional. They propose structured approval and integration flows. One provisional dosage draft also lists automatic H3 advice as a timeout option; this register rejects that option for phase one unless supervisors explicitly reverse the recommendation. No live listener hook is authorized by the drafts. |
| recommendation | Require explicit human approval for every phase-one correction. On timeout, preserve the baseline output and park the item; never apply H3 advice automatically. Permit trained course staff to review defined low-risk items while supervisors retain conflict/adjudication authority. Require a separately approved allowed-touch list before any live hook enters protected framework paths. |
| alternatives | Supervisors review every item; course staff may review but supervisors confirm every result; no live hooks and offline replay only. Automatic timeout advice is not recommended. |
| exact decision requested | Confirm the phase-one approval rule and baseline-preserving timeout; decide whether trained course staff may review low-risk items; authorize only the process for producing an allowed-touch list, not code changes themselves. |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali records the approved authority matrix and prepares an allowed-touch proposal if authorized. |
| due date | 2026-07-15 for policy; allowed-touch proposal due only after authorization. |
| affected artifacts | S4/S6/S7 provisional specifications, dosage specification, prompt requirements, governance docs, and any future implementation proposal. |
| confirmation status | `Open choice`; no runtime change, role delegation, or protected-path access is approved by this register. |

## M-06 - MSc framing and strategic extension

| Field | Value |
| --- | --- |
| ID | M-06 |
| July 1 basis | D12 establishes the literature survey and an idea log; the medical domain was discussed as a preferred extension direction. The March 2027 thesis timing was an illustrative fast-path scenario, not a commitment. |
| timestamp | 23:03-27:30 and 27:30-33:57; medical-direction discussion at approximately 33:05-33:57. |
| attribution confidence | Medium: survey, idea-log, and medical-direction discussion are identifiable in context; endorsement of a named MediVARIA plan is absent because that plan was created later. |
| post-meeting evidence | The July 4 `phd-extension-ideas.md` and MediVARIA study plan are planning drafts. MediVARIA has no approved scope, clinical partner, data work, implementation, or performance evidence. Domain-parameterized H-layer specifications are also a later proposal. |
| recommendation | Revise the MSc research question only after M-02 through M-05 settle the H-layer architecture; keep MSc empirical work in education. Present domain-parameterized specifications and MediVARIA only as PhD/future-work directions pending separate approval, ethics, partners, and evidence. |
| alternatives | Revise the MSc question immediately; postpone all research-question wording until a later meeting. Write education-only specs with a future transfer appendix instead of domain-parameterized specs. |
| exact decision requested | Decide whether the MSc research question is revised now or after architecture approval; confirm education as the MSc empirical scope; decide whether domain-parameterized specifications and MediVARIA remain proposed PhD/future work. |
| selected value | Not yet recorded. |
| decision date | Not yet recorded. |
| outcome | Not yet recorded. |
| rationale | To be recorded during the July 15 read-back. |
| approver | Iris and Arnon. |
| owner | Ali updates thesis/control documents only after the recorded decision. |
| due date | 2026-07-15 for direction; wording update date assigned in the outcome. |
| affected artifacts | Thesis research question, research plan, H-layer detail specs, `phd-extension-ideas.md`, MediVARIA planning draft, and deck appendix. |
| confirmation status | `Open choice`; MediVARIA, domain-parameterization, and the timing recommendation are post-meeting proposals. |

## Meeting close rule

Read back M-01 through M-06 with outcome, rationale, approver, owner, due date, and affected artifacts. A blank field means the item remains `Deferred`; it must not be inferred as accepted from silence.
