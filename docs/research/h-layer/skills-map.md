# H-Layer Skills Map (July 15 Deliverable A)

Last updated: 2026-07-10. Status: **PROVISIONAL DRAFT** for supervisor review. M-02 through M-05 have not been recorded; architecture, dosage, source-set, round-bound, authority, timeout, and live-hook choices are not approved.

Purpose: define the skills of the human-judgment layer ("H-layer") relative to Agents 1-4, the events it observes, its integration points across both VEGO-AI communication circles, interface directions, and the agent-versus-skill decomposition options - per the 2026-07-01 supervisor directives.

Inputs:

- `docs/video1832857678.transcript.he.md` (meeting transcript, primary source)
- `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` (canonical machine-derived notes awaiting participant confirmation)
- `docs/research/extension-plan-2026-07-supervisor-redirect.md` (active plan; H1/H2/H3 and S1-S7 canon)

## Governance Boundary

Everything here is DESIGN for supervisor review. ALL S6 outputs are correction proposals only. Implementation needs M-05 plus a separate approval of `allowed-touch-proposal.md`; until then work remains offline-only. No timeout, missing response, or memory match may apply H3 advice automatically. The H-layer must preserve baseline behavior and E15 must remain outside the framework.

## 1. Observable Events (E1-E15)

The H-layer listens to both communication circles - the artifact circle and the Q&A circle - plus the human-feedback lifecycle it owns. One event (E15) exists only to be routed OUT of the framework into the parked evaluation track.

| # | Channel | Event | Concrete VEGO-AI meaning | Stage |
| --- | --- | --- | --- | --- |
| E1 | Artifact | Language Template created or revised | Agent 1 -> Agent 2 hand-off; revisions include self-refinement after Q&A | Early |
| E2 | Q&A | Downstream agent requests clarification | Either Q&A pair: Agent 2 -> Agent 1 language question (e.g., attribute vs. class) or Agent 3 -> Agent 2 domain question; typically marking a low-confidence decision | Early-mid |
| E3 | Q&A | Upstream agent answers Q&A | Either Q&A pair: Agent 1 -> Agent 2 or Agent 2 -> Agent 3 answer; may trigger the answerer to revise its own artifact (E1/E4) | Early-mid |
| E4 | Artifact | Domain Advisor creates or refines Reference Guidelines | Agent 2 -> Agent 3 hand-off, including refinements from identified variability | Early-mid |
| E5 | Artifact | Model Inspector applies guidelines | Agent 3 produces a compliance vector per model | Mid |
| E6 | Signal | Model Inspector emits uncertainty | `requires_human_review`, low confidence, `flag_for_guidelines_update` | Mid |
| E7 | Artifact | Variability Explorer receives artifacts | Identified variability (from Agent 2) and observed variability (from Agent 3) arrive at Agent 4 | Mid-late |
| E8 | Artifact | Agent 4 classifies variability | Substantial / occasional / `Undetermined`, with confidence - the old M1 trigger scope | Late |
| E9 | Q&A | Q&A reveals template or guideline ambiguity | Recurring or unresolved questions in either Q&A pair (Agent 2 <-> Agent 1, Agent 3 <-> Agent 2) exposing systematic ambiguity | Early-mid |
| E10 | Human | Human feedback received | The real expert answers a routed review item through the H2 interface | Any |
| E11 | Human | Feedback conflicts with source evidence | S5 H-Verify finds expert input inconsistent with the Language Template, Reference Guidelines, domain description, or prior judgments | Any |
| E12 | Human | Verified or adjudicated feedback stored | Only an S5-verified or explicitly supervisor-adjudicated judgment enters trusted H3 memory | Any |
| E13 | Human | Prior feedback retrieved | Stored judgment is recalled for a new, relevant situation | Any |
| E14 | Human | Knowledge correction needed for an agent | A verified judgment implies a correction to Agent 1-4 knowledge (template fix, guideline refinement, context note) | Any |
| E15 | Evaluation | Evaluation event (parked, outside framework) | Comparison/accuracy-relevant events (e.g., M4A advice, M4B-1 comparisons) - observed only to be routed to the parked evaluation track, never acted on inside the framework | Late |

