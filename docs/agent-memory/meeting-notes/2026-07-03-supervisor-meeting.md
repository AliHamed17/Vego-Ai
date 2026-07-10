# Supervisor Meeting Notes - 2026-07-01 Meeting (transcribed 2026-07-03)

> **SUPERSEDED (2026-07-04):** the authoritative notes for this meeting are
> `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md`, derived from the higher-quality
> transcript at `docs/video1832857678.transcript.he.md` (faster-whisper large-v3-turbo). The meeting took
> place on 2026-07-01; 2026-07-03 is the transcription date. This file is kept as a historical note only.

**Source:** `docs/video1832857678.mp4` (repo copy; recording ID video1832857678)
**Transcript:** `docs/video1832857678.transcript.he.md` (authoritative), `docs/video1832857678.transcript.he.txt` (timestamped)
**Language:** Hebrew
**Participants:** Iris (Supervisor), Ali (Student), Arnon (Collaborating faculty)
**Duration:** ~35 minutes

---

## Key Architectural Decisions

### 1. Two Communication Types in VEGO-AI Architecture

The VEGO-AI architecture has two distinct communication mechanisms between agents:

1. **Artifact-based communication**: Agents pass structured artifacts to each other
   - Language Advisor gives the Domain Advisor language templates
   - Domain Advisor gives the Model Inspector references/guidelines
   - Domain Advisor and Model Inspector pass variability information to the Variability Explorer

2. **Question-Answer (Q&A) communication**: A mechanism where agents ask clarifying questions
   - The Domain Advisor receives instructions that when it is uncertain about a topic, it should ask the Language Advisor
   - Two purposes: (a) genuinely seeking answers, (b) self-refinement through questioning

### 2. Human Expert Layer Design

**Decision:** The human expert layer should function as a **passive listener** that is active across all agent interactions.

- Most of the time it listens silently
- Selectively activates when relevant human judgment is needed
- Acts as a **feeding layer** that decides:
  - What to take from the communication flow
  - What to evaluate
  - How to route feedback back to agents

### 3. Agent Decomposition: Agents vs. Skills

**Discussion outcome:** Whether M2/M3 are separate agents or different **skills** of the same agent needs to be defined more precisely.

- The listening/decision-making phase could be one agent/skill
- The feedback integration phase could be another agent/skill
- Need to define: Are these separate agents or skills of the same agent?
- Need to specify the **skills** clearly and how they map to VEGO-AI pipeline stages

### 4. Feedback Interface Design

**Decision:** The human-AI interface must be **bi-directional**, not uni-directional.

- Many of the current architecture arrows are uni-directional
- Most connections should eventually be bi-directional
- The interface needs to be **flexible/configurable**:
  - Option A: Human approves every decision
  - Option B: Human approves only decisions below a confidence threshold
  - Option C: Selective approval based on training data patterns

### 5. Evaluation Framework

**Decision:** Two-version evaluation approach:

- **Version 0**: System without human involvement (baseline)
- **Version 1**: System with human involvement
- Compare criteria: number of errors, usability questionnaire
- Framework phase is distinct from evaluation phase

### 6. Learning from Feedback

**Key insight from Iris:** The system should not just **store** feedback in memory — it should **learn** from it.

- Not just "save and retrieve" (retrieval-based)
- Need reasoning and additional mechanisms for learning from feedback
- This connects to reinforcement learning from human feedback (RLHF) approaches
- This is a relatively new field combining deep learning with human interaction

---

## Research Direction Decisions

### Literature Survey Scope

- Focus on **agentics** and human-in-the-loop in the agent world
- Look at architectures that include human feedback in the loop
- Study how models improve through human feedback (RLHF-adjacent)
- Don't limit to just machine learning — also look at generative AI approaches
- Look at reinforcement learning from human feedback as a related field
- Expected timeline: survey complete by mid-August

### PhD Trajectory

- The project is rich enough for a doctoral extension
- Can expand to medical domain applications
- Direct-track doctorate (MSc → PhD) is possible
- Need to check administrative requirements with Sigal
- The thesis work can serve as a small study/pilot within the larger doctoral research
- Target: 3 studies for PhD, each study ~1 paper

---

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Define agent skills mapping for agents 1-4 in relation to the VEGO-AI pipeline stages | Ali | High |
| 2 | Specify prompt requirements for each agent (what context, what task, what steps) | Ali | High |
| 3 | Define interface contracts between agents (inputs/outputs at each stage) | Ali | Medium |
| 4 | Separate framework/development phase from evaluation phase clearly | Ali | Medium |
| 5 | Move M4 (evaluation) to a separate track document | Ali | Medium |
| 6 | Complete literature survey on HITL/agentic architectures | Ali | High |
| 7 | Look at RLHF and deep learning approaches for feedback learning | Ali | Medium |
| 8 | Check PhD direct-track administrative requirements with Sigal | Ali | Low |
| 9 | Consider expanding evaluation to medical domain for PhD | Iris/Ali | Low |
| 10 | Explore evaluation with teaching assistants and student cohorts | Iris | Low |

---

## Quotes & Key Phrases (Translated)

> "I see this additional layer as a listener that most of the time listens quietly, but sometimes the relevant part of the observation activates." — Iris

> "It's not just storing in memory and using it when needed — it's something smarter." — Iris

> "We are talking about the world of machine learning, so it's not just save and retrieve, but truly reasoning and additional things we need to do learning from these things." — Iris

> "The interface doesn't have to be uni-directional [...] most of them will probably be bi-directional." — Iris

> "I would be a bit careful about that, because it would require him to wait for us, and he wouldn't progress because he's not getting feedback from us." — Iris (on requiring human approval for every decision)

---

## Connection to Current Project State

These meeting insights map to the current VEGO-AI implementation as follows:

| Meeting Concept | Current Implementation | Gap |
|----------------|----------------------|-----|
| Artifact communication | M1-M4B-1 pipeline | Covered |
| Q&A communication | Not implemented | Future work |
| Passive listener layer | M4A advisory (partial) | Needs enrichment |
| Bi-directional interface | Uni-directional only | Future work |
| Configurable feedback | Not implemented | Future work |
| Learning from feedback | Memory storage only (M3) | Core PhD extension |
| RLHF connection | Not explored | Literature survey needed |
| Evaluation V0 vs V1 | EXP-001/003/005 tooling | Labels pending |
