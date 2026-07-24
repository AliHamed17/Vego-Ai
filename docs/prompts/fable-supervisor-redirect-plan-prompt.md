# Fable Prompt: Implement the July 2026 Supervisor Redirect Plan

You are Fable working in the local repository:

`C:\Users\ahamed\vego-ai`

Your job is to implement the documentation/research plan created from the 2026-07-01 supervisor meeting transcript. The plan is documentation, architecture, thesis framing, and research planning work only. Do not implement VEGO-AI source-code behavior changes.

## Mission

Create the missing supervisor-redirect package that reframes VEGO-AI from an evaluation-first M-pipeline story into a framework-first Human layer story.

The July 1 supervisor guidance redirects the project:

1. The human layer must become a continuous listener over both VEGO-AI communication circles:
   - the artifact circle: Language Template -> Reference Guidelines -> variability outputs;
   - the Q&A circle between agents.
2. The human layer intervenes early, not only after Agent 4 classifies.
3. Rename the current M1/M2/M3 conceptual framing to H1/H2/H3 where appropriate, with "H" standing for human. Decide whether H1/H2/H3 are separate agents or skills of one or more agents.
4. Defer M4. M4 belongs to evaluation, not the framework. Keep framework and evaluation in separate diagrams.
5. The human expert is a real person, not a simulated agent. Do not describe the expert as synthetic, automated, or replaceable by an LLM.
6. Add configurable human-intervention dosage:
   - every-decision intervention;
   - confidence-threshold intervention;
   - first-N examples with human feedback, then automatic generalization.
7. Make interfaces bidirectional where the meeting indicated one-way arrows are insufficient.
8. Go beyond save/retrieve memory. Human feedback must support learning or correction of Agent 1-4 knowledge, not only retrieval of stored feedback.
9. Add anti-sycophancy: the H-layer must verify human input against sources and raise questions when human feedback conflicts with evidence, rather than blindly comply.
10. Guarantee convergence: the human-AI interaction should not become an infinite back-and-forth.
11. For the July 15 meeting, prepare:
    - a skills map of the H-layer versus Agents 1-4;
    - prompt requirements for the H-layer skills, not final prompts.
12. Keep a literature survey direction for Pnina's course and a PhD idea log, with the medical domain as the preferred extension.

## Hard Boundaries

Follow these exactly:

- Do not edit implementation paths under `VEGO-AI/framework/`, `VEGO-AI/schemas/`, `VEGO-AI/tests/`, `VEGO-AI/eval/`, `VEGO-AI/inputs/`, `VEGO-AI/docs/memory_*`, or `VEGO-AI/docs/*advisor*`.
- Do not change Agent 4 behavior.
- Do not implement M4B-1.1, M4B-2, LLM/API calls, embeddings, baseline overwrites, or `VEGO-AI/eval_output` changes.
- Do not invent or auto-fill EXP-005 labels.
- Do not claim accuracy improvement. EXP-005 remains the real-label gate and is parked as the future evaluation track.
- Do not treat synthetic or same-pattern evidence as real expert evidence.
- Do not make the human expert a simulated LLM agent.
- Do not merge framework and evaluation into one diagram.
- Do not write secrets, credentials, private personal data, or raw sensitive meeting content beyond what is necessary for research notes.

## Required Startup

Before editing:

1. Run:

   ```powershell
   .\scripts\refresh-tracking.ps1 -Pull
   ```

2. Read:

   - `AGENTS.md`
   - `CLAUDE.md`
   - `docs/agent-memory/compiled-memory.md`
   - `docs/PROGRESS_TRACKER.md`
   - `docs/operations/alignment-control.md`
   - `docs/research/thesis-structure-map.md`
   - `docs/research/phd-thesis-optimization-plan.md`
   - `docs/video1832857678.transcript.he.md`
   - `docs/video1832857678.transcript.he.txt`

3. Check Git status before making claims about tracked/untracked files.

## Primary Source

Use the Hebrew transcript files as the meeting source:

