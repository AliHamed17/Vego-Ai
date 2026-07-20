# H-Layer Skills Map (Deliverable A for 2026-07-15 Meeting)

Last updated: 2026-07-03 by Claude. Status: DRAFT for supervisor review.

Source directives: `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` sections 1, 2, 6, 7, 10, 11.

Purpose: define the skills of the human-judgment layer ("H-layer", renamed from M1-M3 per Iris), map each skill to its integration points across VEGO-AI's Agents 1-4 and both communication circles, mark interface directions, and present the agents-vs-skills decomposition options with a recommendation.

## 1. Observable Events in the Two Communication Circles

The H-layer listens to both circles, plus internal agent signals (confidence markers and flags that are not inter-agent hand-offs; marked `Signal` below) and H-layer-internal events (marked `H-internal`). This is the event inventory it can subscribe to:

| # | Circle | Event | Producer -> Consumer | Stage |
| --- | --- | --- | --- | --- |
| E1 | Artifact | Language Template issued | Agent 1 -> Agent 2 | Early |
| E2 | Artifact | Language Template revised (after a Q&A insight) | Agent 1 -> Agent 2 | Early |
| E3 | Artifact | Reference Guidelines issued | Agent 2 -> Agent 3 | Early-mid |
| E4 | Artifact | Reference Guidelines refined (identified variability) | Agent 2 -> Agent 3 | Mid |
| E5 | Artifact | Compliance vector produced per model | Agent 3 -> Agent 4 | Mid |
| E6 | Artifact | Observed variability reported | Agent 3 -> Agent 4 | Mid |
| E7 | Artifact | Variability classification (substantial/occasional) | Agent 4 -> output | Late |
| E8 | Q&A | Language question asked (e.g., attribute vs. class) | Agent 2 -> Agent 1 | Early |
| E9 | Q&A | Language answer returned (+ possible self-refinement of template) | Agent 1 -> Agent 2 | Early |
| E10 | Q&A | Domain question asked | Agent 3 -> Agent 2 | Mid |
| E11 | Q&A | Domain answer returned (+ possible guideline refinement) | Agent 2 -> Agent 3 | Mid |
| E12 | Signal | Low-confidence guideline marked | Agent 2 internal | Early-mid |
| E13 | Signal | `flag_for_guidelines_update` (Agent 3), `Undetermined` and low confidence (Agent 4) | Agent 3 and Agent 4 internal | Mid-late |
| E14 | Artifact | Identified variability reported | Agent 2 -> Agent 4 | Mid |
| E15 | H-internal | Judgment memory updated (emitted by S6, observable by S1) | H-layer internal | Any |

Key change vs. the previous M1 design: the old review queue consumed only E7 plus the Agent-4 portion of E13 (post-Agent-4 signals). The H-layer observes E1-E15, so human judgment can enter at EARLY stages (mutually confirmed in the meeting, 03:10-03:20).

## 2. H-Layer Skills

| Skill | Function | Consumes | Produces | Human contact |
| --- | --- | --- | --- | --- |
| S1 H-Listen | Continuous, mostly-quiet observation of all events E1-E15 across every agent interaction (Arnon: continuous monitoring), including H-layer-internal events such as E15 | E1-E15 | Observation log entries | None |
| S2 H-Triage | Decide which observations merit human review; frame them; apply the configured dosage policy | S1 log | Candidate review items | None |
| S3 H1 Review Routing | Turn triaged candidates into structured review items with stable identity, trigger reason, and stage context | S2 output | Review queue items | Presents queue |
| S4 H2 Feedback Capture | Capture the real expert's decision with structure: label, rationale, confidence, provenance, reviewer identity | Review items + expert input | Structured feedback records | Bidirectional dialogue |
| S5 H-Verify | Anti-sycophancy check BEFORE feedback is accepted: test expert input against Language Template, Reference Guidelines, and domain sources; if inconsistent, raise questions (not contradictions); bounded rounds; escalate to adjudication if unresolved | S4 input + agent artifacts | Verified/queried/escalated feedback | Bidirectional dialogue |
| S6 H3 Judgment Memory | Store verified judgments as reusable memory with provenance and conflict detection; reached THROUGH S4/H2 (Iris: M3 comes through a skill of M2) | S5-verified feedback | Memory entries | None |
| S7 H-Percolate | Integrate validated judgments back into Agents 1-4: guideline refinement proposals, template corrections, context injection for future queries; iterative and convergence-guarded (no infinite mutual triggering) | S6 memory + S5 output | Correction proposals routed to agents | None (but auditable) |

Notes:

- S5 H-Verify is the new skill created by the meeting's sycophancy discussion (17:29-19:58); it did not exist in the M1-M4 design.
- S7 H-Percolate implements "learning beyond save/retrieve, including correcting the knowledge of Agents 1-4" (16:23-17:29). Save/retrieve alone (old M3) is explicitly insufficient.
- S2 H-Triage carries the dosage requirement (Iris, 15:03-15:19, revisited at 16:45-17:13): the default configuration must never block pipeline progress on missing expert feedback.

### Governance Boundary (applies to S7 and any Agent-4-affecting output)

Everything in this document is DESIGN, prepared for supervisor review. Per `docs/agent-memory/review-state.md` and `docs/research/strategic-review-and-hardening-plan.md`, any S7 output that affects Agent 4 classification (context injection into Agent 4, or template/guideline corrections that change classification inputs) remains implementation-blocked until real EXP-005 label evidence justifies a reviewed deterministic policy. The corresponding cells in the integration matrix below are marked "design only". The H-layer must always be runnable in `silent` mode, leaving baseline behavior unchanged.

## 3. Intervention Configuration Modes (per Arnon, 19:51-20:35)

