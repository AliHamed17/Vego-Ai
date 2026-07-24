# Research Plan

## Topic

Reusable human judgment in AI-assisted domain modeling and model assessment.

## Main Research Question

How can reusable human judgment be captured, governed, and evaluated so that AI-assisted domain model
assessment can move from one-off expert correction toward auditable human-AI co-reasoning?

## Contribution Statement

This research contributes a human-AI co-reasoning approach for AI-assisted domain model assessment, in which
human judgment is selectively triggered, structurally captured, stored as reusable knowledge, and evaluated
under explicit evidence gates before any automated behavior change is allowed.

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
| RQ4 | Can reusable human judgment memory support later variability interpretation first as advisory evidence and then, under controlled conditions, as a deterministic memory-informed comparison? | M4A memory advice reports, planned C4B experiment, memory-informed comparison results, leakage status, comparison to non-memory conditions. |
| RQ5 | How should this artifact be positioned within human-in/on-the-loop AI, XAI, expert feedback, AI-assisted modeling, and design-science literature? | Literature-review taxonomy, claim/evidence table, thesis discussion. |

## Current Mechanism State

| Milestone | Mechanism | Status | Boundary |
| --- | --- | --- | --- |
| M1 | Human Review Queue | Implemented | Selects cases for review; does not decide them. |
| M2 | Human Feedback Manager | Implemented | Attaches validated human feedback to review items. |
| M3 | Human Judgment Memory | Implemented and published | Builds and searches reusable memory; remains inert. |
| M4A | Memory Advisory Layer | Implemented and published | Retrieves relevant memory for Agent 4 patterns and emits advisory reports; no AI classification change. |
| M4B-1 | Memory-informed parallel comparison | Implemented and merged | Deterministic controlled experiment only; writes a separate comparison artifact and keeps baseline behavior unchanged. |
| M4B-2 | Optional Agent 4/LLM reclassification | Deferred | Not approved; no Agent 4 prompt/API/embedding changes. |
| M5 | Human-approved guideline refinement | Planned PhD continuation | Future work; guideline changes require explicit approval and real-label evidence. |
| M6 | Broader evaluation and thesis synthesis | Planned PhD continuation | Consolidates evidence across additional runs, reviewers, domains, and diagrams. |

## Current Artifacts

- Source package: `VEGO-AI/`
- M1-M4B-1 human-AI co-reasoning implementation, comparison tooling, dashboards, and tests.
- Research OS registers for artifact audit, provenance, and publishability.
- Thesis drafts under `thesis/chapters/`, including a guarded Chapter 7 current-evidence draft.
- PhD control page: `docs/research/phd-thesis-optimization-plan.md`.
- Supervisor EXP-005 approval pack: `docs/research/supervisor-label-approval-pack.md`.
- Controlled local artifacts including root paper/IRB material, model files, analysis outputs, and evaluation outputs remain ignored until audit.

## Near-Term Milestones

1. Review `docs/research/supervisor-label-approval-pack.md` with the supervisor.
2. Approve reviewer plan, consent/anonymity handling, evidence target, and claim boundary.
3. Collect blind EXP-005 labels for the 24 generalization-safe rows.
4. Rerun `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream`.
5. Update Chapter 7 with real-label accuracy, macro-F1, paired-correctness, reliability, and limitations.
6. Use `docs/research/phd-thesis-optimization-plan.md` to decide the PhD continuation path after real errors are known.
7. Keep M4B-1.1, M4B-2, Agent 4 behavior changes, LLM/API calls, embeddings, and baseline overwrites blocked until real labels and explicit approval exist.
