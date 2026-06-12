# Research Plan

## Topic

Reusable human judgment in AI-assisted domain modeling and model assessment.

## Main Research Question

What approaches have been proposed to support human-AI collaboration in AI-assisted domain modeling and model assessment, and how can they inform the design of reusable human judgment mechanisms in systems such as VEGO-AI?

## Contribution Statement

This research contributes a human-AI co-reasoning approach for AI-assisted domain model assessment, in which human judgment is selectively triggered, structurally captured, and stored as reusable knowledge for future variability interpretation.

## Core Problem

Domain models can differ in many ways, but not every difference matters. VEGO-AI already provides a multi-agent pipeline for identifying candidate variability. The research gap is that expert judgment is often treated as a one-time correction rather than a reusable research and system asset.

This project studies how human review can move from episodic validation to reusable knowledge: uncertain or important AI classifications are routed to a human, the decision is captured in a structured schema, and approved judgments become transparent memory that can later support variability interpretation.

## Design-Science Framing

| Element | VEGO-AI Framing |
| --- | --- |
| Problem | AI-assisted model assessment needs expert judgment, but one-off review does not scale or accumulate knowledge. |
| Gap | Existing human-in-the-loop and XAI work often explains or corrects individual decisions without preserving reusable modeling judgment. |
| Artifact | VEGO-AI human-AI co-reasoning layer: selective intervention policy, human review queue, feedback manager, and human judgment memory. |
| Mechanisms | Trigger review selectively, capture decisions structurally, preserve provenance, detect conflicts, retrieve prior judgments with explainable matching, and present them as advisory evidence before behavior-changing reuse. |
| Evaluation path | Compare baseline VEGO-AI against staged human-review and memory-assisted conditions, then analyze accuracy, consistency, effort, conflict handling, and thesis-level validity threats. |

## Research Questions

| ID | Question | Evidence Needed |
| --- | --- | --- |
| RQ1 | How does VEGO-AI identify and classify variability across domain models before human intervention? | Existing evaluation outputs, case-level scores, Agent D classes, baseline agreement metrics. |
| RQ2 | Which AI classifications require human judgment, and can selective intervention reduce unnecessary expert effort? | Human Review Queue trigger reasons, queue size, coverage of uncertain or guideline-sensitive cases. |
| RQ3 | Can human feedback be captured with enough structure and provenance to support audit, conflict detection, and future reuse? | Human feedback schema, resolved queue records, validation tests, conflict cases. |
| RQ4 | Can reusable human judgment memory support later variability interpretation first as advisory evidence and then, under controlled conditions, as Agent 4 context? | M4A memory advice reports, planned C4B experiment, memory-assisted reclassification results, comparison to non-memory conditions. |
| RQ5 | How should this artifact be positioned within human-in/on-the-loop AI, XAI, expert feedback, AI-assisted modeling, and design-science literature? | Literature-review taxonomy, claim/evidence table, thesis discussion. |

## Current Mechanism State

| Milestone | Mechanism | Status | Boundary |
| --- | --- | --- | --- |
| M1 | Human Review Queue | Implemented | Selects cases for review; does not decide them. |
| M2 | Human Feedback Manager | Implemented | Attaches validated human feedback to review items. |
| M3 | Human Judgment Memory | Implemented and published | Builds and searches reusable memory; remains inert. |
| M4A | Memory Advisory Layer | Implemented and published | Retrieves relevant memory for Agent 4 patterns and emits advisory reports; no AI classification change. |
| M4B | Memory-informed Agent 4 reclassification | Design-only | Controlled experiment only; no uncontrolled behavior change. |
| M5 | Human-approved guideline refinement | Planned | Future work; guideline changes require explicit approval. |
| M6 | Evaluation and thesis synthesis | Planned | Consolidates evidence for MSc thesis and PhD continuation. |

## Current Artifacts

- Source package: `VEGO-AI/`
- M1-M4A human-AI co-reasoning implementation and tests.
- Research OS registers for artifact audit, provenance, and publishability.
- Controlled local artifacts including root paper/IRB material, model files, analysis outputs, and evaluation outputs remain ignored until audit.

## Near-Term Milestones

1. Complete the data/IRB and publishability audit for deferred artifacts.
2. Map existing packaged results into `EXP-000` without copying controlled contents into Git.
3. Ask Claude to refresh the M1-M2-M3-M4A artifact ZIP and manifest.
4. Draft M4B as a controlled experiment where relevant memory advice is provided as context for Agent 4, but do not implement it until reviewed.
5. Compare C0-C4B evaluation conditions and update the claim/evidence table.
6. Draft the MSc thesis around reusable human judgment, with M4B-M6 as the PhD continuation path.
