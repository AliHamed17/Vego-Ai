# VEGO-AI — Results Deep-Dive & PhD Roadmap

> Companion to `docs/research/phd-thesis-optimization-plan.md`. Honors the project evidence boundary:
> **no accuracy-improvement claim is made anywhere in this document.** Every number is drawn from
> Chapters 6–10, Appendix A, `experiments/registry.md`, and the research-plan docs. This is analysis and
> recommendation, not a change to the baseline, the policy, or the claim boundary.

Author of analysis: Claude · Date: 2026-06-30

---

## Part 1 — Reading the results (what we actually have)

### 1.1 The mechanism is proven; the effect is not yet measurable

The MSc delivered a **complete, inspectable, non-destructive co-reasoning chain** and the machinery to
evaluate it — but **zero** of the evidence currently licenses any claim about accuracy.

| What is established (now) | What is *not* established (yet) |
| --- | --- |
| The full chain runs: AI uncertainty → review → structured feedback → provenance memory → advisory retrieval → parallel comparison | That reusable judgment **improves classification accuracy** |
| Non-destruction is **machine-verified** (`ai_classification_changed = 0`, `ai_behavior_changed_in_baseline = false`) | That memory **generalizes** to genuinely new (held-out) cases |
| Reproducible: 94 tests, 18/18 evidence invariants, frozen baseline tag `official-vego-ai-baseline` (`2eeccb1`) | That Agent 4's behavior should change |
| Scale exercised: 179 models · 27 patterns · 11 queued · 4 feedback · 3 memories · 8 advice · 27 comparison rows | Anything from synthetic EXP-004 (Δ = 0.00 pp is policy-screening only) |

This is a deliberately maximized ratio of **(rigor + readiness) ÷ (unfounded claims)**. It reads as a thin
result only if you expected an accuracy number; it is a strong result if you read it as *a loaded
instrument plus a precisely bounded gap.*

### 1.2 The subtle, important finding: "0 of 27 changed" is partly a policy property, not only a data fact

The conservative policy `memory-informed-classifier-v1` proposes a different class **only on strong,
conflict-free, leakage-safe disagreement** — a condition that **did not occur** in the current run
(0/27 strong-disagreement rows). So "0 differences" is **half data, half design**: original and
memory-informed predictions are identical *by construction*, which means **no labeling can produce an
accuracy delta under v1.** A delta is structurally possible only if a refined policy (M4B-1.1) is later
justified by error analysis and evaluated once on a sealed holdout (see `m4b1-policy-refinement-plan.md`).

**Implication:** the near-term empirical story is not relabeling accuracy — it is **escalation quality**
(where the system flags `requires_human_review_after_memory`). That is more tractable and more honest given
the conservative policy.

### 1.3 The binding constraint

- **0 / 24** generalization-safe expert labels supplied. The gate is closed.
- The **3** memory-derived labels are all `same_pattern_memory_used` → they prove **mechanism only**, never
  generalization. Generalization-safe labeled rows currently = **0**.
- The live, non-trivial signals today are **40.7% targeting** (11/27 queued) and **2/27 escalations**.

### 1.4 The methodological finding is itself a result

The strict review showed the repository's author-reviewed files are **byte-identical** to Agent 4 output for
all 27 patterns — they record *agreement*, not independent ground truth. Using them would be circular.
This negative finding **reframes the entire evaluation** and motivates the bias- and leakage-controlled
annotation protocol. *Discovering that there is no clean benchmark, and designing a defensible way around
it, is a contribution* — arguably the most transferable one.

### 1.5 Capability maturity (per the optimization plan's L1–L5)

- **L1 Prototype — achieved** (mechanism exists and is inspectable, M1–M4B-1).
- **L2 Evidence-infrastructure ready — achieved as tooling only** (protocol, dashboards, guards, and harness exist; empirical evidence is not implied).
- **L3 Empirically evaluated — blocked** on EXP-005 real labels.
- **L4 Generalized / L5 Framework — the PhD.**

---

## Part 2 — What is the progress *for*?

**In one sentence:** the progress builds the *instrument and the discipline* needed to answer the real
question honestly — *does reusable human judgment improve, clarify, or safely escalate AI variability
decisions?* — and narrows the gap to a **single missing input** (24 independent expert labels).

The MSc stage secures three assets that the PhD will stand on:

1. **A working, non-destructive co-reasoning mechanism** — the architecture is real, reproducible, and safe
   to experiment on (you can never corrupt the baseline you are measuring against).
2. **A bias- and leakage-controlled measurement apparatus** — blind sheets, randomization, two-reviewer κ,
   per-row leakage tags, sealed dev/holdout, and pre-committed evidence gates. *This methodology is the
   transferable scientific contribution* and the seed of the doctorate.
