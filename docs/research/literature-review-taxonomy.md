# Literature Review Taxonomy

This taxonomy organizes the related work around the thesis spine: reusable human judgment in AI-assisted domain modeling and model assessment.

## Review Lens

The literature review should explain how prior work supports or fails to support this VEGO-AI design move:

> Human judgment is selectively triggered, structurally captured, and stored as reusable knowledge for future variability interpretation.

## Taxonomy

| Area | What To Look For | Relevance To VEGO-AI | Evidence To Extract |
| --- | --- | --- | --- |
| Human-in-the-loop AI | Systems where humans correct, label, approve, or supervise AI outputs. | Frames M1-M2 as selective review and structured feedback. | Trigger policy, review workload, feedback schema, governance model. |
| Human-on-the-loop AI | Systems where humans monitor or intervene in otherwise automated decisions. | Helps position selective intervention instead of reviewing every case. | Intervention criteria, oversight boundaries, audit requirements. |
| Explainable AI | Explanations, rationales, provenance, and inspectable decision paths. | Supports transparent memory retrieval and match reasons in M3. | Explanation form, trust claims, limitations of explanation-only support. |
| Expert feedback and knowledge capture | Methods for converting expert correction into reusable rules, cases, or guidelines. | Directly motivates Human Judgment Memory. | Knowledge representation, reuse policy, conflict handling, lifecycle. |
| AI-assisted domain modeling | LLM or AI support for models, diagrams, requirements, guidelines, or conformance. | Provides the domain-specific context for VEGO-AI. | Model type, task, evaluation data, expert comparison. |
| Model assessment and variability interpretation | Techniques for comparing domain models and distinguishing valid variation from errors. | Grounds the meaning of "variability" and "assessment." | Classification scheme, metrics, examples, expert labels. |
| Human-AI co-reasoning | Shared reasoning loops where human and AI contributions remain visible. | Names the combined M1-M4 architecture. | Turn structure, memory, accountability, human authority. |
| Design science research | Artifact construction and evaluation as research method. | Frames VEGO-AI as artifact plus evaluation path. | Problem, objectives, artifact, demonstration, evaluation, contribution. |

## Search And Reading Rules

- Prioritize recent peer-reviewed work on human-AI collaboration, AI-assisted modeling, model assessment, and design science.
- Capture both mechanism and evaluation: what the system does, and how the authors know it helps.
- Record when a paper only handles one-time feedback, because that contrast supports the reusable-judgment gap.
- Avoid overstating future-AI claims; connect reuse claims to concrete VEGO-AI mechanisms, M4A advisory evidence, and planned C4B evidence.

## Thesis Use

Use the taxonomy to write Chapter 2 and to justify why M3 is not just storage. The novelty claim should focus on the combined lifecycle: selective trigger, structured capture, transparent reusable memory, and controlled reuse in later AI interpretation.
