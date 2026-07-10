# Chapter 10 — Conclusion and PhD Continuation

> Draft. Summarizes contributions and honest status, revisits research questions, and sets out continuation
> work. Sources: `docs/research/research-plan.md`, `docs/research/m4b1-policy-refinement-plan.md`, the
> evaluation plan.

## 10.1 Summary of contributions

This thesis extended VEGO-AI from an automated agentic model-assessment pipeline into a staged human–AI co-reasoning system. The work makes four distinct contributions:

**A literature-grounded framing** of reusable human judgment for AI-assisted model-variability assessment. The literature review (Chapter 2) identified four interrelated gaps in the surveyed work: one-way explanation, transient judgment, emphasis on generation over assessment, and unused human-review signals. The contribution is the synthesis of these gaps into a coherent problem statement and the positioning of the thesis artifact against the state of the art.

**A design comprising selective review, structured feedback, and provenance-tracked judgment memory.** The co-reasoning artifact (Chapter 5) introduces seven transferable design principles — bidirectional explainability, structured feedback, reusable human judgment, selective intervention, human authority over the rubric, separation of concerns, and future-proofing — that can inform similar human–AI collaboration systems in other domains.

**A working, non-destructive technical prototype (M1–M4B-1)** with dashboard and visualizer inspection surfaces, 94 passing tests, and full deterministic reproducibility. The prototype demonstrates the mechanism at a concrete scale (179 models, 27 patterns, 11 review items, 3 reusable memories) and preserves the original baseline throughout.

**A bias- and leakage-controlled evaluation methodology** that makes the artifact's empirical effect measurable. The methodology (Chapter 6) identifies the byte-identical baseline labels as unusable ground truth, defines a blind annotation protocol with anonymization, randomization, and two-reviewer adjudication, establishes a sealed development/holdout split for policy refinement, and pre-commits to explicit evidence gates. The methodology itself is a contribution: it provides a template for evaluating human–AI collaboration artifacts where conventional benchmarks are unavailable or unreliable.

## 10.2 Revisiting the research questions

**RQ.** The research question asked what approaches support human–AI collaboration in AI-assisted domain modeling and model assessment, and how they can inform the design of reusable human-judgment mechanisms. The thesis answered this by surveying six areas of related work, identifying four gaps, and demonstrating a concrete artifact that closes them.

**SQ1 (Control and timing):** the artifact positions itself between on-the-loop and co-reasoning, escalating by exception while making the human's rationale durable and retrievable.

**SQ2 (Information direction):** information flows bidirectionally — the AI's evidence informs the human's review, and the human's structured decision feeds forward through memory and advisory retrieval.

**SQ3 (Role of judgment):** human judgment is treated as a reusable asset, not a transient correction. The judgment memory stores it with provenance and retrieves it for similar future cases. The running example (§4.4–§7.3) illustrates this concretely: a single expert judgment about "Customer as actor" is captured, stored, retrieved as advisory evidence, and used in a controlled comparison — demonstrating the full lifecycle.

**SQ4 (Structure and reuse):** the combination of schema-validated feedback, provenance-tracked memory, explainable retrieval, and deterministic parallel comparison is novel in the model-assessment context.

**SQ5 (The MDE-assessment gap):** the thesis contributes the missing human-judgment lifecycle for variability interpretation, extending VEGO-AI's substantial/occasional distinction with reusable expert knowledge.

## 10.3 Honest status

The build and validation phase is complete. The artifact is implemented, tested (94 passing tests), merged, tagged, and governed by evidence-consistency guards that verify 18 invariants at every prompt. The evaluation methodology is designed, the annotation package is prepared with blind sheets and leakage controls, and the evaluation harness is implemented.

The empirical phase is not complete: there are zero generalization-safe expert labels, and the current deterministic policy changes zero classifications. The supportable claim at this stage is that the system enables structured, reusable human judgment with traceability, provenance, and safer escalation — not that it improves accuracy. This is an acceptable intermediate state for a design-science thesis because the artifact and methodology contributions stand on their own merits (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013), and the remaining work is clearly defined and human-gated.

## 10.4 Immediate next work (unblocks the empirical claim)

Three steps complete the empirical phase, and all are human-gated — they require supervisor approval and expert participation, not further implementation:

1. **Execute the expert-annotation protocol.** Two independent modeling experts label the 24 generalization-safe patterns using the blind sheets, following the anonymization, randomization, and neutrality controls defined in §6.6. Cohen's κ is computed from their independent labels, and a third expert adjudicates disagreements to produce frozen gold labels.

2. **Measure baseline accuracy.** The evaluation harness computes the Agent 4 baseline accuracy against the gold labels and performs error analysis on the 16 development rows, identifying which patterns the AI classifies incorrectly and whether the memory layer has relevant evidence for those errors.

3. **Conditional policy refinement.** Only if the error analysis suggests that memory-informed evidence could correct specific errors, design a deterministic M4B-1.1 refinement on the 16 development rows and evaluate it **once** on the sealed 8-row holdout — never tuning and evaluating on the same rows.

## 10.5 PhD continuation directions

The MSc thesis establishes the mechanism and methodology; several directions extend the work toward a fuller understanding of reusable human judgment in AI-assisted assessment.

**M4B-2 — LLM-assisted reclassification.** An optional, strictly experimental mode that uses Agent 4's `resolve_with_answers` skill to produce LLM-informed reclassifications based on memory evidence. This introduces LLM calls and stochasticity, requiring the same non-destructive, comparison-only guarantees and separate evaluation.

**M5 — Human-approved guideline refinement.** Studying the loop where substantial-variability judgments inform updates to the assessment rubric, under human authority. This extends the co-reasoning from classification to the assessment framework itself, addressing DP5 (human authority over the rubric) in a more ambitious form.

**Cross-context transfer.** Evaluating whether judgments transfer across settings (Cheers→ParkWise), diagram types (UCD→CD), and domains, using leave-one-pattern-out, cross-setting, and cross-domain experimental designs with larger expert panels and inter-rater reliability analysis.

**Longitudinal value.** Testing DP7 (future-proofing) directly by re-running the pipeline with newer LLMs and measuring whether the judgment memory's contribution persists, increases, or diminishes as the base model improves.

**Mixed-initiative interaction.** Extending the read-only inspection surfaces (dashboard, visualizer) into a genuine co-reasoning interface with feedback capture, real-time advisory display, and iterative refinement, while preserving the auditability and non-destruction guarantees established in this thesis.

## 10.6 Closing statement

This thesis moved VEGO-AI from "automated variability assessment" to "variability assessment with reusable human judgment." The artifact demonstrates that expert reasoning about model variability can be captured structurally, stored with provenance, retrieved as advisory evidence, and evaluated non-destructively against the original AI pipeline. Its lasting idea is methodological as much as technical: human judgment should be captured as structured, reusable, accountable knowledge — and its effect should be claimed only on the strength of leakage-aware, independently labeled evidence.
