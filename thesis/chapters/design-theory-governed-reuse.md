# Chapter — Toward a Design Theory of Governed Human-Judgment Reuse in AI-Assisted Model Assessment

> Candidate PhD-level chapter. It abstracts the situated VEGO-AI artifact (Ch 5) into a **nascent design
> theory** (Gregor & Hevner, 2013, Level 2) and states its **testable propositions**. Consistent with the
> evidence boundary, propositions are presented as *falsifiable claims with their admissible tests and
> current status* — **none is asserted as confirmed, and no accuracy improvement is claimed.** Intended to
> follow Ch 5 (artifact) and precede/extend Ch 9 (discussion). *(Author note: ground the design-theory
> anatomy with a canonical reference before submission; flagged, not cited as present.)*

## 1. Purpose and scope

This chapter proposes a design theory for information systems that **capture, reuse, and govern human
judgment** in AI-assisted assessment of conceptual models. Its scope is the class of settings where (a)
assessment is *interpretive* — a deviation may be a valid alternative or an error (Bian et al., 2020; Ibáñez
et al., 2025); (b) an independent benchmark is *scarce or contaminated*; and (c) qualified experts may
*disagree*. It is explicitly **out of scope** where ground truth is authoritative and correctness is
unambiguous, since automated grading suffices there. Following design-science guidance (Hevner et al., 2004;
Peffers et al., 2007; Gregor & Hevner, 2013), the theory is *nascent*: specified and partially instantiated,
with its effect propositions reserved for future evaluation.

## 2. Constructs (the theory's vocabulary)

- **Reusable human judgment** — an expert decision about a pattern, persisted as a first-class, retrievable
  asset rather than a transient correction.
- **Provenance** — the chain linking a judgment to the feedback, review item, AI classification, and cases
  that produced it.
- **Leakage status** — a per-row tag recording whether (and how) memory used to inform a case derives from
  that same case, setting, or a different one.
- **Advice strength** — the graded weight (none/weak/moderate/strong) of retrieved memory as advisory
  evidence.
- **Governance mode** — the decision of whether a judgment may *advise*, *decide*, or *escalate*.
- **Evidence gate** — a pre-committed threshold (by label count and reliability) bounding which claims are
  permissible.
- **Non-destruction** — the invariant that the baseline AI output is never modified.
- **Selective intervention** — escalation of cases to humans by exception, driven by the AI's own
  uncertainty signals.

## 3. Principles of form and function

Each principle states an architectural commitment (form), the purpose it serves (function), and the
justificatory knowledge it draws on.

| # | Principle (form) | Function / rationale | Kernel knowledge |
| --- | --- | --- | --- |
| DP1 | Bidirectional explainability | AI evidence and human rationale remain mutually inspectable | XAI/traceability (Silva Mercado, 2024); HAI guidelines (Amershi et al., 2019) |
| DP2 | Structured capture | Decisions are schema-valid and machine-actionable for reuse | knowledge-reuse; auditability |
| DP3 | Reusable provenance memory | Judgments persist with origin, scope, and conflict status | HITL critique of transience (Mosqueira-Rey et al., 2023) |
| DP4 | Selective intervention | Scarce expert attention is allocated by exception | human-on-the-loop oversight (NIST, 2023; Amershi et al., 2019) |
| DP5 | Non-destruction | Effect can be measured against an uncontaminated baseline; value persists across model updates | design-science evaluation (Hevner et al., 2004) |
| DP6 | Governed reuse | Advice→decision transitions require evidence and pass gates | accountable human oversight (NIST, 2023) |
| DP7 | Leakage-aware evaluability | Reuse evidence is non-circular | experimental validity; co-reasoning precedent (Silva et al., 2025; Tselonis et al., 2005) |

## 4. Justificatory (kernel) knowledge

