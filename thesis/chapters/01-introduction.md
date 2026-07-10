# Chapter 1 — Introduction

> Draft. Sources: `docs/research/research-plan.md`, `docs/agent-memory/shared-state-report.md`. States the
> motivation, gap, contribution, and honest scope; makes no accuracy claim.

## 1.1 Motivation

Consider a use-case diagram submitted by a software-engineering student. The diagram models a cinema-booking system, but instead of placing *Customer* as a single actor connected to every use case, the student splits the role into *Registered Customer* and *Walk-In Customer*, each linked to different interactions. An automated grading tool that compares the submission to a single reference model would flag this as an error — the reference has one actor, the student has two. Yet a human expert, informed by domain context and pedagogical intent, might recognize the split as a valid alternative: a defensible modeling choice that reveals the student's understanding of role-based behavior, not a misconception.

This kind of interpretive judgment sits at the heart of domain-model assessment. Assessing whether a student's model is correct is not a mechanical diff against a reference; it requires reasoning about the *meaning* of deviations — whether they reflect genuine errors, valid alternatives, language-level issues, or design choices that might even improve the reference. VEGO-AI (Ahmed et al., 2026) addresses this challenge with a four-agent LLM pipeline that distinguishes **substantial variability** (valid alternatives) from **occasional variability** (errors). Unlike single-reference grading tools (Bian et al., 2019; Ibáñez et al., 2025), VEGO-AI reasons about whether a recurring deviation is a legitimate alternative or a mistake.

But VEGO-AI is fully automated. Where genuine judgment is required — about context, ambiguity, pedagogy, or whether a guideline itself should change — there is no person in the loop. The system already produces review signals (`requires_human_review`, `human_review_reason`, confidence scores) and even implements advanced skills for probing missed alternatives, yet these affordances remain latent: no human is asked, and no human response is captured. The judgment gap is not architectural but operational — VEGO-AI anticipates human involvement in its data schema but never closes the loop. A concrete instance of this gap — Agent 4 classifying "Customer as an actor" as an error when a human expert would recognize it as a valid alternative — serves as a running example throughout this thesis (§4.4, §5.6, §6.4, §7.3).

## 1.2 The gap

Across the human–AI collaboration literature, explanation flows mostly one way: systems explain *to* people — evidence, confidence, justification — but rarely ingest *why a human disagrees* (Amershi et al., 2019). Where human feedback is collected, it is typically treated as a transient correction for one case: an annotator labels a single instance, that label trains or adjusts the current model, and the judgment is consumed. It does not persist as structured, retrievable knowledge that can inform future, similar cases — it is not *reusable*.

For AI-assisted **model assessment** specifically — interpreting variability rather than generating or generically grading models — there is no established mechanism that captures human judgment as structured, reusable knowledge. The HITL literature offers patterns for selective oversight (Mosqueira-Rey et al., 2023), the XAI community provides transparency methods (Silva Mercado, 2024), and the AI governance literature establishes accountability principles (NIST, 2023). But none of these combine selective triggering, structured capture, provenance tracking, and cross-case reuse into a single operational loop for model-variability interpretation.

VEGO-AI exhibits this gap concretely: it already explains to humans and anticipates human review in its data schema, yet never captures, stores, or reuses the expert's response. The system generates review signals that go unanswered and produces AI-only classifications where a domain expert's past judgment could inform the assessment.

## 1.3 Contribution

This thesis extends VEGO-AI from an automated agentic pipeline into a staged **human–AI co-reasoning** system. The central contribution is to **transform human judgment into structured, reusable knowledge for AI-assisted domain-model assessment**. The implemented artifact proceeds in five layers:

1. **Selective review (M1):** a pure-Python intervention policy identifies cases where human judgment is most needed, based on the AI's own uncertainty signals, and produces a persistent review queue.
2. **Structured feedback (M2):** expert decisions are captured in a schema-validated format, linked to specific AI decisions by a deterministic signature, and attached to the review queue without overwriting it.
3. **Reusable judgment memory (M3):** approved, reusable feedback is promoted to a provenance-tracked memory store with conflict detection, explainable retrieval, and human-readable match reasons — without embeddings or LLM calls.
4. **Advisory retrieval (M4A):** relevant past judgments are surfaced as graded advisory evidence alongside each Agent 4 pattern, while preserving the original AI classification verbatim.
5. **Non-destructive comparison (M4B-1):** a deterministic, parallel comparison evaluates whether the memory-informed assessment would differ from the original, writing to a separate artifact and never overwriting the baseline.

The contribution is not a single "add a human step" intervention but a *complete lifecycle* for human judgment: from selective trigger through structured capture, provenance-tracked storage, advisory retrieval, and controlled comparison — each layer additive and non-destructive.

## 1.4 What this thesis does and does not claim

The thesis claims, and demonstrates, **mechanism validity**: the reusable human-judgment loop exists, is reproducible, preserves the baseline, and produces controlled artifacts for evaluating its effect. It also contributes a **bias- and leakage-controlled evaluation methodology** with an independent expert-annotation protocol that makes the artifact's empirical effect measurable.

The thesis explicitly makes **no accuracy-improvement claim**. The reason is methodological and is treated honestly throughout: there is no independent benchmark in the data (the author-reviewed labels duplicate the AI's own output byte-for-byte), and the only existing expert labels are same-pattern (leakage), giving zero generalization-safe labels. Furthermore, the current deterministic comparison policy changes zero of 27 classifications, so original and memory-informed results are identical by construction. The demonstrated value at this stage is reusable human judgment, traceability, provenance, and safer escalation; a quantitative accuracy claim awaits the independent expert annotation defined in Chapter 6.

## 1.5 Thesis structure

The remainder of this thesis is organized as follows.

**Chapter 2** surveys related work across LLM-assisted domain modeling, AI-assisted model assessment, human–AI collaboration patterns, explainability and expert feedback, and design-science methodology. It identifies the gap that motivates this work: human judgment is treated as transient correction rather than reusable knowledge.

**Chapter 3** defines the research problem and formulates the research question and five sub-questions, framed within a design-science methodology.

**Chapter 4** describes the original, unmodified VEGO-AI baseline pipeline (C0), including its four-agent architecture, evaluation pipeline, datasets, and the latent human-review affordances that motivate the thesis contribution.

**Chapter 5** presents the human–AI co-reasoning artifact (M1–M4B-1), detailing the design rationale, implementation, and schema decisions for each layer.

**Chapter 6** defines the evaluation methodology, including the conditions, metrics, leakage discipline, independent expert-annotation protocol, sealed development/holdout split, and evidence gates.

**Chapter 7** reports the experimental results available at the time of writing — mechanism evidence and prototype-scale evidence — and identifies the pending empirical results that require expert labels.

**Chapter 8** analyses threats to validity across construct, internal, conclusion, external, and ethical dimensions.

**Chapter 9** discusses the implications of the work, derives transferable design principles, compares findings with related work, and addresses each research question.

**Chapter 10** concludes the thesis, summarizes contributions and honest status, and outlines PhD continuation directions.