S2 H-Triage reads a run-level configuration:

| Mode | Behavior | Intended use |
| --- | --- | --- |
| `every_decision` | Present every agent decision for human confirmation | Small pilots; maximal data collection |
| `threshold` | Present only decisions below a confidence threshold (or with conflict/uncertainty signals) | Default operation |
| `first_n_then_auto` | Massive review on the first N exercises; afterwards automatic handling calibrated on the collected approvals | Exercise-grading use case |
| `silent` | Listen and log only; no human contact | Version 0 baseline runs; regression tests |

The mode, threshold, and N are parameters "we can decide on" - they also become experimental variables in the parked evaluation track.

## 4. Integration Matrix: Skills x VEGO-AI Stages

| VEGO-AI stage | S1 Listen | S2 Triage | S3 Route | S4 Capture | S5 Verify | S6 Memory | S7 Percolate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Agent 1 template creation (E1, E2) | Observe | Low-confidence template constructs | Review item: "template construct unclear" | Expert clarifies construct | Check vs. language sources | Store language judgments | Template correction proposal to Agent 1 |
| Agent 2 guideline creation (E3, E4, E12) | Observe | Low-confidence guidelines; alternatives without justification | Review item: "guideline uncertain" | Expert approves/edits guideline | Check vs. template + domain description | Store guideline judgments | Guideline refinement proposal to Agent 2 |
| Q&A Agent 2 <-> Agent 1 (E8, E9) | Observe | Questions revealing systematic uncertainty | Review item: "recurring language ambiguity" | Expert rules on ambiguity | Check vs. both artifacts | Store Q&A resolutions | Inject resolution into both agents' context |
| Agent 3 inspection (E5, E6, E13 flag portion) | Observe | Compliance anomalies; guideline-update flags | Review item: "inspection uncertainty" | Expert rules on compliance case | Check vs. guidelines | Store inspection judgments | Context injection for future inspections (design only) |
| Q&A Agent 3 <-> Agent 2 (E10, E11) | Observe | Same pattern as E8/E9 | Same | Same | Same | Same | Same |
| Agent 4 classification (E7, E14, E13 confidence portion) | Observe | Uncertain/`Undetermined` classifications; identified-variability inputs (E7 + Agent-4 signals = the old M1 scope) | Review item: "classification review" | Expert labels variability | Check vs. aggregated patterns | Store classification judgments | Context injection for future classification (design only - governance-blocked until the real-label gate passes) |

## 5. Interface Directionality Inventory (Iris, 15:41-15:59)

| Interface | Old direction | New direction | Rationale |
| --- | --- | --- | --- |
| H-layer <-> Human expert | one-way (queue out, labels in, disconnected) | Bidirectional dialogue | S4/S5 question-raising and convergence |
| H-layer <-> Agent 1 | none | Bidirectional | Listen (in) + template corrections (out) |
| H-layer <-> Agent 2 | none | Bidirectional | Listen (in) + guideline refinements (out) |
| H-layer <-> Agent 3 | none | Bidirectional | Listen (in) + context injection (out) |
| H-layer <-> Agent 4 | one-way (consume outputs) | Bidirectional | Listen (in) + context injection (out) |
| Agent Q&A links | already bidirectional | unchanged | Baseline behavior preserved |

Baseline protection note: "out" arrows from the H-layer are PROPOSALS/context additions delivered through defined extension points; the original agent pipeline must remain runnable unchanged with the H-layer in `silent` mode (this preserves Version 0 for the parked evaluation and respects the frozen-baseline governance).

## 6. Agents-vs-Skills Decomposition (open decision for Iris)

| Option | Description | Pros | Cons |
| --- | --- | --- | --- |
| A. One H-agent with 7 skills | Single "Human Judgment Agent" owning S1-S7 | One shared state/memory; simple provenance; matches Iris's "one agent, several skills" hint (05:05-05:17) | Large responsibility surface; harder to reason about percolation independently |
| B. Two agents: Observer + Integrator | Observer agent (S1-S3) listens/triages/routes; Integrator agent (S4-S7) captures/verifies/stores/percolates | Matches the meeting's two functionality types (listening+deciding vs. percolating back, 07:34-08:04); clean convergence boundary | Shared memory must be an explicit contract between the two |
| C. Seven micro-agents | One agent per skill | Maximal modularity | Over-engineered; high coordination cost; Iris did not ask for this |

**Recommendation: Option B** - it mirrors the two functionality types Iris named explicitly, keeps the human-facing dialogue (S4/S5) in one place, and gives the percolation path its own convergence-guarded agent. Presented as a recommendation, not a decision; final call with Iris on 2026-07-15.

## 7. Open Questions for the 2026-07-15 Meeting

1. Agents-vs-skills: confirm Option B (Observer + Integrator) or prefer a single H-agent?
2. Which event subset should the first prototype listen to - all of E1-E13, or start with the Q&A circle (E8-E11) + guideline events (E3, E4) as the highest-value early-stage signals?
3. Default dosage: `threshold` mode with which initial threshold? Who sets N for `first_n_then_auto`?
4. Percolation approval: should every S7 correction need explicit human approval permanently, or may approval be relaxed after the EXP-005 real-label gate passes? (Automatic application is currently governance-blocked as a decision-boundary change before real-label evidence; in phase one every correction requires human approval.)
5. Convergence bounds: acceptable number of question-rounds in S5 before escalation (proposal: 2)?
6. H-naming scope: rename only in new docs/diagrams now, code rename in a dedicated PR later - acceptable?
7. Does the existing M1/M2/M3 implementation (review queue, feedback manager, judgment memory) remain the persistence backbone behind S3/S4/S6, extended with the new event sources - or is a redesign preferred?