- `docs/video1832857678.transcript.he.md`
- `docs/video1832857678.transcript.he.txt`

The transcript was generated locally from `docs/video1832857678.mp4` using `faster-whisper large-v3-turbo` against the matching Zoom audio stream. Treat it as machine-generated: it is good enough for planning, but verify key claims against repeated transcript evidence and avoid over-quoting.

## Deliverables To Create Or Update

Create the following files if missing. If any already exist, reconcile and improve them rather than duplicating.

### 1. Meeting Notes

Create:

`docs/research/meetings/2026-07-01-supervisor-meeting-iris.md`

Required structure:

- Title and metadata:
  - date: 2026-07-01
  - participants: Ali, Iris, Arnon where supported by transcript
  - source: `docs/video1832857678.transcript.he.md`
  - status: machine-transcript-derived, needs human review for exact wording
- Executive summary:
  - one paragraph explaining that Iris redirected the project toward framework design before evaluation.
- Key directives:
  - continuous human listener over artifact and Q&A circles;
  - early-stage intervention;
  - H1/H2/H3 naming;
  - M4 deferred to evaluation;
  - real human expert;
  - configurable dosage;
  - bidirectional interfaces;
  - learning beyond save/retrieve;
  - anti-sycophancy and convergence;
  - July 15 deliverables;
  - literature survey and PhD extension.
- Decisions and implications:
  - distinguish framework design from evaluation design;
  - park EXP-001..EXP-005 as future evaluation evidence;
  - preserve the current evidence boundaries.
- Action items:
  - Ali: prepare skills map and prompt requirements by July 15.
  - Ali: ask Sigal about direct-track course credits/admin details.
  - Ali/Fable/Codex: update research docs and diagrams.
- Open questions:
  - Are H1/H2/H3 separate agents or skills?
  - What intervention dosage is acceptable for early prototype?
  - Which exact Agent 1-4 events should the H-layer observe?
  - What source set should H-Verify use?
  - What convergence policy should stop human-AI loops?

### 2. Main Extension Plan

Create:

`docs/research/extension-plan-2026-07-supervisor-redirect.md`

Required purpose:

This is the central plan document. It should be the file another agent reads first to understand the July 2026 supervisor redirect.

Required sections:

1. Context and scope
   - Explain that the current repo has strong evaluation tooling, dashboards, EXP-001..005, and evidence gates.
   - Explain that the supervisor redirect asks for a better framework architecture first.
2. Transcript-derived directives
   - Trace each directive to a transcript-derived interpretation.
3. Gap analysis against current repo state
   - Current repo: M1/M2/M3/M4A/M4B-1 memory/evaluation framing.
   - Required: H-layer framework with listener, verifier, integrator, and bidirectional interfaces.
   - Current repo: EXP-005 blocked by real labels.
   - Required: do not delete evaluation work; park it as the future evaluation track.
4. Target architecture
   - H-layer listens to artifacts and Q&A.
   - H-layer skills:
     - S1 Listen
     - S2 Classify intervention opportunity
     - S3 Route to human
     - S4 Capture structured feedback
     - S5 H-Verify, anti-sycophancy/source-grounded challenge
     - S6 Integrate feedback back to agents/artifacts
     - S7 Percolate/learn/update knowledge
   - Include H1/H2/H3 mapping:
     - H1: human review/intervention detection
     - H2: human feedback interface and capture
     - H3: human-judgment memory/learning/reuse
   - Keep M4 as evaluation-only.
5. Phased plan with dates
   - P0: Realignment and source capture
   - P1: July 15 package
   - P2: Detail specs
   - P3: Literature survey for Pnina's course
   - P4: Framework + survey paper by September/October
   - P5: Parked evaluation track
   - P6: PhD trajectory
6. Governance reconciliation
   - Keep EXP-005 gate.
   - No source behavior changes on `main`.
   - No invented labels.
   - No accuracy claims.
7. Risks and mitigations
   - Human availability bottleneck: configurable dosage.
   - Human sycophancy risk: H-Verify.
   - Infinite interaction loops: convergence policy.
   - Evaluation premature: separate evaluation diagram.
   - Scope creep into source code: documentation-only boundary.
