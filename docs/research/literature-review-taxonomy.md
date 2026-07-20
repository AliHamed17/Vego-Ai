# Literature Review Taxonomy

This taxonomy organizes the related work around the thesis spine: reusable human judgment in AI-assisted domain modeling and model assessment.

## Review Lens

The literature review should explain how prior work supports or fails to support this VEGO-AI design move:

> Human judgment is selectively triggered, structurally captured, and stored as reusable knowledge for future variability interpretation.

## Taxonomy

| Area | What To Look For | Relevance To VEGO-AI | Evidence To Extract |
| --- | --- | --- | --- |
| Human-in-the-loop AI | Systems where humans correct, label, approve, or supervise AI outputs. | Frames H1-H2 (review routing and structured feedback capture) as selective review and structured feedback. | Trigger policy, review workload, feedback schema, governance model. |
| Human-on-the-loop AI | Systems where humans monitor or intervene in otherwise automated decisions. | Helps position selective intervention instead of reviewing every case. | Intervention criteria, oversight boundaries, audit requirements. |
| Explainable AI | Explanations, rationales, provenance, and inspectable decision paths. | Supports transparent memory retrieval and match reasons in H3 Judgment Memory. | Explanation form, trust claims, limitations of explanation-only support. |
| Expert feedback and knowledge capture | Methods for converting expert correction into reusable rules, cases, or guidelines. | Directly motivates Human Judgment Memory. | Knowledge representation, reuse policy, conflict handling, lifecycle. |
| AI-assisted domain modeling | LLM or AI support for models, diagrams, requirements, guidelines, or conformance. | Provides the domain-specific context for VEGO-AI. | Model type, task, evaluation data, expert comparison. |
| Model assessment and variability interpretation | Techniques for comparing domain models and distinguishing valid variation from errors. | Grounds the meaning of "variability" and "assessment." | Classification scheme, metrics, examples, expert labels. |
| Human-AI co-reasoning | Shared reasoning loops where human and AI contributions remain visible. | Names the combined H-layer architecture. | Turn structure, memory, accountability, human authority. |
| Design science research | Artifact construction and evaluation as research method. | Frames VEGO-AI as artifact plus evaluation path. | Problem, objectives, artifact, demonstration, evaluation, contribution. |
| Human-in-the-loop in agentic/multi-agent LLM systems (added 2026-07-03, supervisor directive) | HITL architectures specifically for LLM agent pipelines: where the human plugs into multi-agent communication, monitoring/listener patterns, interrupt and approval mechanisms. | Directly frames the H-layer listener over VEGO-AI's artifact and Q&A circles. | Integration points, event/trigger models, monitoring granularity, blocking vs. non-blocking designs. |
| RLHF and RL+LLM feedback incorporation (added 2026-07-03, Arnon's pointer) | How human feedback improves LLM-based systems when the base model is not retrained: RLHF at training time vs. inference-time alternatives; reward models; preference learning. | Contrast class: VEGO-AI learns via memory, context injection, and guideline refinement - not fine-tuning; the survey must say how these relate. | Feedback loop mechanics, what is actually updated, sample efficiency, applicability without weight access. |
| Memory and learning in LLM agents beyond save/retrieve (added 2026-07-03) | Agent memory systems that reason over stored experience: reflection, self-correction, knowledge-base refinement, in-context learning from accumulated feedback. | Supports Iris's "reason and learn, not just save-and-retrieve" requirement and the S7 percolation design. | Memory representation, consolidation policy, how memory changes future behavior, evaluation of learning effect. |
| Sycophancy and trust calibration in LLM/agentic systems (added 2026-07-03) | Evidence and mitigations for models being swayed by user assertions; disagreement strategies; source-grounded verification of user claims. | Grounds the S5 H-Verify anti-sycophancy protocol (colleague-level questioning, convergence). | Sycophancy measurements, mitigation methods, dialogue convergence, escalation designs. |
| Configurable human-intervention policies (added 2026-07-03, Arnon) | Adjustable oversight regimes: per-decision approval, confidence-threshold routing, active-learning-style first-N calibration. | Grounds the S2 H-Triage configuration modes and the dosage question. | Policy types, cost/benefit of expert effort, threshold selection, effect on quality. |

## Course-Work Alignment (added 2026-07-03)

This taxonomy is also the scope definition for the literature survey in Pnina's research-methodology course (presentation mid-August 2026; submission end-September/October 2026). Per the 2026-07-01 supervisor meeting: cover generative-AI approaches, not only classic ML-on-the-loop; compare works; the decisive output is the gap statement - what the VEGO-AI H-layer innovates relative to each branch. Supervisors do not coach the course work itself (agreement with Pnina).

## Search And Reading Rules

- Prioritize recent peer-reviewed work on human-AI collaboration, AI-assisted modeling, model assessment, and design science.
- Capture both mechanism and evaluation: what the system does, and how the authors know it helps.
- Record when a paper only handles one-time feedback, because that contrast supports the reusable-judgment gap.
- Avoid overstating future-AI claims; connect reuse claims to concrete VEGO-AI H-layer mechanisms. M4A advisory outputs and the planned C4B comparison are PARKED evaluation-track instruments (per `docs/research/extension-plan-2026-07-supervisor-redirect.md`); cite them as future evaluation, never as near-term evidence.

## Thesis Use

Use the taxonomy to write Chapter 2 and to justify why H3 Judgment Memory is not just storage. The novelty claim (updated 2026-07-03 per the supervisor redirect) focuses on the H-layer lifecycle: a continuous listener over both agent-communication circles, selective and configurable triggering of a real human expert, structured capture with anti-sycophancy verification of expert input (S5), transparent reusable memory, and convergence-guarded percolation that corrects agent knowledge (S7) rather than only saving and retrieving. Controlled reuse in later AI interpretation (M4/C4B) belongs to the parked evaluation track and is future work in the thesis narrative, not a near-term claim.
