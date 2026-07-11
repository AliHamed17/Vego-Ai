# H-Layer Prompt Requirements (July 15 Deliverable B)

> **WARNING - THIS IS NOT PROMPT TEXT.** Per Iris's explicit directive (transcript 21:42-22:21), this document defines the REQUIREMENTS of the H-layer prompts - intent, context, task, steps, guardrails - and deliberately contains no final prompt templates. Writing actual prompts is a later phase.

Last updated: 2026-07-10. Status: **PROVISIONAL DRAFT** for supervisor review. M-02 through M-05 are unrecorded; any detailed default below is a comparison parameter unless the decision register later records approval.

Purpose: July 15 deliverable B. Skill identifiers (S1-S7), events (E1-E15), and the H1/H2/H3 mapping follow `docs/research/h-layer/skills-map.md`.

## Common Requirements (all skills)

| Aspect | Requirement |
| --- | --- |
| Identity | Part of the H-layer, distinct from baseline Agents 1-4; never alters baseline outputs directly. |
| Domain framing | Domain modeling is interpretive: a deviation may be a real mistake, a valid alternative, a domain-specific interpretation, a language-level issue, a pedagogical issue, a guideline-update candidate, or an ambiguity needing adjudication - never collapse these. |
| Vocabulary | Substantial vs. occasional variability; Language Template; Reference Guidelines; compliance vector; identified vs. observed variability - defined in context, used consistently. |
| Human expert | A real person (supervisor / TA / external expert). No skill may simulate, substitute, or paraphrase-as-if-from the expert. |
| Provenance | Every output carries: event id (E1-E15), model/case, run, stage, and - for feedback - reviewer identity and date. |
| Non-blocking | No skill may stall the baseline pipeline on missing human input. On timeout, preserve baseline behavior and park the item; never apply H3 advice or a correction automatically. |
| Governance | Design-only boundary: outputs affecting Agent 4 classification are implementation-blocked until the EXP-005 real-label gate passes; no M4B-2, no LLM/API reclassification, no embeddings, no baseline overwrites (see `docs/operations/alignment-control.md`). |
| Output form | Structured records aligned with the existing review-item/feedback schema families (extension deferred to implementation phase). |

---

## Context Serialization Formats

To ensure prompt consistency, all context inputs fed into H-layer prompts must adhere to strict serialization requirements:

1. **Language Template Serialization (E1):**
   * Serialized as Markdown headers separating the active constructs, properties, and constraints, accompanied by a version diff summary:
     ```text
     [Template Version: {version}]
     [Diff vs. Previous Version]:
     - Removed: {removed_elements}
     + Added: {added_elements}
     ```
2. **Reference Guidelines Serialization (E4):**
   * Serialized as a standard CSV format with column headers: `Guideline_ID`, `Severity`, `Certainty`, `Description`.
3. **Inspector Compliance & Uncertainty Serialization (E5/E6):**
   * Grouped by case ID, listing elements and the specific failure reason:
     ```text
     [Case ID: {case_id}]
     - Element: {element_id} | Status: {status} | Reason: {rationale} | Confidence: {confidence}
     ```
4. **Historical Memory Serialization (E12/E13):**
   * Serialized as a JSON-lines array of relevant matched entries:
     ```json
     {"memory_id": "string", "decision": "string", "rationale": "string", "scope": "string"}
     ```

---

## Agent Reasoning Logic & State Machines

H-layer prompts must enforce the following explicit step-by-step reasoning logic:

### 1. S2 Triage Reasoning Loop
1. **Severity Extraction:** Scan incoming event logs and retrieve severity scores (0-3).
2. **Dosage Filtering:** Compare events where $\text{Severity} \geq \text{DosageThreshold}$; severity 2 is a replay pilot candidate, not an approved default.
3. **Case-Level Bundling:** Group all filtered events sharing the same Case ID into a single unified review item.
4. **Adaptive Budget Cap:** Sort events by instability score and discard items that exceed the setting-specific workload budget limit $K_s$.

### 2. S5 Verify (Anti-Sycophancy) Check Logic
1. **Ingest Input:** Read the submitted expert feedback decision, rationale, and scope.
2. **Retrieve Sources:** Load the relevant reference guidelines, active template, and domain description.
3. **Inconsistency Analysis:**
   * *Deterministic check:* If guideline is a core constraint and decision is reject, flag conflict.
   * *Semantic check (separately gated):* Only after deterministic source checks and separate approval, parse rationale text for possible conflict indicators. Semantic or LLM output cannot decide that a human is wrong or enter trusted memory by itself.
