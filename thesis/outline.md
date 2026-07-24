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

## Draft Status

| Chapter | File | Status |
| --- | --- | --- |
| 1 Introduction | `thesis/chapters/01-introduction.md` | Draft (unblocked) |
| 3 Problem & Research Questions | `thesis/chapters/03-problem-and-research-questions.md` | Draft (unblocked) |
| 4 VEGO-AI Baseline Pipeline | `thesis/chapters/04-vego-ai-baseline-pipeline.md` | Draft (unblocked; system-grounded) |
| 5 Human–AI Co-Reasoning Artifact | `thesis/chapters/05-human-ai-co-reasoning-artifact.md` | Draft (unblocked; system-grounded) |
| 6 Evaluation Methodology | `thesis/chapters/06-evaluation-methodology.md` | Draft enhanced with B0–B5, EXP-019–027 preregistration, paired statistics, and stop rules |
| 8 Threats to Validity | `thesis/chapters/08-threats-to-validity.md` | Draft (unblocked) |
| 9 Discussion | `thesis/chapters/09-discussion.md` | Draft (unblocked) |
| 10 Conclusion & PhD Continuation | `thesis/chapters/10-conclusion-and-phd-continuation.md` | Draft (unblocked) |
| 2 Background & Related Work | `thesis/chapters/02-background-and-related-work.md` | Draft (verified citations: paper bibliography + resource pack) |
| 7 Experimental Results | `thesis/chapters/07-experimental-results.md` | Current evidence and baseline-progress draft; accuracy panels intentionally not computable at safe N=0 |

**Full thesis structure now includes:** Abstract (`00-abstract.md`), 10 body
chapters, References (`11-references.md`), Appendix A
(`appendix-a-supplementary.md`), Mermaid figures, and the AI review-loop
architecture. On 2026-07-24 the empirical plan was extended with E-RQ1–E-RQ3,
H1–H4, a B0–B5 evidence ladder, EXP-019–EXP-027, a fixed primary paired
estimand, reviewer calibration, a 16/8 development/holdout discipline, and an
external education-domain gate. Ch 7 reports mechanism and tooling evidence
now; every expert-dependent accuracy field remains blank/not computable at safe
N=0.

## Evidence Map

| Chapter | Needed Evidence | Source |
| --- | --- | --- |
| 1 | Problem, contribution, and research question centered on reusable human judgment. | `docs/research/research-plan.md` |
| 2 | Related work taxonomy across human-in/on-the-loop AI, XAI, expert feedback, AI-assisted modeling, co-reasoning, and design science. | `docs/research/literature-review-taxonomy.md` |
| 3 | Design-science framing and RQ mapping. | `docs/research/research-plan.md` |
| 4 | Original VEGO-AI agents and C0 baseline. | `VEGO-AI/`, `docs/research/methodology.md` |
| 5 | M1-M3 selective review, structured feedback, and reusable memory mechanisms. | `VEGO-AI/docs/human_review_queue.md`, `VEGO-AI/docs/human_feedback_manager.md`, `VEGO-AI/docs/human_judgment_memory.md` |
| 6 | C0-C4B conditions, B0-B5 maturity, EXP-019-027 preregistration, metrics, statistics, and stop rules. | `docs/research/thesis-evidence/PREREGISTRATION_EXP019_027.md` |
| 7 | Baseline progress, review/feedback/memory outputs, empty safe-N=0 performance panels, and future paired comparison. | `docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json`, `experiments/registry.md` |
| 8 | Data, IRB, LLM drift, small-sample, and human-disagreement risks. | `docs/research/validity-threats.md`, `docs/project-management/risk-register.md` |
| 9 | Interpretation of reusable human judgment as human-AI co-reasoning. | Claim/evidence table and experiment notes. |
| 10 | M4B-M6 continuation: memory-informed parallel comparison, possible later Agent 4/LLM mode, guideline refinement, broader evaluation. | `docs/project-management/roadmap.md` |