The theory rests on three bodies of knowledge: the design-science research paradigm and its dual
mechanism/effect evaluation stance (Hevner et al., 2004; Gregor & Hevner, 2013; Peffers et al., 2007); the
human–AI collaboration spectrum from in-the-loop through on-the-loop to co-reasoning (Mosqueira-Rey et al.,
2023; NIST, 2023; Amershi et al., 2019; Silva et al., 2025; Tselonis et al., 2005); and the assessment and
variability literatures that establish *why* the task is interpretive (Bian et al., 2020; Ibáñez et al.,
2025; Pohl et al., 2005; Metzger & Pohl, 2014). The host system is VEGO-AI (Ahmed et al., 2026).

## 5. Testable propositions

The doctoral move is to state the theory as falsifiable propositions, each with its admissible test and
current status. **No proposition below is asserted as confirmed.**

- **P1 — Targeting.** Selective intervention concentrates expert effort on patterns more likely to be
  baseline errors than an unfocused review would. *Test:* queue coverage/precision against expert errors on
  generalization-safe rows. *Status:* queue rate measured (11/27 = 40.7%); error-coverage **pending labels.**
- **P2 — Escalation without contamination.** Governed comparison can flag ambiguous cases for review while
  preserving correct baseline outputs verbatim. *Test:* escalation precision/recall plus the non-destruction
  invariant. *Status:* non-destruction **demonstrated** (0/27 changed, const-enforced); escalation precision
  **pending labels.**
- **P3 — Non-circular reuse.** Provenance plus leakage tagging yields reuse evidence that is not
  self-referential. *Test:* generalization-safe metrics computed with same-pattern rows excluded. *Status:*
  retrieval mechanism **demonstrated**; generalization-safe rows currently 0 (**pending**).
- **P4 — Justified adoption.** A deterministic policy refinement raises agreement with experts *only when*
  justified by held-out error analysis, and *without* increasing changed-and-wrong. *Test:* development
  leave-one-pattern-out, then one-shot sealed holdout. *Status:* **conditional/gated** (the current policy
  changes 0/27 by design).
- **P5 — Reviewer-grounded validity.** Inter-rater reliability bounds the trust placed in any effect
  estimate. *Test:* Cohen's κ and adjudication rate reported with every effect figure. *Status:* protocol
  ready; **pending labels.**
- **P6 — Transferability.** The principles and methodology transfer across domains, diagram types, reviewer
  panels, and model versions. *Test:* cross-setting, cross-diagram, and multi-reviewer studies. *Status:*
  **PhD-scale**; five cross-setting rows seed it; otherwise untested.

## 6. Boundary conditions

The theory applies where assessment is interpretive, benchmarks are scarce or contaminated, experts may
disagree, and reuse retains value across model updates. It does not apply where authoritative ground truth
exists and correctness is unambiguous. Its claims weaken as samples shrink and as reviewer agreement falls;
both are therefore reported, never assumed.

## 7. Evaluation criteria for the theory

Three levels, matching the evidence gates: **mechanism validity** (assessable now, by inspection and tests);
**empirical effect** (gated on ≥20 generalization-safe labels); and **generalization** (PhD-scale, multiple
runs and reviewers). A nascent design theory is judged first on the coherence and instantiability of its
principles, and only later on confirmation of its effect propositions.

## 8. Contribution positioning

In Gregor & Hevner's (2013) terms the work contributes at two levels: a **Level-1 situated implementation**
(the VEGO-AI artifact, Ch 5) and a **Level-2 nascent design theory** (this chapter). The doctoral
contribution is the *governed-reuse theory* together with its *bias-controlled evaluation methodology*, of
which VEGO-AI is one instantiation. The propositions map to the PhD research questions: P-RQ1↔DP4/P1;
P-RQ2↔DP2/DP3; P-RQ3↔P1–P3; P-RQ4↔DP6/P4; P-RQ5↔P6. This abstraction is what turns *"we built a system"*
into *"we propose principles and falsifiable propositions about a class of systems"* — the standard expected
of doctoral design-science work.
