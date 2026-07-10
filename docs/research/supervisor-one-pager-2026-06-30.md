# VEGO-AI — MSc Evidence Gate: Supervisor Approval Request

**Date:** 2026-06-30  ·  **Student:** Ali Ahmed  ·  **Thesis:** *Reusable Human Judgment in AI-Assisted Domain Model Assessment — The VEGO-AI Case*

## The ask (one decision)

Approve the **blind expert-labeling protocol and reviewer panel** so the **24 generalization-safe patterns**
can be independently labeled. This is the single blocker between *mechanism demonstrated* and *quantitative
results*.

## Where the project stands

Artifact complete through **M4B-1** (selective review → structured feedback → provenance-tracked memory →
advisory retrieval → non-destructive parallel comparison). **10/10** thesis chapters drafted; a 38-slide
progress deck; methodology + empirical papers scaffolded. Reproducible: frozen baseline tag
`official-vego-ai-baseline` (`2eeccb1`), **94 tests**, **18/18** evidence invariants passing.

## Evidence boundary (honest by construction)

- **Demonstrated now:** mechanism, traceability, escalation, reproducibility.
- **Not yet evaluable:** classification-accuracy improvement or generalization — because **0 of 24**
  generalization-safe expert labels exist (the 3 memory-derived labels are same-pattern → mechanism only).

## What your approval unlocks

Independent labels enable leakage-safe accuracy / macro-F1, escalation precision/recall, and inter-rater
reliability (Cohen's κ). Pre-committed gates: **0 → not evaluable · 1–19 → pilot only · ≥20 → quantitative**.

## Decisions requested

1. **Protocol & labels** — `Substantial` / `Occasional` / `Undetermined` + rationale + confidence. Acceptable?
2. **Reviewer panel** — two independent reviewers + adjudication (or reviewer-2 + supervisor adjudication)?
3. **Ethics/consent** — existing IRB sufficient; reviewer anonymity handling confirmed?
4. **Minimum evidence** — confirm **≥20** generalization-safe labels before any quantitative claim.
5. **Immediate set** — confirm the current **24** candidates as the labeling target.
6. **Scope** — confirm M4B-1.1 / M4B-2 / Agent-4 / baseline changes remain **out of scope** (label collection only).

## To review (start here)

`reports/generated/exp005_label_review/labeling_instructions.md` · `…/exp005_label_review_blind.csv` ·
`…/exp005_adjudication_sheet.csv`. Full detail: `docs/research/supervisor-label-approval-pack.md`.

> **Out of scope until real-label error analysis justifies it:** any accuracy/generalization claim, any
> baseline or Agent-4 modification, and any deterministic policy refinement. Approval is requested for
> **label collection only.**
