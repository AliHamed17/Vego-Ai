# Thesis-Defense Q&A Preparation

> Anticipated examiner questions with honest, grounded answers. **No accuracy-improvement claim is made;**
> the strategy is to present the bounded evidence position as a strength. Grounds: Ch 6–10, Appendix A,
> `experiments/registry.md`, `results-deepdive-and-phd-roadmap.md`. Date: 2026-06-30.

## A. The evidence boundary ("you have no results")

**Q1. You report no accuracy improvement — so what is the contribution?**
Three things, none of which requires an accuracy number. (1) A working, non-destructive co-reasoning
*artifact* (M1–M4B-1). (2) A bias- and leakage-controlled *evaluation methodology* for a setting with no
clean benchmark — the transferable contribution. (3) A precisely-bounded, falsifiable *evidence position*.
In design-science terms (Hevner et al., 2004; Gregor & Hevner, 2013) this is a Level-1 situated artifact
plus Level-2 nascent design theory; effect measurement is the explicitly-scoped next stage.

**Q2. Isn't "0 of 24 labels" a failure?**
No — it is a controlled state, not a stalled one. We identified exactly what evidence is missing
(independent expert labels), built the instrument to process it (the evaluation harness), designed the
protocol to obtain it without bias or leakage, and pre-committed the gates that bound claims. The distance
between "mechanism ready" and "empirical proof" is as narrow and well-defined as it can be without the
labels themselves.

**Q3. Why not just label the data yourself?**
Because the only on-hand labels are byte-identical to the AI output (0 field differences) — using them grades
the system against itself. Admissible ground truth must be independent, and bias control requires reviewers
who are blind to the AI's answer; a single self-labeling pass would reintroduce exactly the circularity the
methodology is designed to prevent.

## B. Methodology

**Q4. The policy changes 0 of 27 classifications — isn't that a null result?**
"Zero change" is partly a *property of the conservative policy*, not only of the data: v1 proposes a change
only on strong, conflict-free, leakage-safe disagreement, which did not occur. So a delta is structurally
unobservable under v1, and the honest near-term story is *targeting and escalation* (which patterns get
routed to a human), not relabeling. A relabeling delta becomes possible only if a refined policy (M4B-1.1)
is justified by development-row error analysis and evaluated once on a sealed holdout.

**Q5. How do you prevent leakage and overfitting?**
Every comparison row carries a per-row `evaluation_leakage_status`; same-pattern rows are excluded from all
generalization-safe metrics. Any policy refinement uses a 16-row development set only and is evaluated
exactly once on an 8-row sealed holdout, under leave-one-pattern-out — never tuning and testing on the same
rows. The analysis plan is pre-registered before labels are seen.

**Q6. Why is the unit of analysis the pattern (27), not the student model (179)?**
The judgment being captured is about a *recurring deviation pattern* (e.g., "Customer as actor"), which is
the level at which an expert decision generalizes and is reused. The 179 models are aggregated into 27
patterns by the baseline; reuse and evaluation therefore operate at pattern level.

## C. Validity and scale

**Q7. 27 patterns, 24 safe, 8 holdout — how can this carry a doctorate?**
It carries the *MSc* (mechanism + methodology), not the PhD. The PhD broadens it (roadmap phase P4): a second
annotated run, more domains, diagram types, and reviewers, with reliability reported throughout. The thesis
is deliberately framed so its contribution rests on methodology and governed reuse, which do not depend on a
large positive effect from a small sample.

**Q8. Single domain and a single pipeline — what about external validity?**
Acknowledged as the primary external-validity threat. Two mitigations: the design principles and the
evaluation methodology are framed as transferable (the artifact is one situated instantiation), and five
rows already use cross-setting memory, seeding the cross-setting transfer question that P4 expands.

**Q9. The substantial/occasional distinction is subjective — how is that valid ground truth?**
It is an expert judgment, not a fact, so the protocol treats it as such: a third "Undetermined" label,
mandatory written rationales, two independent reviewers, Cohen's κ reported alongside any accuracy figure,
and third-reviewer adjudication of disagreements. The reliability of the ground truth is reported, not
assumed.

## D. Positioning

**Q10. How is this different from human-in-the-loop ML?**
HITL consumes the human's input into the current model iteration and discards it (Mosqueira-Rey et al.,
2023). Here the judgment is *persisted* with provenance, *retrieved* for similar future cases, and *governed*
(advise vs. decide vs. escalate). The distinctive move is durability, reuse, and governance — not adding a
human step.

**Q11. Why not just use a stronger LLM or fix Agent 4 directly?**
A model update may reduce some errors but cannot encode institution-specific norms, pedagogy, or precedent —
which is what the judgment memory stores. The contribution is also deliberately *non-destructive*: the
baseline is never modified, so the human-judgment asset retains value across model versions and the effect
can always be measured against an uncontaminated baseline.

## E. Practical

**Q12. What if the labels eventually show no benefit — or a negative one?**
That is an admissible, reportable outcome, and the thesis is structured to survive it: the contribution is
mechanism + methodology + governance, not a guaranteed positive delta. Pre-registration and the evidence
gates exist precisely so the result is credible whichever way it lands.

**Q13. Is the work reproducible?**
Yes. The baseline is frozen at tag `official-vego-ai-baseline` (`2eeccb1`); the pipeline is deterministic
and offline; 94 tests pass; an evidence-consistency guard verifies 18 invariants (including a claim-language
check) at every change; and non-destruction is enforced by const-valued schema fields, not convention.

---

### One-line framing to keep returning to
*"The contribution is an honest, governed instrument for reusing human judgment — and a precise account of
exactly what evidence would settle the effect question. The missing piece is independent expert labels, and
the protocol to obtain them is built and waiting on approval."*
