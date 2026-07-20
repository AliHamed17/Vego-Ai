# H-Layer Prompt Requirements (Deliverable B for 2026-07-15 Meeting)

Last updated: 2026-07-03 by Claude. Status: DRAFT for supervisor review.

Source directive: Iris, 2026-07-01 meeting (21:42-22:21): "do not write the agents' prompts yet - define the REQUIREMENTS of the prompts: what to say, what context to give them, what task, what steps."

Scope note: this document intentionally contains NO prompt text. It specifies, per H-layer skill, what any future prompt must convey. Skill identifiers (S1-S7) follow `docs/research/h-layer/skills-map.md`.

## Common Requirements (all H-layer prompts)

| Aspect | Requirement |
| --- | --- |
| Identity | The agent must know it is part of the human-judgment layer of VEGO-AI, distinct from the four baseline agents, and must never alter baseline outputs directly. |
| Domain framing | Domain modeling is interpretive: a deviation may be a real mistake, a valid alternative, a domain-specific interpretation, a language-level issue, a pedagogical issue, a guideline-update candidate, or an ambiguity needing adjudication. Prompts must forbid collapsing these categories. |
| Baseline vocabulary | Substantial vs. occasional variability; Language Template; Reference Guidelines; compliance vector; identified vs. observed variability - definitions provided in context, used consistently. |
| Provenance | Every output must carry provenance: which event (E1-E13), which model/case, which run, which stage. |
| Language of record | English for artifacts; must handle Hebrew-language course materials as input. |
| Non-blocking | No skill may stall the pipeline waiting for human input; timeouts and `silent`-mode fallbacks are mandatory (Iris's dosage concern). |
| Governance | Design-only boundary: any output that affects Agent 4 classification (context injection, or corrections changing classification inputs) is implementation-blocked per `docs/agent-memory/review-state.md` until real EXP-005 label evidence justifies a reviewed deterministic policy; no M4B-2, no LLM/API reclassification, no embeddings, no baseline output overwrites. |
| Output structure | JSON conforming to the H-layer schemas (to be derived from existing `human_review_item` / `human_feedback` schemas). |

## S1 H-Listen (observation)

| Aspect | Requirement |
| --- | --- |
| Intent | Passive, complete, quiet observation - "mostly a quiet listener" (Iris, 03:42-04:24). |
| Context to provide | The event catalog E1-E15 (inter-agent exchanges, internal signals, and H-layer-internal events) with producer/consumer agents; the current run configuration; what "artifact revision" means per artifact type. |
| Task | Normalize every observed inter-agent exchange into an observation record; never interrupt, never rank. |
| Steps | Capture event -> classify event type -> extract artifact deltas (what changed between versions) -> attach provenance -> append to observation log. |
| Explicitly out of scope | Any judgment about review-worthiness (that is S2); any communication with agents or humans. |

## S2 H-Triage (decide what merits human review)

| Aspect | Requirement |
| --- | --- |
| Intent | Select the few observations worth expert time, under a configured dosage budget. |
| Context to provide | The active intervention mode (`every_decision` / `threshold` / `first_n_then_auto` / `silent`) and its parameters; confidence/uncertainty signals available per event; the expert-time budget; what has already been asked (avoid duplicate asks). |
| Task | Score each observation for review-worthiness and either drop, defer, or promote it; group related observations into one reviewable unit. |
| Steps | Read observation -> check dosage budget -> evaluate uncertainty/conflict/recurrence signals -> deduplicate against pending and past review items -> promote or park with reason. |
| Guardrails | Must respect the budget strictly; must record WHY an item was promoted (trigger reason taxonomy); must prefer early-stage events (template/guideline uncertainty) over late-stage re-litigation when budgets are tight. |

## S3 H1 Review Routing (structured review items)

| Aspect | Requirement |
| --- | --- |
| Intent | Convert promoted observations into stable, self-contained review items an expert can decide without opening the whole system. |
| Context to provide | Stable-identity rules (survives regeneration - existing M1.2 mechanism); the review-item schema; the target expert role (supervisor / TA / external). |
| Task | Produce a review item with: the question at stake, the minimal evidence bundle (artifact excerpts, model fragment, guideline text), the stage, the options considered by the AI, and what kind of answer is needed. |
| Steps | Build evidence bundle -> state the decision needed in one sentence -> attach AI's current position and confidence -> assign stable ID -> route to queue. |
| Guardrails | Self-containedness test: an expert reading only the item can decide; no leaking of a "preferred" answer that biases the expert (blind-first presentation, consistent with the EXP-005 blind-sheet principle). |

## S4 H2 Feedback Capture (structured expert feedback)

| Aspect | Requirement |
| --- | --- |
| Intent | Capture the REAL expert's decision with enough structure for audit, conflict detection, and reuse. Human expert is a person, never simulated (Iris, 05:35-08:15). |
| Context to provide | The review item; the feedback schema (label, rationale, confidence, scope of validity, reviewer identity, date); prior related judgments if any. |
| Task | Conduct a short structured dialogue that elicits: the decision, the rationale, the confidence, and the intended scope (this case only / this pattern / this course / general). |
| Steps | Present item -> collect decision -> elicit rationale (why, not just what) -> elicit confidence and scope -> confirm summary back to the expert -> persist. |
| Guardrails | Bidirectional but converging: bounded clarification turns; never proceed with an empty rationale; explicit reviewer identity (no anonymous judgments). |

## S5 H-Verify (anti-sycophancy verification)

| Aspect | Requirement |
| --- | --- |
| Intent | Behave like "a colleague at the expert's level" (Iris, 18:00-18:44): verify expert input against sources BEFORE accepting it; question, do not comply; do not flatly contradict. |
| Context to provide | The expert's input; the relevant Language Template sections; the relevant Reference Guidelines; the domain description; prior stored judgments that touch the same construct (conflict candidates). |
| Task | Check consistency of the expert input with each source; if consistent, accept; if inconsistent, generate specific questions that surface the contradiction ("this seems to contradict A, B, C - shall we discuss whether it is an error?"); never silently rewrite artifacts on expert say-so. |
| Steps | Retrieve sources -> compare claim vs. each source -> classify: consistent / possibly-inconsistent / conflicting-with-prior-judgment -> if not consistent, formulate the minimal question set -> run bounded dialogue rounds (proposal: max 2) -> outcome: accepted / revised / escalated to adjudication. |
| Guardrails | The known failure mode to prevent is sycophancy - being swept along even when the expert is wrong (TA-nonsense scenario; dropped-"not" scenario). Also prevent the opposite failure: stubborn refusal. Escalation, not deadlock. Every verification outcome is logged with the sources checked. |

## S6 H3 Judgment Memory (reusable memory)

| Aspect | Requirement |
| --- | --- |
| Intent | Store verified judgments as reusable, provenance-carrying knowledge; reached through S4/H2, not directly (Iris, 11:38-11:45). |
| Context to provide | The verified feedback record; the memory schema (pattern, scope, provenance, conflict links); existing memory entries for conflict detection. |
| Task | Decide reusability (is this judgment case-specific or pattern-level?), detect conflicts with existing memory, store with retrieval keys. |
| Steps | Extract pattern -> set scope from the expert's stated validity scope -> conflict-check -> store -> emit memory-updated event (E15 in the skills-map catalog, observable by S1). |
| Guardrails | Conflicting judgments are stored as explicit conflicts requiring adjudication, never silently overwritten; evaluation-leakage status must remain trackable (same-pattern vs. cross-setting reuse - existing leakage taxonomy is retained). |

## S7 H-Percolate (feedback integration and learning)

| Aspect | Requirement |
| --- | --- |
| Intent | "Not just save-and-retrieve - reason and learn" (Iris, 16:23-16:45): route validated judgments back so Agents 1-4 knowledge is corrected. |
| Context to provide | The validated judgment; which agent's artifact it affects (template / guidelines / inspection context / classification context); the correction-proposal format each agent accepts; loop-history for this artifact. |
| Task | Produce correction proposals: template corrections to Agent 1, guideline refinements to Agent 2, context injections for Agents 3/4 - and track whether the target agent's next iteration actually improved. |
| Steps | Map judgment to target agent(s) -> draft minimal correction proposal -> check loop-history (has this artifact been corrected for this reason before?) -> submit through the agent's extension point -> observe next iteration -> mark converged or escalate. |
| Guardrails | Convergence rules are hard requirements: bounded correction iterations per artifact per reason; idempotent proposals; no mutual re-triggering chains (Iris, 05:22-05:34: iterative improvement "without entering infinite loops where they disturb each other"). In phase one, every correction MUST receive human approval before application; automatic application is governance-blocked until the EXP-005 real-label gate passes (open question 4 in the skills map covers whether to relax this later). Any Agent-4-affecting output stays design-only per the common Governance requirement. |

## Requirements Traceability

| Meeting directive | Covered by |
| --- | --- |
| Listener over both circles, early stages | S1, S2 common requirements |
| Two functionality types: intake vs. percolation | S1-S3 vs. S4-S7 split (Option B in skills map) |
| Real human expert, never simulated | S4 intent; common requirement "Non-blocking" handles availability |
| Dosage calibration | S2 (budget), common "Non-blocking" |
| Bidirectional interfaces | S4/S5 dialogue requirements; skills-map directionality inventory |
| Learning beyond save/retrieve; correct Agents 1-4 | S7 |
| Anti-sycophancy, question-raising, convergence | S5 |
| Configurable intervention | S2 context (modes) |
| Prompt requirements, not prompts | This document's format |