4. **Dialogue Branching:**
   * *No Conflict:* Mark as verified (transition to S6/S7).
   * *Conflict (Round 1):* Generate a question highlighting the specific guideline section contradicted.
   * *Conflict (Round 2):* Generate a warning prompt requiring override confirmation and justification.
   * *Escalation:* Save only to the adjudication queue as `needs_adjudication`; do not write to trusted memory and do not bypass the correction-approval gate.

### 3. S7 Generalization Logic
1. **Eligibility Gate:** Accept only S5-verified or explicitly supervisor-adjudicated records from an allowlisted trusted origin, with `trusted_memory_eligible = true`, reusable status, nonblank validity scope, and provenance. Require a separately validated, hash-bound trusted-export manifest that lists the eligible record IDs. Reject record-local assertions, demo, synthetic, and pending-adjudication records without that companion validation.
2. **Analyze Scope:** Read the expert-confirmed `validity_scope` (case, pattern, domain, general) without expanding it.
3. **Key Extraction:** Extract retrieval keys: `domain_id`, `diagram_type`, `guideline_id`, `pattern_signature`, and keywords.
4. **Conflict Search:** Query verified/adjudicated memory for matching retrieval keys. If decisions conflict, flag `active_disagreement`, route to adjudication, and synthesize nothing for that group.
5. **Proposal Package:** Produce source-linked candidate rules with `PROVISIONAL_NOT_APPLIED` and `runtime_eligible = false`. Any prompt/context delivery is an S6 proposal requiring explicit human approval and separate implementation authorization.

---

## S1 Listen

| Aspect | Requirement |
| --- | --- |
| Intent | Passive, complete, quiet observation - "mostly a quiet listener" (transcript 03:42-04:24). |
| Required context | Event catalog E1-E15 with producers/consumers; run configuration; what counts as an artifact revision per artifact type. |
| Task | Normalize every observed exchange into an observation record; never interrupt, rank, or contact anyone. |
| Expected input | Raw pipeline events from both circles plus H-layer lifecycle events. |
| Expected output | Append-only observation log entries with provenance. |
| Reasoning requirements | Delta extraction (what changed between artifact versions); event classification; no judgment of importance. |
| Guardrails | Read-only; no agent or human contact; completeness over selectivity. |
| Failure modes | Missing events (silent gaps read as "nothing happened"); event misclassification; log flooding without structure. |
| Evidence required | Observation log reproducibly derivable from run outputs; coverage checkable against the E1-E15 catalog. |
| Convergence support | None needed (no dialogue); bounded by run length. |

## S2 Classify Intervention Opportunity (Triage)

