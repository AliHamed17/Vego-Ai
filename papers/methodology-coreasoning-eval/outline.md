# Paper A — Outline

## 1. Introduction
- Problem: AI-assisted model assessment must *interpret* deviations (valid alternative vs error); systems
  produce review signals but rarely reuse the human judgment that resolves them.
- The evaluation gap this paper addresses: how do you measure whether reusable human judgment helps, **when
  no independent benchmark exists** and naive labels are circular?
- Contribution: a bias- and leakage-controlled evaluation methodology + evidence-gate discipline.

## 2. Background (real citations only)
- Design science: Hevner et al. (2004); Peffers et al. (2007); Gregor & Hevner (2013).
- Human–AI collaboration: Mosqueira-Rey et al. (2023, HITL); NIST AI RMF (2023, on-the-loop); Amershi et al.
  (2019, guidelines); co-reasoning precedent Silva et al. (2025); Tselonis et al. (2005).
- AI-assisted assessment limits: Bian et al. (2020); Ibáñez et al. (2025); Chen et al. (2024).
- Explainability/reuse: Silva Mercado (2024). Host system: Ahmed et al. (2026, VEGO-AI).

## 3. The evaluation problem (the core motivation)
- 3.1 No independent benchmark: author-reviewed labels byte-identical to Agent 4 (0 field differences) →
  using them is circular.
- 3.2 Same-pattern leakage: memory derived from a pattern cannot evaluate that pattern.
- 3.3 Conservative-policy invariance: a non-destructive deterministic policy may change 0 rows by design, so
  no delta is observable without a justified refinement.
- 3.4 Small sample: counts in the tens, not thousands.

## 4. Methodology (the contribution)
- 4.1 Conditions C0–C4B (layered contribution chain).
- 4.2 Two-tier metrics: primary (effect; gated) vs secondary (mechanism validity; measurable now).
- 4.3 Blind annotation protocol: anonymization, per-reviewer randomization, two independent reviewers,
  Cohen's κ, adjudication (Appendix A.3).
- 4.4 Leakage discipline: per-row `evaluation_leakage_status`; generalization-safe filtering.
- 4.5 Sealed development/holdout (16/8): never tune and evaluate on the same rows.
- 4.6 Evidence gates: 0 → not evaluable; 1–19 → pilot; ≥20 → quantitative; +reviewer-2/adjudication →
  reliability strengthened.
- 4.7 Machine-checked discipline: const-enforced non-destruction; 18-invariant consistency guard.

## 5. Instantiation on VEGO-AI (descriptive, not an effect claim)
- Operating profile (179 cases, 27 patterns, 4 settings; leakage/advice/policy distributions) — see
  `docs/research/baseline-characterization.md`. Reported as feasibility/operability, not accuracy.

## 6. Discussion — transferability
- The methodology generalizes to any human–AI co-reasoning artifact where benchmarks are unavailable or
  contaminated; the gate + leakage + sealed-holdout pattern is domain-independent.

## 7. Threats to validity (Ch 8): construct, internal, external, reliability + mitigations.

## 8. Conclusion: an honest-by-construction evaluation template; empirical instantiation deferred to Paper B.