8. Acceptance checklist
   - all directives covered;
   - no VEGO-AI source changes;
   - diagrams separated;
   - docs linked from relevant indexes;
   - validations passed.

### 3. H-Layer Skills Map

Create:

`docs/research/h-layer/skills-map.md`

Required content:

- Purpose: July 15 deliverable A.
- Inputs:
  - `docs/video1832857678.transcript.he.md`
  - `docs/research/extension-plan-2026-07-supervisor-redirect.md`
- Define 15 observable events E1-E15 across Agents 1-4. Use concrete VEGO-AI pipeline events, for example:
  - E1 Language Template created or revised
  - E2 Domain Advisor requests clarification
  - E3 Language Advisor answers Q&A
  - E4 Domain Advisor creates Reference Guidelines
  - E5 Model Inspector applies guidelines
  - E6 Model Inspector emits uncertainty
  - E7 Variability Explorer receives artifact
  - E8 Agent 4 classifies variability
  - E9 Q&A reveals template ambiguity
  - E10 Human feedback received
  - E11 Feedback conflicts with source evidence
  - E12 Feedback approved and stored
  - E13 Prior feedback retrieved
  - E14 Knowledge correction needed for an agent
  - E15 Evaluation event, parked outside framework
- Define seven skills:
  - S1 Listen
  - S2 Triage intervention
  - S3 Ask human
  - S4 Capture feedback
  - S5 H-Verify
  - S6 Integrate
  - S7 Percolate/learn
- Include a matrix:
  - rows: Agents 1-4 and artifact/Q&A channels
  - columns: S1-S7
  - mark observe, interrupt, ask, verify, integrate, learn
- Include an interface-direction inventory:
  - current likely one-way arrows;
  - required bidirectional arrows;
  - where bidirectionality should be delayed or configurable.
- Include architecture options:
  - Option A: H1/H2/H3 as separate agents
  - Option B: Observer + Integrator with multiple skills
  - Option C: one H-agent with skill modules
  - Recommend Option B unless the repo evidence suggests otherwise.
- Include open questions for Iris:
  - exact human intervention dosage;
  - acceptable source set for H-Verify;
  - how to represent H1/H2/H3 in the diagram;
  - whether course staff can act as early human experts;
  - what July 15 output format she prefers.

### 4. H-Layer Prompt Requirements

Create:

`docs/research/h-layer/prompt-requirements.md`

This file must not contain final prompt text. It should define requirements only.

Required sections:

- Purpose: July 15 deliverable B.
- For each skill S1-S7, specify:
  - intent;
  - required context;
  - task;
  - expected input;
  - expected output;
  - reasoning requirements;
  - guardrails;
  - failure modes;
  - evidence required;
  - how it supports convergence.
- Include traceability table back to the 12 supervisor directives.
- Include "not prompt text" warning at top.
- Include acceptance criteria:
  - no final prompt templates;
  - no simulated expert;
  - S5 explicitly verifies human input;
  - S7 is more than save/retrieve;
  - M4/evaluation remains out of scope.

### 5. Framework Diagram

Create:

`docs/architecture/framework-diagram.md`

Required:

- Mermaid diagram only plus concise explanation.
- Show the framework architecture:
  - Agents 1-4;
  - artifact circle;
  - Q&A circle;
  - H-layer listener;
  - H1/H2/H3 or H skills;
  - real human expert interface;
  - H-Verify anti-sycophancy step;
  - bidirectional feedback routes.
- Do not include evaluation metrics, EXP-005, accuracy comparison, version 0/version 1, or usability questionnaire here.
- Clearly label M4/evaluation as "not in this diagram".

### 6. Evaluation Diagram

Create:

`docs/architecture/evaluation-diagram.md`

Required:

