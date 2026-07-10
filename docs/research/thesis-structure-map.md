# Thesis Structure Map

Last updated: 2026-07-04 by Fable (Claude) - MediVARIA note in Future PhD Extension; content otherwise 2026-06-29 by Codex.

This map connects the implemented VEGO-AI artifact to the thesis argument. It keeps the system contribution, current evidence, blocked claims, and future PhD path separate.

## Core Thesis Spine

```text
Problem:
  AI-assisted domain model assessment needs human judgment for ambiguous variability.

Gap:
  Human decisions are often captured informally and are not reused systematically.

Artifact:
  VEGO-AI reusable human-judgment layer.

Mechanism:
  M1 review queue
    -> M2 structured feedback
    -> M3 judgment memory
    -> M4A advisory retrieval
    -> M4B-1 non-destructive comparison

Evaluation:
  EXP-001..EXP-005 gates, dashboard, visualizer, topology exports, and expert-label protocol.
```

## Contribution Chain

| Stage | Thesis role | Evidence status |
| --- | --- | --- |
| M1 Human Review Queue | Shows where human judgment is needed. | Implemented and testable. |
| M2 Human Feedback Manager | Captures expert decisions in structured form. | Implemented and testable. |
| M3 Human Judgment Memory | Turns reusable feedback into persistent knowledge. | Implemented and testable. |
| M4A Memory Advisory Layer | Retrieves past judgments as advisory evidence. | Implemented as advisory only. |
| M4B-1 Deterministic Comparison | Produces a parallel memory-informed comparison without changing the baseline. | Implemented, currently 0/27 changed classifications. |
| EXP-005 Real-Label Gate | Tests whether the layer improves or clarifies decisions against expert labels. | Blocked until real labels exist. |

## Chapter Draft Coverage

All ten thesis chapters now have a draft file under `thesis/chapters/`. Chapter 7 is intentionally written
as a current-evidence and results-readiness chapter: it reports mechanism/readiness evidence and records the
EXP-005 gate, but leaves quantitative accuracy, macro-F1, paired-correctness, and reliability results blocked
until independent expert labels are supplied.

## Current Evidence Boundary

Current evidence supports:

- feasibility of reusable human judgment;
- improved traceability and governance;
- review routing;
- advisory evidence retrieval;
- non-destructive comparison;
- dashboard and visual inspection.

Current evidence does not support:

- improved classification accuracy;
- generalization across held-out settings;
- automatic Agent 4 behavior changes;
- M4B-2 or LLM/API reclassification.

## HITL Literature Connection

Use `literature/hitl-resource-pack/` to frame:

- human-AI interaction guidelines;
- human oversight and risk governance;
- human-in-the-loop machine learning;
- expert-label workflow tooling;
- future active-learning or label-quality extensions.

These resources support Chapter 2 and methodology. They do not count as VEGO-AI accuracy evidence.

## Future PhD Extension

Use `docs/research/phd-thesis-optimization-plan.md` as the control page for the MSc-to-PhD trajectory. The
MSc thesis establishes the reusable human-judgment artifact and evidence gate; the PhD extension turns that
into a broader governed human-AI co-reasoning framework.

The concrete PhD umbrella is **MediVARIA** (`docs/research/medivaria/medivaria-study-plan.md`, added
2026-07-04): the medical-domain transfer of VEGO-AI + H-layer to clinical guideline adherence (justified
clinical variability vs. erroneous deviations). Thesis narrative effect: the MSc thesis is the
education-domain instantiation of a two-domain research program - use the section-7 enhancement checklist
in the MediVARIA plan for Chapters 1, 2, 3, 9, and 10 (motivation, related work via the course-survey
taxonomy branches, RQ generality, transferability discussion, future work). Thesis scope stays
education-domain; MediVARIA enters only as motivation and future work.

After real labels exist, future work may explore:

- deterministic M4B-1.1 policy refinement;
- reviewer reliability and adjudication;
- active selection of high-value review rows;
- larger cross-domain expert-label studies (MediVARIA MV-RQ1/2 being the flagship);
- M4B-2 or LLM-assisted reclassification only after strict evidence and review.
