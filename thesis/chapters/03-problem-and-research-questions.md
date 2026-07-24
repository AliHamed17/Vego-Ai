# Chapter 3 — Problem Definition and Research Questions

> Draft. Sources: `docs/research/research-plan.md`, `docs/research/methodology.md`. Frames the study as
> design science and fixes the research question and sub-questions.

## 3.1 Problem statement

AI-assisted assessment of domain models must do more than detect deviations from a reference; it must **interpret** them — deciding whether a recurring deviation is a valid alternative, an error, a domain-specific choice, a language-level issue, a guideline-update candidate, or an ambiguity requiring adjudication. These are judgments that depend on context, domain knowledge, and pedagogy. They cannot be reduced to a mechanical diff, and reasonable experts may disagree about them.

VEGO-AI automates this interpretation with a four-agent LLM pipeline that distinguishes substantial variability (valid alternatives) from occasional variability (errors). The pipeline produces confidence scores, review flags, and justification fields that anticipate human involvement — yet it provides no operational way to *incorporate* human judgment where it is most needed, and no way to *reuse* a judgment once made. An expert who reviews a flagged case and decides that a particular deviation is a valid alternative must communicate that decision outside the system; the next time a similar deviation appears, the expert must make the same judgment again from scratch.

The problem this thesis addresses is therefore: **how to capture human judgment about model variability as structured, reusable knowledge, and feed it back into AI-assisted assessment without replacing or corrupting the original AI pipeline.**

This problem has three dimensions. First, it is a *design* problem: what mechanisms are needed to selectively trigger human review, capture structured feedback, store reusable judgments, and retrieve them for future cases? Second, it is an *integration* problem: how can these mechanisms be added to an existing, functioning pipeline without changing its behavior or corrupting its baseline outputs? Third, it is an *evaluation* problem: how can the effect of reusable human judgment be measured honestly, given the specific evidence constraints (no independent benchmark, same-pattern leakage, small sample) that characterize this case?

## 3.2 Research question

> **RQ.** What approaches have been proposed to support human–AI collaboration in AI-assisted domain
> modeling and model assessment, and how can they inform the design of reusable human-judgment mechanisms in
> systems such as VEGO-AI?

This is a literature-review-oriented and design-science-compatible question. It asks both about the state of the art (what has been proposed) and about design implications (how prior work informs the artifact). VEGO-AI is the motivating case and the artifact, not the sole object of the review.

## 3.3 Sub-questions

The research question decomposes into five sub-questions, each addressing a distinct aspect of the human–AI collaboration design space and mapped to specific thesis chapters and milestones.

**SQ1 — Control and timing.** How do existing approaches distribute control and timing between human and AI (in-the-loop, on-the-loop, co-reasoning)? This question motivates the Selective Intervention Policy (M1) and its decision to escalate by exception rather than reviewing every case. It is addressed in Chapter 2 (§2.5) and Chapter 5 (§5.2).

**SQ2 — Direction of information.** Does information flow AI→human (explanation), human→AI (feedback), or both? This question underpins the bidirectional design of the artifact: the AI's evidence is preserved and the human's rationale is captured, stored, and resurfaced. It is addressed in Chapter 2 (§2.6) and Chapter 5 (§5.3–§5.5).

**SQ3 — Role of judgment.** Is human judgment treated as a temporary correction for current AI limits, or as an essential, reusable asset? This is the central question of the thesis, and it motivates the Human Judgment Memory (M3) as a provenance-tracked, conflict-aware store rather than a transient label buffer. It is addressed in Chapter 2 (§2.6, §2.8) and Chapter 5 (§5.4).

**SQ4 — Structure and reuse.** How (if at all) is human feedback structured, stored, and reused across cases, models, or runs? This question maps directly to the schema-validated feedback (M2), the judgment memory (M3), and the advisory retrieval (M4A). It is addressed in Chapter 5 and evaluated in Chapter 6.

**SQ5 — The MDE-assessment gap.** What gap remains specifically for interpreting *model variability*, and where does VEGO-AI sit within it? This question positions the contribution against the broader model-assessment literature and is addressed in Chapter 2 (§2.3, §2.4, §2.8).

## 3.4 Evaluation research questions and hypotheses

The main RQ and SQ1–SQ5 govern the literature synthesis and artifact design. A
separate set of empirical questions governs the accuracy-evidence phase. Keeping
these sets distinct prevents the absence of performance labels from obscuring
what the design-science work has already established.

> **E-RQ1 — Baseline errors.** Where, and in which error categories, does the
> frozen Agent 4 baseline disagree with independent expert judgment?

> **E-RQ2 — Targeting and retrieval.** Do selective review and memory retrieval
> focus attention on expert-identified baseline problems with relevant,
> scope-correct, traceable evidence?

> **E-RQ3 — Unseen paired effect.** Does a frozen deterministic parallel policy
> produce positive net correction on unseen, leakage-safe data while preserving
> baseline safety?

