# Escalation-Quality Framing & Thin-Evidence De-Risk Plan

> Step 3 of `results-deepdive-and-phd-roadmap.md`. **No accuracy claim.** Defines the near-term empirical
> story (escalation quality) and the actions that de-risk the small-sample problem. Metric *definitions* and
> the plan are label-independent; computing precision/recall still requires the gated expert labels.

---

## Part A — Escalation quality as the primary near-term story

### A.1 Why escalation, not relabeling
Under the conservative policy `memory-informed-classifier-v1`, **0 of 27** classifications change — by design
(it relabels only on strong, conflict-free, leakage-safe disagreement, which did not occur). So an accuracy
*delta* is structurally unobservable under v1. The system's *live* value today is **where it routes work to
a human**: the **2 of 27** `requires_human_review_after_memory` flags (the `moderate_disagreement_keep_
original_require_review` rows) and the **11 of 27** M1 review-queue selections (40.7% targeting). The honest
near-term claim is about **targeting and escalation**, not relabeling accuracy.

### A.2 Metric specification (definitions ready now; computation gated on labels)
- **M1 targeting rate** = queued / total = 11/27 = 40.7% *(measurable now, descriptive)*.
- **Escalation count** = `requires_human_review_after_memory` = 2/27 *(measurable now, descriptive)*.
- **Escalation precision** = (flagged rows that are *actual baseline errors*) / (all flagged rows). *(needs
  expert labels to define the error set.)*
- **Escalation recall / coverage** = (actual baseline errors that were flagged by M1 or M4B-1) / (all actual
  baseline errors). *(needs labels.)*
- All computed on **generalization-safe rows only**; same-pattern rows excluded.

### A.3 How this reframes the thesis/papers
Present escalation + targeting as the **demonstrated safety contribution** (the system focuses scarce expert
attention and never silently overrides the AI), and accuracy as the **precisely-gated open question**. This
lets Chapter 7 and Paper B report a substantive, honest result the moment labels arrive — even if the
relabeling delta stays at zero under v1.

---

## Part B — De-risk plan for the thin-evidence problem

### B.1 The risk
24 generalization-safe candidates, of which only 8 are sealed holdout, cannot by themselves sustain a strong
generalization claim. A doctorate cannot rest on one accuracy number from 8 rows.

### B.2 Actions (start in parallel with MSc completion)
1. **Reviewers:** with supervisor approval, line up **two independent reviewers + an adjudicator** now;
   record reliability (Cohen's κ) as first-class evidence (`expert-labeling-protocol.md`).
2. **Second annotated run:** plan an additional VEGO-AI run / additional settings to grow the pattern count
   beyond 27 (more domains/diagram types), increasing safe rows well past 24.
3. **Exploit existing cross-setting rows:** the **5** `cross_setting_memory_used` rows are already
   generalization-relevant — prioritize them in labeling to seed cross-setting transfer evidence (P-RQ5).
4. **Transfer designs:** specify leave-one-pattern-out, cross-setting (Cheers↔ParkWise), and cross-diagram
   (UCD↔CD) protocols (Ch 6.5) so breadth evidence is collected by construction, not retrofitted.
5. **Lead with methodology + governance:** ensure the thesis/paper contributions (Paper A methodology,
   governed advise/decide/escalate framework) do not depend on a large positive delta.

### B.3 Sequencing
- **P0 (MSc):** label the current 24 (16 dev / 8 sealed holdout); report targeting + escalation + reliability.
- **P4 (PhD):** second run + cross-domain/diagram/reviewer expansion → generalization evidence at scale.

### B.4 Guardrails (unchanged)
No accuracy claim < 20 safe labels; baseline never modified; sealed holdout evaluated once; synthetic ≠ real;
every figure separates mechanism metrics from (gated) accuracy metrics.
