# Evaluating Reusable Human Judgment in AI-Assisted Model Assessment When No Independent Benchmark Exists

**Paper A — working draft (core sections). Status: draft, 2026-06-30. No accuracy-improvement claim is made
or implied anywhere in this paper.** Citations are restricted to the verified thesis reference list
(`thesis/chapters/11-references.md`). Quantitative figures are descriptive operating counts from the frozen
baseline and `reports/generated/`; they characterize feasibility, not effect.

---

## Abstract

AI-assisted assessment of domain models increasingly produces uncertainty signals and review flags, yet the
human judgments that resolve them are typically consumed once and discarded. A system that instead captures
those judgments as reusable, provenance-tracked knowledge raises an evaluation question that is harder than
it first appears: *does reusable human judgment help?* — when the repository contains no independent
benchmark, when naive labels duplicate the AI's own output, when the available sample is small, and when a
deliberately non-destructive policy may change nothing by design. This paper contributes a **bias- and
leakage-controlled evaluation methodology** for human–AI co-reasoning artifacts in exactly these conditions.
It comprises a diagnosis of why on-hand labels are inadmissible, a blind annotation protocol with
anonymization, randomization, two independent reviewers and adjudication, a per-row leakage discipline that
isolates same-pattern reuse, a sealed development/holdout split that forbids tuning on test data, and a set
of pre-committed evidence gates that bound which claims are permissible at each label count. We instantiate
the methodology on VEGO-AI, an agentic variability-assessment pipeline, and report its operating profile.
The methodology is *honest by construction*: it specifies how to obtain admissible evidence without
asserting an effect that the current evidence cannot support.

## 1. Introduction

Automated and semi-automated assessment of conceptual models must do more than detect deviation from a
reference: it must *interpret* whether a recurring deviation is a valid alternative or an error — a judgment
that depends on domain context and pedagogy and on which reasonable experts may disagree (Bian et al., 2020;
Ibáñez et al., 2025). Modern pipelines surface this difficulty as confidence scores and review flags, but
they rarely provide an operational way to incorporate the human judgment that resolves a flagged case, and
almost never a way to *reuse* that judgment when a similar case recurs.

Suppose such a reuse mechanism is built. How would one evaluate whether it helps? The obvious design —
compare the system's labels against a gold standard — fails in a common and under-discussed situation: the
only labels on hand are the author's own review files, which turn out to be *byte-identical* to the AI
output. Grading the system against those labels measures its agreement with itself. This paper addresses the
methodological problem this creates, and contributes a reusable evaluation design for human–AI co-reasoning
artifacts where benchmarks are unavailable or contaminated. We deliberately separate two questions that
design-science research requires (Hevner et al., 2004; Gregor & Hevner, 2013): whether the artifact *does
what it claims* (mechanism validity) and whether it produces a *beneficial effect* (empirical effect). This
paper concerns how to make the second question answerable *honestly*; it reports no effect.

## 2. Background and related work

Where the human sits relative to the AI distinguishes several patterns. Human-in-the-loop systems make the
human part of each decision cycle, with input consumed immediately (Mosqueira-Rey et al., 2023);
human-on-the-loop systems let the AI act autonomously with human oversight by exception (NIST, 2023). Both
share a transience problem: the human's judgment corrects the current case but is not preserved as a
retrievable asset. Human–AI co-reasoning, by contrast, treats both parties' contributions as durable,
inspectable artifacts. Guidance for when and how to involve humans (Amershi et al., 2019) and recent
domain-modeling precedents (Silva et al., 2025; Tselonis et al., 2005) motivate the design, while
explainability work argues that reuse decisions should be as inspectable as the original AI decision (Silva
Mercado, 2024). On the assessment side, LLM-as-grader studies report systematic limits precisely where
deviation is a valid alternative rather than an error (Ibáñez et al., 2025; Chen et al., 2024). Our focus is
orthogonal to all of these: not a new collaboration mechanism, but a *methodology to evaluate one* when
clean ground truth is absent.

## 3. The evaluation problem

Four obstacles make naive evaluation inadmissible.

**No independent benchmark.** In our instantiation the author-reviewed classification files are byte-identical
to the AI output for every pattern (zero field differences). They record agreement, not ground truth; using
them is circular and could detect neither the system's errors nor a reuse mechanism's effect. Independent
expert labels are therefore the only admissible ground truth.

**Same-pattern leakage.** If a human judgment about a pattern is stored in memory and then used to inform the
classification of that same pattern, any agreement between the memory-informed label and the expert label is
circular. Such cases demonstrate the retrieval *mechanism* but cannot demonstrate *generalization*.

**Conservative-policy invariance.** A non-destructive deterministic policy may, by design, propose a changed
label only under strong, conflict-free, leakage-safe disagreement. If that condition does not arise, the
policy changes nothing, and no accuracy delta is observable regardless of labeling. "Zero change" is then a
property of the policy, not only of the data — a fact any honest evaluation must state.