These questions are operationalized by four hypotheses. Their status is part of
the research result, not an implementation target that must be made positive.

| ID | Hypothesis | Current status | Decisive evidence |
| --- | --- | --- | --- |
| H1 | Selective review contains a meaningful share of expert-confirmed baseline errors. | Unproven | EXP-021 and EXP-022 |
| H2 | Human Judgment Memory retrieves relevant, scope-correct prior judgments. | Unproven | EXP-022 |
| H3 | A frozen deterministic parallel policy yields positive net correction on unseen data. | Unproven and blocked | EXP-024 pilot, then EXP-025 external replication |
| H4 | Reusable memory reduces repeated review effort without reducing escalation quality. | Unproven and not approved | EXP-026 controlled human-effort study |

The primary empirical estimand for H3 is **net correction**:
`changed-and-correct - changed-and-wrong`. This paired measure makes benefit and
harm visible. Accuracy and macro-F1 are secondary measures. A positive H3 claim
requires a separate external education-domain set with at least 30 adjudicated
generalization-safe rows and all preregistered statistical and safety criteria
to pass; the current 24-row set cannot supply that formal claim.

## 3.5 Design-science framing

The study follows a design-science research methodology (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013). The cycle proceeds through five phases:

**Problem identification.** AI-assisted model assessment needs expert judgment, but one-off review does not scale or accumulate knowledge. The problem is real, recurring, and documented in VEGO-AI's own architecture (the latent human hooks of §4.4).

**Objectives.** Design a reusable human-judgment layer that selectively triggers review, captures structured feedback, stores judgments with provenance, retrieves them as advisory evidence, and enables controlled comparison — all without modifying the host pipeline's behavior.

**Design and development.** The artifact comprises five layers (M1–M4B-1) implemented as pure-Python modules with schema-validated data structures, deterministic matching, and non-destructive parallel comparison (Chapter 5).

**Demonstration.** The artifact is demonstrated on the VEGO-AI pipeline across four settings (two domains, two diagram types), processing 179 student models aggregated into 27 variability patterns (Chapter 7).

**Evaluation.** A bias- and leakage-controlled annotation protocol defines how to obtain independent expert labels and measure the artifact's empirical effect honestly (Chapter 6). The evaluation methodology is itself a contribution.

The artifact's novelty is not "a human step" but **turning human judgment into a reusable knowledge asset** for variability assessment. Contribution types are kept distinct: a literature-review contribution (taxonomy and gap), a design contribution (the co-reasoning architecture, feedback schema, and judgment-memory concept), a technical prototype (the implemented and tested M1–M4B-1 pipeline), and a planned empirical contribution (the leakage-aware evaluation).

## 3.6 Scope and boundaries

**In scope:** selective human review triggered by AI uncertainty signals; structured, schema-validated feedback capture with signature verification; reusable judgment memory with provenance tracking, conflict detection, and explainable retrieval; advisory evidence retrieval that preserves original AI output; and a deterministic, non-destructive comparison between original and memory-informed classifications.

**Out of scope** (and explicitly blocked for this thesis): LLM-based reclassification (M4B-2); any change to Agent 1–4 prompts, logic, or API behavior; automatic guideline rewriting without human approval; embedding-based retrieval; any overwrite of the baseline evaluation outputs. These boundaries are not limitations of the design but deliberate choices that keep the artifact cleanly evaluable against the preserved baseline.

**Data scope:** the evaluation is bounded by the available data — four settings, two domains (Cheers, ParkWise), two diagram types (UCD, CD), 179 student models, 27 recurring variability patterns — and by the evidence gates of Chapter 6, which require at least 20 generalization-safe expert labels before any quantitative accuracy claim is permitted.

The following table maps the research questions to the thesis structure:

| Question | Addressed in | Artifact layer | Evaluated in |
| --- | --- | --- | --- |
| SQ1 Control & timing | Ch 2 §2.5, Ch 5 §5.2 | M1 Selective Review | Ch 7 §7.3 |
| SQ2 Information direction | Ch 2 §2.6, Ch 5 §5.3–5.5 | M2–M4A | Ch 7 §7.3 |
| SQ3 Role of judgment | Ch 2 §2.6/§2.8, Ch 5 §5.4 | M3 Judgment Memory | Ch 7 §7.3–7.4 |
| SQ4 Structure & reuse | Ch 5 §5.3–5.6 | M2–M4B-1 | Ch 6, Ch 7 |
| SQ5 MDE-assessment gap | Ch 2 §2.3/§2.4/§2.8 | — (positioning) | Ch 9 §9.1 |
| E-RQ1 Baseline errors | Ch 6 §6.10 | B0/B2 | EXP-020/021 |
| E-RQ2 Targeting & retrieval | Ch 6 §6.10 | M1/M3/M4A | EXP-022 |
| E-RQ3 Unseen paired effect | Ch 6 §6.10 | B3–B5 | EXP-023–025 |