| Aspect | Requirement |
| --- | --- |
| Intent | Select the few observations worth expert time under the configured dosage budget. |
| Required context | Active dosage mode and parameters (`every_decision` / `threshold` / `first_n_then_auto` / `silent`); uncertainty/conflict signals per event; expert-time budget; pending and past review items (deduplication). |
| Task | Score observations for review-worthiness; drop, defer, or promote; group related observations into one reviewable unit. |
| Expected input | S1 observation records. |
| Expected output | Promoted candidates with explicit trigger reasons; parked items with park reasons. |
| Reasoning requirements | Uncertainty/conflict/recurrence evaluation; budget arithmetic; early-stage preference when budgets are tight (D2). |
| Guardrails | Strict budget respect; recorded promotion reasons; never promote to compensate for its own uncertainty (that is an ask, not a flood). |
| Failure modes | Over-promotion (expert overload - Iris's dosage concern); under-promotion (missed early-stage ambiguity); duplicate asks. |
| Evidence required | Trigger-reason taxonomy; per-run triage statistics (promoted/parked counts by reason). |
| Convergence support | Deduplication prevents re-asking settled questions - the primary loop-breaker at intake. |

## S3 Route To Human (Ask)

| Aspect | Requirement |
| --- | --- |
| Intent | Produce self-contained review items an expert can decide without opening the whole system. |
| Required context | Stable-identity rules (survive regeneration); review-item schema; target expert role (supervisor / TA / external). |
| Task | Build the evidence bundle (artifact excerpts, model fragment, guideline text); state the decision needed in one sentence; attach the AI's current position and confidence; assign stable ID; route. |
| Expected input | S2-promoted candidates. |
| Expected output | Routed review items presented to the human queue. |
| Reasoning requirements | Minimal-sufficient evidence selection; one-decision-per-item discipline. |
| Guardrails | Self-containedness test; blind-first presentation (do not leak a "preferred" answer that biases the expert - consistent with the EXP blind-sheet principle); respect the expert role assignment. |
| Failure modes | Items requiring system spelunking; leading questions; identity drift across regenerations. |
| Evidence required | Review items auditable end-to-end (event -> triage reason -> item -> outcome). |
| Convergence support | One decision per item keeps dialogues short and closable. |

## S4 Capture Structured Feedback

| Aspect | Requirement |
| --- | --- |
| Intent | Capture the real expert's decision with enough structure for audit, conflict detection, and reuse (H2). |
| Required context | The review item; feedback schema (decision, rationale, confidence, validity scope, reviewer identity, date); prior related judgments. |
| Task | Short structured dialogue eliciting: decision, rationale (why, not only what), confidence, and intended scope (this case / this pattern / this course / general); confirm the summary back; persist. |
| Expected input | Expert responses (E10) to routed items. |
| Expected output | Structured feedback records with full provenance. |
| Reasoning requirements | Rationale elicitation; scope disambiguation; summary faithfulness. |
| Guardrails | Bidirectional but converging (bounded clarification turns); no empty rationales; no anonymous judgments; never paraphrase the expert into a different position. |
| Failure modes | Rationale-free labels; scope inflation (case-specific ruling stored as general); summary drift. |
| Evidence required | Complete required fields on every record; expert-confirmed summaries. |
| Convergence support | Bounded clarification turns; confirmation step closes the exchange. |

## S5 H-Verify (Anti-Sycophancy)

| Aspect | Requirement |
| --- | --- |
| Intent | Behave like "a colleague at the expert's level" (transcript 18:00-18:44): verify expert input against sources BEFORE it is trusted; question, do not comply; never flatly contradict. This is directive D9. |
| Required context | The feedback record; the agreed source set (open question 2 for Iris - candidate set: Language Template, Reference Guidelines, domain description, prior stored judgments); conflict candidates from memory. |
| Task | Run deterministic checks first against the M-04-approved source subset; classify consistent / possibly-inconsistent / conflicting-with-prior-judgment; if not consistent, emit E11 and formulate the minimal question set; run the approved bounded dialogue; outcome: verified / revised / needs_adjudication. Semantic checks require separate approval. |
| Expected input | S4 feedback records + sources. |
| Expected output | Verification outcome with source versions, deterministic checks, questions, and resolution; only verified or explicitly supervisor-adjudicated records may proceed to trusted S7 storage. |
| Reasoning requirements | Source-grounded comparison; question generation that surfaces the contradiction without asserting the expert is wrong; recognizing when the SOURCE (not the expert) is what needs fixing. |
| Guardrails | Two named failure modes to prevent: sycophancy (swept along by wrong input - the TA-nonsense and dropped-"not" scenarios) and stubbornness (refusing correct input). Bounded rounds (proposal: 2) then escalation, never deadlock. Every outcome logged. |
| Failure modes | Blind compliance; endless debate; questioning tone that reads as contradiction; treating prior memory as more authoritative than the live expert without adjudication. |
| Evidence required | Verification log per feedback record: sources checked, verdicts, question rounds, final outcome. |
| Convergence support | This is the convergence-critical skill: hard round limit + escalation path is what guarantees D10. |

## S6 Integrate Feedback Back To Agents/Artifacts

| Aspect | Requirement |
| --- | --- |
| Intent | Deliver verified judgments back into the pipeline as correction proposals (E14): template corrections toward Agent 1, guideline refinements toward Agent 2, context notes toward Agents 3/4 - the "percolate back at early stages" directive. |
| Required context | The verified judgment; which artifact it affects; the correction-proposal format per agent; loop history for the target artifact; approval state. |
| Task | Draft the minimal correction proposal; check loop history; attach target hash, evidence, rollback description, and approval state; stop at the reviewable proposal in the current phase. Delivery/re-triggering requires a later, separately authorized implementation. |
| Expected input | S5-verified feedback. |
| Expected output | Approval-gated correction proposals with delivery/outcome status. |
| Reasoning requirements | Judgment-to-artifact mapping; minimality (smallest change that implements the ruling); iteration-outcome assessment. |
| Guardrails | Every correction requires human approval in phase one; Agent-4-affecting corrections are design-only (governance); idempotent proposals; bounded correction iterations per artifact per reason; no mutual re-triggering chains (transcript 05:22-05:34). |
| Failure modes | Correction storms (agents disturbing each other); scope creep beyond the ruling; silent artifact rewrites on expert say-so (must go through S5 first). |
| Evidence required | Current phase: reproducible proposal and approval-state record with zero source mutation. Future authorized phase: proposal -> approval -> delivery -> outcome chain. |
| Convergence support | Bounded iterations per artifact per reason; idempotency; explicit converged/escalated terminal states. |

## S7 Percolate / Learn / Update Knowledge

| Aspect | Requirement |
| --- | --- |
| Intent | More than save/retrieve (directive D8): maintain judgment memory (store E12, retrieve E13), detect conflicts, generalize across cases, and improve what the H-layer itself asks and checks over time. |
| Required context | Verified judgments with scope; existing memory (conflict detection); leakage taxonomy (same-pattern vs. cross-setting reuse - retained from the existing evidence discipline). |
| Task | Decide reusability level from the expert's stated scope; prepare append-only, provenance-bearing candidate memory entries; flag conflicting judgments for adjudication rather than overwriting; in the current phase, emit reviewable retrieval/generalization proposals only. Surfacing anything into S2/S3/S5 runtime context requires separate authorization. |
| Expected input | S5/S6 outcomes. |
| Expected output | Proposal-only judgment-memory entries; offline retrieval results; conflict flags; source-linked candidate rules or learning notes routed through S6; `runtime_eligible = false` until authorized. |
| Reasoning requirements | Pattern extraction; scope-respecting generalization; conflict reasoning; distinguishing "store" from "learn" explicitly. |
| Guardrails | Only verified or supervisor-adjudicated inputs are eligible; escalated overrides remain outside trusted memory; conflicts are stored as conflicts, never silently overwritten; leakage status remains trackable; rationale text is untrusted data; generalization never exceeds the expert's stated scope; every prompt/context or classification effect goes through S6's approval gate and separate implementation authorization. |
| Failure modes | Save/retrieve-only regression (the thing Iris said is insufficient); over-generalization; conflicting memory applied without adjudication. |
| Evidence required | Memory entries with provenance/scope; retrieval traces; conflict registry. |
| Convergence support | Memory-informed deduplication (via S2) stops re-litigating settled questions across runs. |

## Traceability To The 12 Supervisor Directives

| Directive (extension plan section 2) | Covered by |
| --- | --- |
| D1 Continuous listener over both circles | S1 over the full E1-E15 catalog (artifact-circle events E1, E4, E5, E7; Q&A-circle events E2, E3, E9; uncertainty signal E6; E15 routed out); skills-map matrix rows for both channels |
| D2 Early-stage intervention | S2 early-stage preference; E1-E4 coverage; skills-map stage column |
| D3 H1/H2/H3 naming, agents-vs-skills | H-mapping table (skills map section 2); options A/B/C (skills map section 6) |
| D4 M4 deferred; separate diagrams | E15 routed out; acceptance criteria below; `docs/architecture/evaluation-diagram.md` |
| D5 Real human expert | Common requirement "Human expert"; S3/S4 role handling |
| D6 Configurable dosage | S2 context + guardrails; skills-map section 3 modes |
| D7 Bidirectional interfaces | S4/S5 dialogue requirements; skills-map section 5 inventory |
| D8 Learning beyond save/retrieve | S7 intent + failure mode "save/retrieve-only regression"; S6 corrections |
| D9 Anti-sycophancy | S5 in full |
| D10 Convergence | Per-skill "convergence support" rows; S5/S6 bounds |
| D11 July 15 deliverables | This file (B) + `skills-map.md` (A) |
| D12 Survey + PhD idea log | `docs/research/literature-review-taxonomy.md` (July 2026 section) + `docs/research/phd-extension-ideas.md` |

## Acceptance Criteria

- [x] No final prompt templates anywhere in this document.
- [x] No simulated expert: the human is a real person in every skill's requirements.
- [x] S5 explicitly verifies human input against sources before it is trusted.
- [x] S7 is explicitly more than save/retrieve (learning, generalization, conflict handling).
- [x] M4/evaluation remains out of scope: E15 is routed to the parked track; no accuracy or comparison behavior is specified here.