**Small sample.** When the unit of analysis is the recurring pattern, counts are in the tens, not thousands;
quantitative results must be framed as pilot evidence and reliability reported alongside them.

## 4. A bias- and leakage-controlled methodology

**Conditions.** The artifact is decomposed into layered conditions (C0 baseline → C1 selective review → C2
structured feedback → C3 reusable memory → C4A advisory retrieval → C4B memory-informed comparison), making
each increment separately evaluable for mechanism validity.

**Two-tier metrics.** *Primary* metrics (accuracy, macro-F1 against independent expert labels on
generalization-safe rows) measure effect and are reported only when the label gate permits. *Secondary*
metrics measure mechanism validity and are available immediately: targeting rate and trigger distribution
(C1); schema validity, rationale completeness and signature-mismatch rate (C2); advice-strength and conflict
distributions (C3/C4A); change count, escalation precision/recall and a paired-correctness table (C4B); and
inter-rater reliability (Cohen's κ) with adjudication rate.

**Blind annotation protocol.** Reviewers receive neutralized sheets carrying only pattern description,
setting, affected-case count, related guideline and cited evidence; all AI-derived fields (original label,
justification, memory advice, leakage status, ranking) are withheld. Row order is randomized separately per
reviewer, items carry anonymous IDs, two reviewers label independently, Cohen's κ is computed, and
disagreements are adjudicated by a third expert before labels are frozen.

**Leakage discipline.** Every comparison row carries a per-row `evaluation_leakage_status`
(`none`, `same_pattern_memory_used`, `same_setting_memory_used`, `cross_setting_memory_used`, `unknown`).
Same-pattern rows are excluded from all generalization-safe metrics; generalization evidence must come from
leave-one-pattern-out, cross-setting, cross-diagram, or expert-holdout designs.

**Sealed development/holdout.** Labeled rows are split into development and sealed holdout sets. All error
analysis and any policy tuning use development rows only; the holdout is evaluated exactly once, after the
refined policy is frozen. One never tunes and evaluates on the same rows.

**Pre-committed evidence gates.** Permissible claims are bounded by label count: zero safe labels → not
evaluable; 1–19 → pilot/qualitative only; ≥20 → quantitative reporting (still with stated threats);
reviewer-2/adjudication present → reliability strengthened. The gates are committed before labels are seen.

**Machine-checked discipline.** Non-destruction is enforced by const-valued schema fields
(`ai_classification_changed`, `ai_behavior_changed_in_baseline`) rather than convention, and a consistency
guard verifies a fixed set of invariants — including a claim-language check — at every change.

## 5. Instantiation on VEGO-AI (descriptive)

We instantiate the methodology on VEGO-AI (Ahmed et al., 2026), covering 179 student-model cases aggregated
into 27 recurring variability patterns across four settings (two domains × two diagram types). The artifact
exercises the full chain at this scale: 11 of 27 patterns are selectively queued; four structured feedback
entries are captured; three are promoted to provenance-tracked memory; eight patterns receive advisory
evidence (strength none 19 / weak 4 / moderate 2 / strong 2); and all 27 produce comparison records with
zero baseline classifications changed and two escalations. Leakage tagging yields 24 generalization-safe
candidates (19 `none` + 5 `cross_setting`) and 3 same-pattern rows excluded from effect metrics. These
counts are reported as evidence of feasibility and operability — *not* of accuracy. The full profile is given
in `docs/research/baseline-characterization.md`.

## 6. Discussion — transferability

Nothing in the methodology is specific to variability classification. The diagnosis (circular labels), the
leakage tags, the sealed-holdout discipline, and the evidence gates apply to any human–AI co-reasoning
artifact evaluated where benchmarks are unavailable or contaminated. The design contribution is therefore a
*template* (Gregor & Hevner, 2013) for honest evaluation of reusable-judgment systems, of which the VEGO-AI
instantiation is one situated implementation.

## 7. Threats to validity

*Construct:* the substantial/occasional distinction is interpretive; mitigated by a third "undetermined"
label, written rationales, two reviewers, and reported κ. *Internal:* anchoring bias (mitigated by blind,
randomized, anonymized sheets) and same-pattern leakage (mitigated by per-row tags and exclusion).
*External:* a single pipeline and two domains limit generalization; the methodology, not the instantiation,
is the claimed contribution. *Conclusion/reliability:* small sample and LLM non-determinism; mitigated by the
deterministic comparison and pilot-only framing below the label gate.

## 8. Conclusion

We presented an honest-by-construction methodology for evaluating reusable human judgment in AI-assisted
model assessment where no independent benchmark exists. The methodology specifies how to obtain admissible
ground truth and bounds the claims permissible at each evidence level, without asserting an effect the
current data cannot support. Its empirical instantiation — reporting targeting, escalation, and (once labels
are collected) leakage-safe accuracy and reliability — is the subject of a companion empirical study.