## Milestone Story

| Milestone | Thesis Role | Status |
| --- | --- | --- |
| M1 | Shows human judgment is selectively triggered. | Implemented |
| M2 | Shows expert decisions can be structurally captured. | Implemented |
| M3 | Shows reusable human judgment can be stored, retrieved, and checked for conflicts. | Implemented and published |
| M4A | Shows reusable human judgment can be retrieved as advisory evidence for Agent 4 patterns. | Implemented and published |
| M4B-1 | Tests memory advice as a deterministic parallel comparison while preserving original Agent 4 output. | Implemented historically; current 0 / 27 changes |
| M4B-2 | Tests optional Agent 4/LLM-assisted reclassification. | Deferred; not approved |
| M5 | Studies human-approved guideline refinement. | Planned PhD continuation |
| M6 | Consolidates broader evaluation and thesis evidence. | Planned |

## Thesis-Ready Tables To Maintain

### Contribution Chain

| Layer | What it contributes | Current evidence |
| --- | --- | --- |
| M1 Human Review Queue | Selectively triggers human judgment where VEGO-AI needs review. | Implemented; dashboard/report counts available. |
| M2 Feedback Manager | Captures human decisions structurally. | Implemented; resolved feedback records available. |
| M3 Human Judgment Memory | Stores reusable human judgment with provenance. | Implemented; reusable memory entries available. |
| M4A Memory Advisory | Retrieves memory as advisory evidence. | Implemented; advice outputs preserve `ai_classification_changed=false`. |
| M4B-1 Parallel Comparison | Compares original Agent 4 and memory-informed assessment non-destructively. | Implemented; 0 / 27 memory-informed classifications differ from original. |

### Evidence Gates

| Gate | Threshold | Thesis interpretation |
| --- | --- | --- |
| 0 safe EXP-005 labels | Current blocked state | Accuracy improvement cannot be evaluated. |
| 1-19 safe EXP-005 labels | Pilot only | Report as exploratory evidence with validity threats. |
| 20+ safe EXP-005 labels | Quantitative allowed | Report original vs memory-informed vs expert labels, still with limitations. |
| Reviewer-2/adjudication present | Reliability strengthened | Use for stronger claims about expert-label validity. |
| 8 sealed holdout rows | Pilot only | Open once after a candidate is frozen; no formal improvement claim. |
| ≥30 new external safe labels | Formal gate eligible | Claim only if bootstrap, McNemar, macro-F1, subgroup, and safety gates all pass. |

### Validity Threats

| Threat | Required handling |
| --- | --- |
| Same-pattern leakage | Report as mechanism validation only. |
| Synthetic EXP-004 gains | Report as policy-risk screening only. |
| Single-reviewer labels | Treat as preliminary unless adjudicated. |
| Small sample | Report pilot-only below 20 safe labels. |
| Data/IRB sensitivity | Use aggregate summaries until publishability is approved. |

### Current EXP-005 Status

| Item | Current value |
| --- | ---: |
| Label rows | 27 |
| Generalization-safe candidates | 24 |
| Supplied labels | 0 |
| Complete valid labels | 0 |
| Generalization-safe valid labels | 0 |
| Current verdict | Accuracy improvement cannot be evaluated yet. |

### Supervisor Decisions Needed

| Decision | Needed output |
| --- | --- |
| Label protocol approval | Confirm allowed labels and confidence/rationale expectations. |
| Reviewer plan | Decide whether supervisor adjudicates directly or a second reviewer labels first. |
| Minimum evidence target | Confirm 20 safe labels minimum and 24 current safe candidates as immediate target. |
| Claim boundary | Confirm no accuracy-improvement claim before EXP-005 passes. |
| Future policy gate | Decide whether M4B-1.1 can be designed only after real-label error analysis. |

Supervisor-facing approval pack: `docs/research/supervisor-label-approval-pack.md`.