- Mermaid diagram only plus concise explanation.
- Show evaluation as parked/future:
  - framework v0: no H-layer or minimal H-layer;
  - framework v1: H-layer enabled;
  - course-team evaluation;
  - possible Stockholm/Belgium expansion;
  - usability questionnaire;
  - EXP-005 real labels as the current evidence gate;
  - no quantitative claim until labels exist.
- Do not wire M4 into the framework diagram.

### 7. Literature Survey Scope

Update:

`docs/research/literature-review-taxonomy.md`

Add a July 2026 section for the supervisor redirect. Include:

- agentic human-in-the-loop architectures;
- human-AI collaboration in multi-agent systems;
- RLHF, reinforcement learning, and LLM feedback learning, but distinguish from direct model training when not applicable;
- agent memory and learning from feedback;
- anti-sycophancy/source-grounded challenge;
- intervention policies and human workload/dosage;
- evaluation of human-AI systems with usability and correctness measures.

Do not fabricate citations. If adding citation placeholders, label them as "to be sourced".

### 8. PhD Extension Ideas

Create:

`docs/research/phd-extension-ideas.md`

Required:

- Purpose: lightweight idea log, not a commitment.
- Mention medical domain transfer as the preferred extension discussed by Iris/Arnon.
- Add five seed ideas:
  1. H-layer transfer to medical model assessment.
  2. Human-dosage policies across domains.
  3. Source-grounded anti-sycophancy for expert feedback.
  4. Cross-institution evaluation with modeling courses.
  5. Longitudinal human-judgment memory and learning.
- For each idea include:
  - research question;
  - required evidence;
  - possible study;
  - risks;
  - relation to MSc thesis.
- Include an admin note:
  - ask Sigal / graduate authority about direct-track PhD requirements and course credits.

### 9. Index And Memory Updates

Update where appropriate:

- `docs/research/README.md`
- `docs/architecture/README.md`
- `docs/architecture/project-map.md`
- `docs/agent-memory/current-state.md`
- `docs/agent-memory/progress.md`
- `docs/agent-memory/issues.md` if you identify a real new open issue
- `docs/agent-memory/decisions.md` if you make a durable decision
- `docs/agent-memory/revert-log.md`

Use concise entries. Do not bloat memory.

## Quality Review Before Finish

Run an adversarial review on your own docs before finalizing:

1. Coverage lens:
   - Check every one of the 12 supervisor directives appears in at least one deliverable.
2. Consistency lens:
   - Framework diagram and evaluation diagram are separate.
   - H1/H2/H3 naming is consistent.
   - M4 remains evaluation-only.
   - H-Verify happens before feedback is treated as trusted knowledge.
3. Governance lens:
   - No source implementation files changed.
   - No EXP-005 labels invented.
   - No accuracy claims added.
   - No simulated human expert language.
4. Operational lens:
   - New files are linked from indexes.
   - Memory and progress reflect the work.
   - Rollback notes list every changed file group.

If you find defects, fix them before the final answer.

## Validation Commands

At minimum run:

```powershell
git status --short
python scripts\check_evidence_consistency.py
.\scripts\refresh-tracking.ps1 -Viz
.\scripts\build-confluence-wiki.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox
```

If you edit PowerShell scripts, also run parser checks. This task should not require script edits.

## Required Finish

Before the final response, run:

```powershell
.\scripts\agent-memory-finish.ps1
```

Use the current script's required parameters. Include:

- summary of created files;
- commands run and pass/fail status;
- rollback note;
- next action: review open questions with Iris before July 15 and ask Sigal about direct-track credits.

Then run:

```powershell
.\scripts\refresh-tracking.ps1 -Viz
.\scripts\build-confluence-wiki.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox
```

If live Confluence sync is blocked because IDs/access are missing, report that clearly and treat `docs/confluence/outbox/` as the pending sync pack.

## Final Response Format

Return a concise implementation summary with:

- created/updated files;
- validation results;
- any blocked live sync;
- the two human-only next actions:
  - confirm open questions with Iris before July 15;
  - ask Sigal about direct-track PhD credits/requirements.

Do not include a long transcript excerpt in the final response.
