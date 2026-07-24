# VEGO-AI Alignment Control

Last updated: 2026-07-04 by Fable (Claude) - redirect pointer added; content otherwise 2026-06-29 by Codex.

This page is the short control point for Codex and Claude alignment. Read it when checking structure, reviewing progress, or deciding the next step.

> **July 2026 redirect (2026-07-01 supervisor meeting):** the FRAMEWORK track is now active - see
> `docs/research/extension-plan-2026-07-supervisor-redirect.md` (read first). EXP-005 label collection
> remains the entry gate of the PARKED evaluation track; the "Next Required Human Action" below applies to
> that track when it unparks. All Allowed/Blocked Claims on this page remain in force unchanged.
>
> **MediVARIA boundaries (added 2026-07-04):** the medical-domain PhD track
> (`docs/research/medivaria/medivaria-study-plan.md`, section 6 is authoritative) adds STRICTER gates:
> education-domain TRL3 metrics may never be presented as MediVARIA/clinical performance; NO clinical or
> patient data of any kind in this repository (public de-identified datasets included); MediVARIA is
> documentation-only until Iris/Arnon endorse the MV-P0 scope; the clinician is always the decision
> authority and is never simulated.

## Current Architecture State

VEGO-AI is implemented as a preserved baseline plus a non-destructive reusable human-judgment research layer:

```text
Original VEGO-AI Agent 1-4 pipeline
  -> M1 Human Review Queue
  -> M2 Human Feedback Manager
  -> M3 Human Judgment Memory
  -> M4A Memory Advisory Layer
  -> M4B-1 Deterministic Memory-Informed Comparison
  -> Dashboard, visualizer, topology exports, EXP-001..EXP-005 evidence gates
```

The original Agent 4 output remains the baseline. M4B-1 writes a parallel comparison artifact and must not overwrite baseline outputs.

## Implemented Milestones

| Area | Status | Current meaning |
| --- | --- | --- |
| M1-M4B-1 | Implemented | Reusable human judgment can be captured, stored, retrieved as advice, and compared non-destructively. |
| Dashboard and visualizer | Implemented | Results can be inspected with mismatch protection and read-only research panels. |
| EXP-001..EXP-005 tooling | Implemented | Evidence gates exist, but real labels are still required. |
| HITL resource pack | Implemented | Supports thesis framing and evaluation design, not accuracy claims. |
| Shared Codex-Claude memory | Implemented | Both agents load current state, review state, resource memory, and progress through the memory scripts. |
| PhD thesis optimization control | Implemented | `docs/research/phd-thesis-optimization-plan.md` aligns MSc evidence, PhD trajectory, baseline enhancement, and Claude/Codex roles. |

## Evidence State

| Measure | Current value |
| --- | ---: |
| M4B-1 comparison rows | 27 |
| Generalization-safe EXP-005 candidates | 24 |
| Real EXP-005 expert labels | 0 |
| Generalization-safe valid expert labels | 0 |
| Memory-informed classifications differing from original Agent 4 | 0 / 27 |
| Current accuracy verdict | Accuracy improvement cannot be evaluated yet. |

## Allowed Claims

- VEGO-AI now has a reusable human-judgment layer.
- Human review can be routed, structured, stored, and retrieved as advisory evidence.
- M4B-1 supports non-destructive memory-informed comparison.
- Current evidence supports feasibility, traceability, explainability, review routing, and mechanism readiness.

## Blocked Claims

- Classification accuracy improved.
- Human Judgment Memory generalizes across held-out settings.
- Synthetic EXP-004/EXP-005 results prove real accuracy gains; synthetic outputs are policy-risk screening only, not real evidence.
- Same-pattern memory labels prove generalization.
- M4B-2, Agent 4 behavior changes, embeddings, or LLM/API reclassification are justified.

## Next Required Human Action

First review `docs/research/supervisor-label-approval-pack.md` with the supervisor to approve the label
protocol, reviewer plan, ethics/consent handling, minimum evidence target, and claim boundary.

After approval, fill `reports/generated/exp005_label_review/exp005_label_review_blind.csv` with real
supervisor/expert labels, save it, close Excel, then rerun:

```powershell
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet reports\generated\exp005_label_review\exp005_label_review_blind.csv -RunDownstream
```

Quantitative reporting is allowed only after at least 20 generalization-safe valid labels exist.

## Doctoral Extension Control

Use `docs/research/phd-thesis-optimization-plan.md` for PhD-facing work. Any proposed extension must identify
which capability it strengthens:

- baseline preservation;
- human judgment capture;
- governed reuse;
- evaluation gates;
- thesis/research operations;
- literature and framing.

Extensions remain blocked if they require behavior-changing policy, Agent 4 changes, LLM/API calls,
embeddings, or baseline overwrites before EXP-005 labels and explicit supervisor approval.

## Standard Validation

```powershell
python scripts/check_evidence_consistency.py
.\scripts\run-project-review.ps1
.\scripts\build-confluence-wiki.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox
.\scripts\research-health.ps1
python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery scripts
git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval
```

Protected VEGO behavior paths must remain unchanged unless a future reviewed plan explicitly approves a behavior-changing experiment.