3. **A precisely bounded, falsifiable evidence position** — you know exactly what is missing and exactly
   what each evidence gate unlocks. The honesty is the strength: the gap between "mechanism ready" and
   "empirical proof" is as narrow and well-defined as it can be without the labels themselves.

So the point of the progress is **not** a result yet — it is to convert a vague aspiration
("human-in-the-loop is good") into a **governed, falsifiable research program** where the next single input
yields a credible yes/no, and where the *way* you answer is reusable beyond VEGO-AI.

---

## Part 3 — Next steps (prioritized recommendation)

### 3.1 Critical path (nothing quantitative moves without this)

1. **Supervisor approval** of `supervisor-label-approval-pack.md` — reviewer plan, consent/anonymity, claim
   boundary.
2. **Collect the 24 expert labels** with **two independent reviewers** + Cohen's κ + adjudication. Keep the
   **16 dev / 8 holdout** split sealed (reviewers label all 24, blind to the split).
3. **EXP-003 error analysis on the 16 dev rows** → fill the (currently empty) baseline-error taxonomy.
4. **Only then** decide whether M4B-1.1 is justified; if so, freeze it and evaluate **once** on the 8 holdout.
5. **Complete Chapter 7 quantitative sections** under the gate that matches the label count.

### 3.2 Do these now — they need no labels (high value while the gate is closed)

- **Baseline characterization** chapter/table (Agent 4 error profile framing, 179/27/4 settings).
- **Sharpen the escalation framing** (escalation precision/recall as the primary near-term empirical story).
- **Write the methodology paper** — the "no clean benchmark + bias/leakage-controlled protocol" contribution
  is publishable *without any accuracy number.*
- **Reproducibility package** (clean scripts/configs + data-sharing decision).

### 3.3 Strategic de-risk (start planning now, not after the MSc)

- **24 labels (8 holdout) cannot carry a PhD.** The single most important strategic move is to **scale the
  evaluation**: a second annotated run, more settings, more reviewers. Begin recruiting reviewers and
  selecting additional VEGO-AI runs/domains in parallel with MSc completion.
- **Reframe the contributions** so the thesis does not hinge on one accuracy delta (which may be small,
  neutral, or negative). Lead with methodology + governance + escalation quality + cross-domain transfer.

---

## Part 4 — The big PhD plan

### 4.1 Thesis statement (sharpened)

> **Reusable human judgment for governed human–AI co-reasoning in AI-assisted domain-model assessment:** a
> framework — and an evaluation methodology — for deciding *when* a captured human judgment may be reused to
> decide, *when* it may only advise, and *when* it must escalate to further expert review, validated across
> multiple settings, reviewers, and model versions without ever corrupting the baseline being assessed.

The defensible novelty is the **governed reuse decision** (advise vs. decide vs. escalate) plus the
**evaluation methodology for human–AI co-reasoning where no clean benchmark exists** — not "an LLM grader
that is more accurate."

### 4.2 PhD research questions (aligned with the optimization plan, with priority notes)

| ID | Question | My note |
| --- | --- | --- |
| P-RQ1 | *When* should the system ask for human judgment? | Strong, tractable. Targeting/coverage metrics already partly exist. |
| P-RQ2 | How to represent judgments so they stay reusable, auditable, conflict-aware? | Largely answered at MSc; deepen with reviewer-reliability + adjudication history. |
| P-RQ3 | *When* does reuse improve / clarify / safely escalate decisions? | **Highest-risk, highest-value.** Depends on labels + breadth. Frame around escalation first, accuracy second. |
| P-RQ4 | How to govern advise vs. deterministic-policy vs. blocked-automation? | The signature contribution. Sealed-holdout discipline is the proof method. |
| P-RQ5 | How well does it transfer across domains, diagrams, reviewers, datasets? | The generalization spine. **Under-resourced today (1 pipeline, 2 domains, 0 second run).** |

### 4.3 Phase roadmap (extends the plan's P0–P5; durations indicative)

| Phase | Goal | Key deliverables | Gate | Indicative |
| --- | --- | --- | --- | --- |
| **P0** MSc evidence gate | Real labels + Ch 7 quant | 24 labels (κ, adjudication), EXP-003 error taxonomy, Ch 7 complete | ≥20 safe labels | now → ~3 mo |
| **P1** Baseline characterization | Empirical profile of Agent 4 errors & review needs | Error taxonomy, baseline-error chapter, methodology paper | Real labels + taxonomy | Y1 |
| **P2** Reuse validity | Where memory helps / conflicts / only escalates | Leakage-aware paired comparison; escalation precision/recall | Safe-row comparison | Y1–Y2 |
| **P3** Policy refinement | Design M4B-1.1 *only if* errors justify it | Frozen v1.1 behind feature flag; one-shot holdout eval | 16 dev / 8 holdout + supervisor approval | Y2 |
| **P4** Broader validation | More runs, domains, diagrams, reviewers | 2nd+ annotated runs; cross-domain/diagram study; reliability analysis | Publishability + IRB | Y2–Y3 |
| **P5** General framework | Principles + tooling beyond VEGO-AI | Framework paper; reusable design/eval patterns; thesis synthesis | Cross-case evidence | Y3–Y4 |