## 2. Skills (S1-S7)

| Skill | Function | Consumes | Produces | Human contact |
| --- | --- | --- | --- | --- |
| S1 Listen | Continuous, mostly-quiet observation over E1-E14 across every agent interaction (Arnon: continuous, all agents); E15 evaluation events are only routed out to the parked track, never acted on | E1-E15 | Observation log | None |
| S2 Triage intervention | Classify each observation as an intervention opportunity or not, under the configured dosage budget | S1 log | Promoted candidates with trigger reasons | None |
| S3 Ask human | Turn promoted candidates into self-contained review items and route them to the real expert | S2 output | Review items (stable identity, evidence bundle, decision needed) | Presents queue |
| S4 Capture feedback | Structured capture of the expert's decision: label, rationale, confidence, validity scope, reviewer identity, date | Review items + expert input (E10) | Structured feedback records | Bidirectional dialogue |
| S5 H-Verify | Anti-sycophancy: check expert input against sources BEFORE it is trusted; raise questions on conflict (E11), never blind-comply and never flatly contradict; bounded rounds | S4 records + sources | Verified / revised / escalated feedback | Bidirectional dialogue |
| S6 Integrate | Deliver verified judgments back into agent artifacts/context as correction proposals (E14), approval-gated, loop-safe | S5-verified feedback | Correction proposals to Agents 1-4 | Approval requests |
| S7 Percolate / learn | Maintain judgment memory (store E12, retrieve E13), detect conflicts, generalize across cases, and update what the layer itself asks/checks over time - more than save/retrieve | S5/S6 outputs + memory | Judgment memory; learning updates; retrieval results | None |

H1/H2/H3 mapping: H1 = S1+S2+S3 (intervention detection), H2 = S4+S5 (feedback interface and capture), H3 = S6+S7 (memory, learning, reuse). M4-equivalent advisory/comparison is NOT a skill here - it is parked evaluation.

## 3. Intervention Dosage Configuration (D6)

S2 reads a run-level configuration; it also parameterizes the parked evaluation later.

| Mode | Behavior | Intended use |
| --- | --- | --- |
| `every_decision` | Route every agent decision for human confirmation | Small pilots; Arnon's maximal-data first stage |
| `threshold` | Route only decisions below a candidate confidence/severity threshold or carrying conflict/uncertainty signals (E6, E9, E11) | Replay candidate; `threshold_sev2` is not an approved default |
| `first_n_then_auto` | Intensive review of the first N exercises; afterwards baseline behavior continues under the selected routing policy | Exercise-grading comparison; no automatic H3 application |
| `silent` | Listen and log only; no human contact | Baseline preservation; regression testing |

Safety proposal for M-05: no mode may make pipeline progress depend on expert availability. On timeout, preserve baseline behavior and park the item; never apply H3 advice or a correction automatically.

## 4. Integration Matrix

Cell values: observe (S1 watches), interrupt (S2 may promote), ask (S3 routes to human), verify (S5 checks), integrate (S6 proposes corrections), learn (S7 stores/generalizes).

| Row \ Skill | S1 Listen | S2 Triage | S3 Ask | S4 Capture | S5 Verify | S6 Integrate | S7 Learn |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Agent 1 Language Advisor (E1, E3) | observe | interrupt on template ambiguity | ask: "template construct unclear" | capture language rulings | verify vs. language sources | integrate template corrections (design only, approval-gated) | learn language judgments |
| Agent 2 Domain Advisor (E2, E3, E4, E7 identified) | observe | interrupt on low-confidence guidelines | ask: "guideline uncertain" | capture guideline rulings | verify vs. template + domain description | integrate guideline refinements (design only, approval-gated) | learn guideline judgments |
| Agent 3 Model Inspector (E2, E5, E6) | observe | interrupt on uncertainty signals | ask: "inspection uncertainty" | capture compliance rulings | verify vs. guidelines | integrate inspection context (design only, approval-gated) | learn inspection judgments |
| Agent 4 Variability Explorer (E7, E8) | observe | interrupt on `Undetermined` / low confidence (old M1 scope) | ask: "classification review" | capture variability labels | verify vs. aggregated patterns | integrate classification context (design only - governance-blocked until real-label gate passes) | learn classification judgments |
| Artifact channel (E1, E4, E5, E7) | observe | interrupt on artifact deltas that reverse earlier decisions | ask when deltas conflict | - | verify deltas cited in feedback | integrate artifact corrections (design only, approval-gated) | learn artifact history |
| Q&A channel (E2, E3, E9) | observe | interrupt on recurring/unresolved questions | ask: "recurring ambiguity" | capture Q&A adjudications | verify vs. both artifacts | integrate resolutions into both agents' context (design only, approval-gated) | learn resolved ambiguities |

