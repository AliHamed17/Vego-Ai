# VEGO-AI Extension Plan - Supervisor Redirect (2026-07-01 Meeting)

Last updated: 2026-07-03 by Claude.

Status: ACTIVE PLAN. Supersedes the "evaluation-first, feature-frozen" next-step ordering in `docs/research/strategic-review-and-hardening-plan.md` for sequencing purposes, while keeping all of its evidence gates and claim boundaries intact.

Sources: `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` (meeting notes), local Hebrew transcript at ignored `artifacts/meetings/2026-07-01-iris/transcript_he.txt`.

## 0. Executive Summary

The 2026-07-01 supervisor meeting redirects the project from "collect EXP-005 labels and evaluate the M4B-1 pipeline" to "redesign and specify the human-judgment layer as a first-class part of the VEGO-AI framework, then evaluate later."

The eight structural directives from Iris (with Arnon's additions):

1. The human layer must integrate with BOTH VEGO-AI communication circles - the artifact circle and the questions-and-answers circle - as a mostly-quiet continuous LISTENER that intervenes at EARLY stages, not only after Agent 4 classification.
2. Rename the human-layer milestones M1/M2/M3 to **H1/H2/H3**; decide whether they are separate agents or skills of one agent.
3. **M4 (memory advisory / memory-informed comparison) is deferred** and repositioned as part of the EVALUATION track, not the framework.
4. Keep FRAMEWORK and EVALUATION in **separate diagrams**; park evaluation work until the framework stabilizes.
5. The human expert is a **real person** (Iris, Arnon, TAs, later colleagues abroad) - never a simulated agent; but calibrate the dosage of expert involvement so progress never blocks on expert availability.
6. Interfaces to the human and between agents must be largely **bidirectional**; part of the thesis is defining the human interface.
7. Memory must go beyond save/retrieve: **reason and learn** from feedback, including correcting the knowledge of Agents 1-4, with an **anti-sycophancy** protocol (verify expert input against sources; question rather than comply; guaranteed convergence).
8. Human intervention must be **configurable** (per-decision pop-up / confidence threshold / first-N-massive-then-automatic) - to be captured in a detailed spec per element.

Two concrete deliverables are due for the **2026-07-15** meeting: (A) an H-layer skills map against Agents 1-4 with integration points, and (B) prompt REQUIREMENTS (not prompts) for the H-layer agents.

Parallel obligations: literature survey (Pnina's course; presentation mid-August, submission end-September/October), aiming for a framework+survey PAPER by September/early October, with a March-2027 thesis submission trajectory and a possible MSc-to-PhD direct track (medical-domain extension as the preferred PhD direction).

## 1. Gap Analysis: Meeting Directives vs. Current Repo State

| # | Iris/Arnon directive | Current repo state | Gap / action |
| --- | --- | --- | --- |
| 1 | Human layer listens on BOTH circles (artifact + Q&A), intervenes early (Agents 1-3), not only post-Agent-4 | M1 review queue triggers on late-stage Agent 3/4 signals (`requires_human_review`, confidence, `Undetermined` from Agent 4, `flag_for_guidelines_update` from Agent 3); no hooks on Language Template, Reference Guidelines, or inter-agent Q&A | Design listener hook points across both circles; new H-layer architecture spec; later a non-destructive listener implementation |
| 2 | Rename M1/M2/M3 -> H1/H2/H3; agents-vs-skills decision | All docs, diagrams, schemas, and memory files use M1-M4B naming | Docs/diagram rename first (H1=review routing, H2=feedback capture, H3=judgment memory); code/schema rename deferred to a dedicated PR to avoid churn |
| 3 | M4 deferred; belongs to evaluation | M4A + M4B-1 implemented, merged, tagged; M4B-2 blocked | No new M4 work; keep artifacts frozen at tags; reposition M4A/M4B-1 + EXP-001..005 in the evaluation diagram/track |
| 4 | Separate framework and evaluation diagrams; park evaluation | Single combined topology (`docs/architecture/workspace-diagram.md`, topology exports); evaluation-first strategy doc | Produce two diagrams; mark evaluation track PARKED; EXP-005 label collection remains the evaluation entry gate when unparked |
| 5 | Real human experts; calibrated dosage | EXP-005 blind labeling sheet awaiting real labels (0/27); "human expert" concept correctly real-human in EXP tooling | Aligned in evaluation track; framework spec must define expert roles (supervisor, TA, external) and dosage/configuration modes |
| 6 | Bidirectional interfaces; thesis defines the human interface | Current flow is one-directional (queue -> feedback -> memory -> advice); visualizer is read-only | Add interface-direction inventory to the skills map; human-interface requirements section in the detail spec; UI design parked until framework stabilizes (Iris: "the easier part") |
| 7 | Learning beyond save/retrieve; correct Agents 1-4 knowledge; anti-sycophancy; convergence | M3 memory is inert save/retrieve with provenance/conflict detection; M4A advisory-only; no learning loop; no sycophancy defense | New H3+ design: judgment validation against sources, question-raising protocol, convergence rules, knowledge-correction pathways (guideline/template refinement proposals) - spec first, implementation gated |
| 8 | Configurable intervention (per-decision / threshold / first-N) | Selective intervention policy exists but is fixed-rule, post-Agent-4 only | Intervention-configuration section in detail spec; maps to existing `selective_intervention_policy.py` as the extension point |
| 9 | Deliverables for 2026-07-15: skills map + prompt requirements | Do not exist | Draft both this week (see Phase 1) |
| 10 | Literature survey (agentic HITL, RL+LLM, generative-AI feedback loops) as course work; gap articulation | `docs/research/literature-review-taxonomy.md` exists (earlier framing) | Extend taxonomy with agentic-HITL, RLHF/RL+LLM, LLM-agent memory/learning, sycophancy/trust-calibration branches; build survey corpus and gap statement |
| 11 | Paper (framework + survey) by Sep/early-Oct | `papers/mas4models2026/claim-evidence-table.md` oriented to old framing | New paper skeleton for framework+survey; update claim/evidence table to H-layer framing |
| 12 | PhD trajectory: idea log; medical-domain extension | Not tracked | Add `docs/research/phd-extension-ideas.md` idea log; capture medical-domain transfer question |

## 2. Reframed Target Architecture (Framework Track)

```text
                    VEGO-AI baseline (UNCHANGED, protected)
   Agent 1 Language Advisor --Language Template--> Agent 2 Domain Advisor
   Agent 2 --Reference Guidelines--> Agent 3 Model Inspector
   Agent 2 + Agent 3 --identified/observed variability--> Agent 4 Variability Explorer
   plus Q&A circle: Agent 2 <-> Agent 1, Agent 3 <-> Agent 2 (questions and answers)

                    H-layer (NEW FRAMING - continuous listener)
   S1 H-Listen:      subscribe to artifact events AND Q&A exchanges across
                     all agent interactions (Arnon: continuous, every interaction)
   S2 H-Triage:      decide which observations merit human review, frame them
                     (configurable dosage: per-decision / threshold / first-N)
   S3 H1 Review routing:   create structured review items early (not only post-Agent 4)
   S4 H2 Feedback capture: structured expert feedback with provenance (real experts only)
   S5 H-Verify:      anti-sycophancy - check expert input against sources BEFORE it
                     is accepted, raise questions instead of complying, drive convergence
   S6 H3 Judgment memory:  reusable memory of VERIFIED judgments, reached THROUGH H2,
                     feeding back into VEGO-AI
   S7 H-Percolate:   integrate validated judgments back to Agents 1-4
                     (guideline/template corrections, context injection), iterative,
                     convergence-guarded (no infinite agent loops); Agent-4-affecting
                     outputs are design-only until the real-label gate passes

   Open design decision for 2026-07-15: one H-agent with multiple skills vs.
   multiple H-agents; interface directions (mostly bidirectional).
```

Evaluation track (SEPARATE diagram, PARKED): Version 0 (no human) vs. Version 1 (with human) comparison on error counts and agreed criteria + usability questionnaire; M4A advisory retrieval and M4B-1 deterministic comparison become evaluation instruments; EXP-001..EXP-005 tooling and the real-label gate live here unchanged.

## 3. Workstreams and Phases

### Phase 0 - Repo and governance realignment (2026-07-03 .. 2026-07-06)

| Task | Output | Notes |
| --- | --- | --- |
| P0.1 Record meeting notes | `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` | Done 2026-07-03 |
| P0.2 This plan | `docs/research/extension-plan-2026-07-supervisor-redirect.md` | Done 2026-07-03 |
| P0.3 Split diagrams | `docs/architecture/framework-diagram.md` (H-layer listener view) + `docs/architecture/evaluation-diagram.md` (parked track) | Mermaid, GitHub-rendered |
| P0.4 Memory + dashboards update | `docs/agent-memory/*`, `docs/dashboards/*`, wiki outbox | Per CLAUDE.md end-of-prompt workflow |
| P0.5 Naming policy decision | Decision entry: H1/H2/H3 naming used in all NEW docs/diagrams; code rename deferred | Avoids breaking tags/tests mid-redesign |

### Phase 1 - 2026-07-15 meeting deliverables (2026-07-03 .. 2026-07-14)

| Task | Output | Acceptance |
| --- | --- | --- |
| P1.1 H-layer skills map (Deliverable A) | `docs/research/h-layer/skills-map.md` | Lists every H-skill; for each: purpose, trigger events on artifact/Q&A circles, involvement point per Agent 1-4 stage, direction of each interface (uni/bi), agents-vs-skills options with a recommendation and open questions for Iris |
| P1.2 Prompt requirements (Deliverable B) | `docs/research/h-layer/prompt-requirements.md` | For each H-skill: intent (what we want to say), required context, task definition, steps, inputs/outputs, guardrails (anti-sycophancy, convergence, dosage) - explicitly NOT the prompt text |
| P1.3 Framework diagram v2 | `docs/architecture/framework-diagram.md` | Two circles explicit; H-layer as listener; bidirectional arrows marked; evaluation absent (separate diagram) |
| P1.4 Open-questions list | section inside P1.1 | Agents-vs-skills, dosage defaults, which Q&A events are in scope first, memory-correction approval flow |
| P1.5 Dry-run review | Supervisor-ready package | Self-review against the meeting notes; all 8 directives traceable |

### Phase 2 - Detailed specification per element (2026-07-15 .. 2026-08-15, direction-corrected after the meeting)

| Task | Output |
| --- | --- |
| P2.1 Listener hook catalog | Spec of every observable event: Language Template issued/revised, Reference Guidelines issued/refined, compliance vector produced, Q&A question, Q&A answer, guideline-update flag - with schema sketches |
| P2.2 Intervention configuration spec | Modes: per-decision pop-up, confidence-threshold, first-N-massive-then-auto (Arnon), per-run config file; mapping to `selective_intervention_policy.py` as extension point |
| P2.3 Anti-sycophancy and convergence protocol | Expert-input verification flow: check against Language Template/Reference Guidelines/domain sources -> if inconsistent, generate questions (not refusals) -> bounded dialogue rounds -> escalation/adjudication; convergence limits |
| P2.4 Feedback percolation and learning spec | How validated judgments correct Agents 1-4 knowledge: guideline refinement proposals, template corrections, context injection for future queries; distinction save/retrieve vs. reason/learn; loop-safety (no infinite mutual triggering) |
| P2.5 Human-interface requirements (not UI build) | Roles (supervisor/TA/external expert), bidirectional exchanges, review ergonomics; UI implementation deferred (Iris: after framework, "the easier part") |
| P2.6 H-layer prototype scaffolding (code, gated) | Non-destructive listener that logs artifact/Q&A events from existing run outputs to `h_layer_observations.jsonl`; no baseline behavior change; new branch + PR; tests |

### Phase 3 - Literature survey and course work (2026-07-03 .. 2026-08-15 presentation; submission end-Sep/Oct)

| Task | Output |
| --- | --- |
| P3.1 Survey scope and taxonomy v2 | Extend `docs/research/literature-review-taxonomy.md`: (a) HITL in agentic/multi-agent LLM systems; (b) RLHF and RL+LLM feedback incorporation (Arnon's pointer); (c) memory/learning in LLM agents beyond save-retrieve; (d) sycophancy and trust calibration; (e) human-AI collaboration in conceptual modeling/model assessment; (f) configurable human-intervention architectures |
| P3.2 Corpus building | Search log + screened paper list per branch, PRISMA-style counts |
| P3.3 Gap articulation | One-page statement: what VEGO-AI H-layer adds relative to each branch (the thesis gap) - reviewed with Iris |
| P3.4 Mid-August presentation | Slides for Pnina's course |
| P3.5 Written survey | Course submission end-September/October; doubles as thesis related-work chapter |

### Phase 4 - Paper assembly (2026-09-01 .. 2026-10-31)

| Task | Output |
| --- | --- |
| P4.1 Paper skeleton | Framework (H-layer architecture + detail specs) + literature positioning; venue per `docs/research/publication-plan.md` review with Iris |
| P4.2 Claim/evidence table refresh | Claims restricted to framework/design + mechanism readiness; accuracy claims remain blocked until real-label evaluation |
| P4.3 Consolidated framework demo | Runnable walkthrough on course-modeling data for the October "crystallized" target |

### Phase 5 - Evaluation track (PARKED; unpark on Iris's go-ahead)

Preserved, not deleted. When unparked:

| Element | Source |
| --- | --- |
| Version 0 vs. Version 1 comparison design (error counts, agreed criteria) | Meeting section 4 |
| Usability questionnaire for Version 1 users | Meeting section 4 |
| Real-expert labels via EXP-005 gate (>=20 generalization-safe labels; adjudication) | `docs/research/strategic-review-and-hardening-plan.md` - unchanged |
| M4A advisory + M4B-1 comparison as evaluation instruments | Frozen tags `research-state-m4b1-deterministic-comparison`, `research-state-m4a` |
| Pilots: local course team, second-semester lecturer, TA teams; later Stockholm University and Belgium colleagues | Meeting section 5 |

### Phase 6 - PhD trajectory (ongoing, low intensity)

| Task | Output |
| --- | --- |
| P6.1 Idea log | `docs/research/phd-extension-ideas.md`: extensions noticed while reading (Arnon's instruction), each 2-4 lines, to be closed with Iris |
| P6.2 Medical-domain transfer note | Standing entry: can the architecture/evaluation transfer to medical-domain modeling; implications |
| P6.3 Administrative checks | Ali: direct-track rules with Sigal / Graduate Studies Authority (course credit, milestones) |

## 4. Governance Alignment

Unchanged (from `docs/agent-memory/review-state.md` and the hardening plan):

- No M4B-2, no Agent 4 behavior changes, no LLM/API reclassification, no embeddings, no baseline output overwrites, no `VEGO-AI/eval_output` changes.
- Blocked claims stay blocked (no accuracy-improvement claims; no generalization claims; synthetic outputs are not evidence).
- Frozen tags stay frozen.

Changed by this plan (supervisor-directed):

- Sequencing: framework redesign/specification work is now the active track; EXP-005 label collection moves into the PARKED evaluation track (it remains the entry gate of that track when unparked - collecting labels earlier remains welcome if supervisor time appears).
- New implementation work is allowed ONLY for the H-layer listener/spec scaffolding (P2.6-style, non-destructive, logging-first, separate branch/PR) after the 2026-07-15 skills-map review - not before Iris confirms the skills map direction.
- Naming: new research docs and diagrams use H1/H2/H3; existing code, schemas, tags, and merged history keep M-names until a dedicated rename PR is approved.

Reconciliation with the standing review machinery:

- `docs/agent-memory/review-state.md` and `scripts/run-project-review.ps1` encode "collect real EXP-005 labels" as the blocking next action. Under this redirect, that blocker gates ONLY the parked evaluation track; the framework track proceeds independently. Review-state carries a redirect note to the same effect; the review runner's EXP-005 verdict should be read as the evaluation-track status, not a stop signal for framework-track doc/spec work.
- `docs/research/strategic-review-and-hardening-plan.md` status line now points here for sequencing; its evidence gates, claim boundaries, and validation command set are unchanged and still authoritative for any evidence claim.
- Protected-paths gate vs. H-layer implementation: the M1-M3 backbone and any live listener hooks live under `VEGO-AI/framework/`, which the standing validation treats as a no-diff protected path. Before any P2.6-style code work, the allowed-touch list must be agreed explicitly (proposal: new H-layer modules may be ADDED under `VEGO-AI/framework/` or a new `VEGO-AI/h_layer/` package; existing agent/orchestrator files may gain only inert, opt-in hook points; behavior equivalence is proven by baseline-output regression tests with the H-layer in silent mode, replacing the blanket no-diff rule for those specific files). This proposal itself needs supervisor/Codex review sign-off first.

## 5. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Misreading a meeting point (ASR noise) | Meeting notes cross-verified by independent extraction passes; open-questions list presented to Iris on 2026-07-15 for confirmation |
| Over-building before supervisor confirmation | Phase 1 is docs/diagrams only; code scaffolding gated behind the 2026-07-15 review |
| Expert-time bottleneck (Iris's dosage concern) | Intervention-configuration spec defaults to threshold/first-N modes; never design a flow that blocks on per-decision expert input |
| Sycophancy in the H-layer | P2.3 protocol: verify-then-question; bounded dialogue; escalation to adjudication |
| Infinite agent feedback loops | Convergence rules in P2.4: bounded iterations, idempotent guideline updates, no mutual re-triggering |
| Literature survey crowds out framework work (or vice versa) | Separate phases with distinct outputs; survey doubles as thesis chapter to avoid duplicate effort |
| Losing the evaluation investment (EXP-001..005) | Nothing deleted; evaluation track parked with explicit unpark conditions |
| Claim drift in the paper | P4.2 claim table keeps accuracy claims blocked until real-label evidence exists |

## 6. Immediate Next Actions (this week)

1. Build the two diagrams (P0.3) - framework with H-layer listener over both circles; evaluation parked.
2. Draft `docs/research/h-layer/skills-map.md` (P1.1) with the agents-vs-skills analysis and integration-point matrix.
3. Draft `docs/research/h-layer/prompt-requirements.md` (P1.2).
4. Extend the literature-review taxonomy (P3.1) and start the corpus log.
5. Create `docs/research/phd-extension-ideas.md` (P6.1).
6. Update agent memory, dashboards, wiki outbox; run health checks.
7. Prepare the 2026-07-15 open-questions list for Iris.