### 4.4 Contribution arc (how four contributions compound)

1. **Artifact** — the M1–M4B-1 non-destructive co-reasoning layer (MSc: mechanism proven).
2. **Methodology** — bias/leakage-controlled evaluation for human–AI co-reasoning without a clean benchmark
   (MSc: designed; PhD: validated at scale). *Most transferable.*
3. **Governance framework** — evidence-gated rules for advise vs. decide vs. escalate, with sealed-holdout
   adoption criteria (PhD core).
4. **Generalization evidence** — transfer across domains, diagrams, reviewers, and model versions (PhD spine).

The thesis is strong even if the measured accuracy delta is small, because contributions 2–4 do not depend
on a large positive delta — they depend on *doing the measurement honestly and at breadth.*

### 4.5 Publication strategy (candidates; reconcile with `publication-plan.md`)

- **Done/in progress:** MAS4Models @ MODELS 2026 (VEGO-AI baseline, "Not All Differences Matter").
- **Paper A — Methodology (no accuracy claim needed):** evaluating human–AI co-reasoning when the only
  available labels are circular — the bias/leakage-controlled protocol + evidence gates. Venue: ER / CAiSE /
  SoSyM.
- **Paper B — Empirical (post-labels):** selective triggering + escalation quality on real expert labels;
  leakage-aware comparison. Venue: MODELS / EMSE.
- **Paper C — Framework (later):** governed reuse (advise/decide/escalate) as transferable design theory.
  Venue: EMSE / TSE / SoSyM, or a human–AI venue (CHI/CSCW angle for the co-reasoning interaction).

### 4.6 Risk register (top risks first)

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| **Thin evidence / small sample** | 24 labels, 8 holdout cannot sustain strong generalization claims | Plan 2nd annotated run + more settings *now*; frame holdout as pilot; lead with methodology |
| **Conservative policy → no delta** | v1 changes 0/27, so accuracy delta is structurally 0 | Lead with escalation precision/recall; gate M4B-1.1 strictly on dev-row error analysis |
| **Single domain / pipeline** | 1 system, 2 domains limits external validity | P4 cross-domain/diagram/reviewer expansion is non-optional for the PhD |
| **Reviewer reliability** | Subjective substantial/occasional distinction | Two reviewers + κ + adjudication; report reliability *alongside* every accuracy figure |
| **Over-claiming pressure** | Temptation to imply improvement | Keep evidence gates + claim-language guard; never tune and evaluate on the same rows |

### 4.7 Guardrails carried into the PhD (do not relax)

- No accuracy-improvement claim until ≥20 generalization-safe labels exist.
- Baseline `eval_output/` and Agent 4 are never overwritten; every variant writes a separate artifact.
- Sealed holdout: never tune and evaluate on the same rows.
- Synthetic ≠ real (EXP-004 is policy screening only).
- Every reported result maps to data + code + labels + limitations + provenance.

### 4.8 Success criteria (when this is a strong PhD, not a thin one)

- Generalization-safe labels exist **at scale** (well beyond 24), across **>1 run and >1 domain**, with
  reported inter-rater reliability.
- A **governed reuse framework** (advise/decide/escalate) is specified and validated on sealed holdouts.
- The **evaluation methodology** is shown to transfer to at least one setting beyond VEGO-AI.
- Claims and limitations are exactly bounded by evidence — the honesty that characterizes the MSc is
  preserved at PhD scale.

---

## Part 5 — One paragraph for your supervisor

The MSc has delivered a working, non-destructive human–AI co-reasoning layer (M1–M4B-1) and, more
importantly, a bias- and leakage-controlled methodology for evaluating it — together with a precisely
bounded evidence position: mechanism, traceability, and escalation are demonstrated and reproducible, while
classification-accuracy improvement remains *well-posed but not yet answerable* pending 24 independent
expert labels. The immediate ask is approval to collect those labels. The PhD then broadens this from a
single-instance prototype into a **general, evaluated framework for governed reuse of human judgment**
(when to advise, when to decide, when to escalate), validated across domains, diagrams, reviewers, and model
versions — with the evaluation methodology itself as a transferable contribution that does not depend on any
single accuracy number.