E10-E14 are the H-layer's own lifecycle (rows above produce them); E15 is routed to the parked evaluation track without framework action.

## 5. Interface-Direction Inventory (D7)

| Interface | Current (likely) | Required | Timing |
| --- | --- | --- | --- |
| H-layer <-> Human expert | One-way (queue out, labels in, disconnected) | Bidirectional dialogue (S4 elicitation, S5 questioning) | Immediately (design) - core of the thesis interface work |
| H-layer <- Agents 1-4 (listening) | Absent (only post-Agent-4 signals reach M1) | Inbound taps on E1-E9 | Immediately (design), listener-first |
| H-layer -> Agents 1-4 (corrections) | Absent | Outbound correction proposals (S6) | Delayed and configurable: approval-gated; Agent-4-affecting outputs design-only until the real-label gate |
| Agent Q&A links | Already bidirectional | Unchanged | Baseline behavior preserved |
| H-layer internal (S5 <-> S4, S6 <-> S7) | New | Bidirectional (revision loops, memory feedback) | Immediately (design) |

Bidirectionality that should stay configurable/delayed: outbound corrections into agents (dosage + approval), and any Agent-4-adjacent flow (governance).

## 6. Architecture Options (agents vs. skills)

| Option | Description | Pros | Cons |
| --- | --- | --- | --- |
| A. H1/H2/H3 as three separate agents | One agent per H-milestone | Clear one-to-one mapping to Iris's H-naming; independent evolution | Splits tightly-coupled skills (S3/S4 share the review item; S5/S6 share verification state); three-way shared-memory contracts |
| B. Observer + Integrator (provisional recommendation) | Observer agent = H1 (S1-S3); Integrator agent = H2+H3 (S4-S7) | Mirrors the meeting's two functionality types (listen+decide+frame vs. percolate back); human dialogue lives in one place; clean convergence boundary between watching and changing | H2/H3 boundary is internal to the Integrator and must stay visible in docs |
| C. One H-agent with skill modules | Single agent, S1-S7 as modules | One state store; simplest provenance | Large responsibility surface; harder to reason about convergence; weakest match to "maybe several skills, maybe another agent" (transcript 05:05-05:17) |

Provisional recommendation for M-02: **Option B**. It remains an open choice until an outcome is recorded; no repository evidence converts it into an approved architecture.

## 7. Open Questions For Iris (2026-07-15)

1. Intervention dosage: which mode should be piloted, with what threshold/cap and reviewer role? No mode is currently the default.
2. H-Verify source set: should S5 check expert input against the Language Template + Reference Guidelines + domain description + prior stored judgments (all four), or a smaller set first?
3. Diagram representation: show H1/H2/H3 as grouped skill clusters (as now) or as explicit agent boxes once the option is chosen?
4. Can course staff (TAs, the second-semester lecturer) act as early human experts, or supervisors only in the first phase?
5. Observation coverage: approve passive E1-E14 observation, or record a smaller phase-one subset; E15 remains evaluation-only in either case.
6. Convergence policy: acceptable number of S5 question rounds before escalation to adjudication (proposal: 2)?
7. Percolation/authorization: confirm explicit approval for every phase-one correction and whether to authorize preparation of the five-file allowed-touch record; no code change follows automatically.
8. MediVARIA alignment (M-06): keep it proposed PhD/future work with education as the MSc empirical scope?
