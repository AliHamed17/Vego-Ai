# Thesis Outline

## Working Title

Reusable Human Judgment in AI-Assisted Domain Model Assessment: The VEGO-AI Case.

## Possible Chapters

1. Introduction
2. Background and Related Work
3. Problem Definition and Research Questions
4. VEGO-AI Baseline Pipeline
5. Human-AI Co-Reasoning Artifact
6. Evaluation Methodology
7. Experimental Results
8. Threats to Validity
9. Discussion
10. Conclusion and PhD Continuation

## Evidence Map

| Chapter | Needed Evidence | Source |
| --- | --- | --- |
| 1 | Problem, contribution, and research question centered on reusable human judgment. | `docs/research/research-plan.md` |
| 2 | Related work taxonomy across human-in/on-the-loop AI, XAI, expert feedback, AI-assisted modeling, co-reasoning, and design science. | `docs/research/literature-review-taxonomy.md` |
| 3 | Design-science framing and RQ mapping. | `docs/research/research-plan.md` |
| 4 | Original VEGO-AI agents and C0 baseline. | `VEGO-AI/`, `docs/research/methodology.md` |
| 5 | M1-M3 selective review, structured feedback, and reusable memory mechanisms. | `VEGO-AI/docs/human_review_queue.md`, `VEGO-AI/docs/human_feedback_manager.md`, `VEGO-AI/docs/human_judgment_memory.md` |
| 6 | C0-C4 evaluation conditions and metrics. | `docs/research/evaluation-plan.md` |
| 7 | Baseline results, review/feedback/memory outputs, and future C4 comparison. | `experiments/registry.md`, `papers/mas4models2026/claim-evidence-table.md` |
| 8 | Data, IRB, LLM drift, small-sample, and human-disagreement risks. | `docs/research/validity-threats.md`, `docs/project-management/risk-register.md` |
| 9 | Interpretation of reusable human judgment as human-AI co-reasoning. | Claim/evidence table and experiment notes. |
| 10 | M4B-M6 continuation: memory-informed Agent 4, guideline refinement, broader evaluation. | `docs/project-management/roadmap.md` |

## Milestone Story

| Milestone | Thesis Role | Status |
| --- | --- | --- |
| M1 | Shows human judgment is selectively triggered. | Implemented |
| M2 | Shows expert decisions can be structurally captured. | Implemented |
| M3 | Shows reusable human judgment can be stored, retrieved, and checked for conflicts. | Implemented and published |
| M4A | Shows reusable human judgment can be retrieved as advisory evidence for Agent 4 patterns. | Implemented and published |
| M4B | Tests memory advice as explicit Agent 4 context for reclassification. | Design-only; planned controlled experiment |
| M5 | Studies human-approved guideline refinement. | Planned PhD continuation |
| M6 | Consolidates broader evaluation and thesis evidence. | Planned |
