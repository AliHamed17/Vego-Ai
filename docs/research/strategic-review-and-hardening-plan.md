# VEGO-AI Strategic Review And Hardening Plan

Last updated: 2026-07-03 by Claude (status line only; content unchanged).

Status: SEQUENCING SUPERSEDED on 2026-07-03 by `docs/research/extension-plan-2026-07-supervisor-redirect.md` (2026-07-01 supervisor meeting): the framework track (H-layer redesign/specs) is now active and the EXP-005 real-label gate moves to the PARKED evaluation track. The evidence gates, claim boundaries, and validation commands in this document remain authoritative and unchanged for any evidence claim.

## Executive Verdict

VEGO-AI is technically strong through M1, M2, M3, M4A, M4B-1, the dashboard, visualizer UX, EXP-001 to EXP-005 tooling, the local workbench, and topology exports.

The main blocker is no longer implementation. The blocker is empirical evidence.

Current evidence state:

| Measure | Current value |
| --- | ---: |
| Current published baseline | `main` at `0976c05` |
| M4B-1 comparison rows | 27 |
| Generalization-safe EXP-005 candidates | 24 |
| EXP-005 supplied expert labels | 0 |
| EXP-005 complete valid labels | 0 |
| Generalization-safe valid labels | 0 |
| Memory-informed classifications differing from original Agent 4 | 0 / 27 |
| Review-after-memory cases | 2 |
| Strict accuracy gate | Accuracy improvement cannot be evaluated yet. |

The project can currently claim improved traceability, explainability, reusable human-judgment structure, advisory retrieval, review routing, visual inspection, dashboard reporting, and non-destructive comparison. It must not claim improved classification accuracy yet.

## Flow Check

The implemented research topology is coherent:

```text
Original VEGO-AI
  Agent 1 language advice
  Agent 2 domain advice
  Agent 3 model inspection
  Agent 4 variability classification
        |
        v
M1 human review queue
        |
        v
M2 structured human feedback
        |
        v
M3 reusable Human Judgment Memory
        |
        v
M4A advisory memory retrieval
        |
        v
M4B-1 deterministic parallel comparison
        |
        v
EXP-001..EXP-005 evidence gates, dashboard, visualizer, topology exports
```

The important boundary is preserved: M4B-1 writes a parallel comparison artifact and keeps the original Agent 4 classification unchanged. This makes the current architecture valid for design-science evaluation because it separates the baseline decision pipeline from experimental human-judgment reuse.

## Main Vulnerabilities

| Vulnerability | Why it matters | Current control | Required hardening |
| --- | --- | --- | --- |
| No real expert labels | Accuracy and generalization cannot be measured. | EXP-005 label-review package exists. | Fill at least 20 generalization-safe labels; prefer all 24 current candidates and then 30-50 across more audited runs. |
| Same-pattern leakage | Same-pattern memory can validate mechanism behavior but cannot prove generalization. | `evaluation_leakage_status` is tracked. | Report same-pattern, cross-setting, and no-memory/safe partitions separately. |
| Synthetic evidence overclaim | EXP-004 can show possible policy effects but is not real evidence. | Docs mark EXP-004 synthetic-only. | Every report must state that synthetic gains are policy-risk screening only. |
| M4B-1 has zero classification changes | No accuracy delta is possible until a future approved policy changes the parallel classification. | `0/27` difference is documented. | Treat current value as clarification/escalation evidence, not accuracy evidence. |
| Manual CSV/Excel workflow friction | File locks and unsaved edits can block EXP-005 and waste time. | ISS-011 documents the lock risk. | Stop reopening the CSV automatically; save and close Excel before running downstream scripts. |
| Single-reviewer validity risk | One labeler can introduce bias and weak adjudication. | Label fields include reviewer metadata and rationale. | Add a second reviewer or supervisor adjudication for disputed rows before strong claims. |
| False thesis narrative risk | The project may be presented as accuracy improvement before evidence exists. | Evaluation report and accuracy plan block claims. | Keep thesis claim centered on feasibility, governance, reusable judgment, and non-destructive comparison until EXP-005 passes. |
| Confluence drift | Live wiki sync remains blocked by access, so external docs can lag. | Outbox/manual sync pack exists. | Refresh outbox after memory updates and perform manual sync until live access is granted. |
| Data/IRB exposure risk | Controlled PDFs, model files, analysis outputs, and artifacts may contain sensitive material. | `.gitignore`, provenance, publishability registers. | Complete data/IRB audit before publishing deferred artifacts. |
| Decision-boundary risk | Agent 4 changes, M4B-2, embeddings, or LLM reclassification before labels would weaken the study. | Current docs block these changes. | Keep all decision-boundary changes on hold until real-label evidence justifies a reviewed deterministic policy. |

## Strategic Plan

1. Freeze feature work.

   Keep M4B-2, Agent 4 changes, embeddings, LLM/API reclassification, baseline overwrites, and `VEGO-AI/eval_output` changes blocked.

2. Fix the evidence bottleneck.

   Fill `reports/generated/exp005_label_review/exp005_label_review_blind.csv` with real supervisor/expert labels. Do not invent labels and do not use original Agent 4 classifications while labeling.

3. Run the evidence gate only after saved labels exist.

   ```powershell
   .\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet reports\generated\exp005_label_review\exp005_label_review_blind.csv -RunDownstream
   ```

4. Interpret results strictly.

   | Safe labels | Interpretation |
   | ---: | --- |
   | 0 | Accuracy improvement cannot be evaluated. |
   | 1-19 | Pilot evidence only. |
   | 20+ | Quantitative reporting allowed with validity threats. |

5. Strengthen evaluation validity.

   Add a second reviewer or supervisor adjudication for disputed rows using the generated `exp005_adjudication_sheet.csv`. Report leakage partitions separately and include reviewer confidence/rationale in the analysis.

6. Keep the thesis story aligned with proven evidence.

   Current thesis-safe claim: VEGO-AI demonstrates a reusable human-judgment layer for governed, non-destructive human-AI co-reasoning in domain model assessment.

   Not yet allowed: VEGO-AI improves classification accuracy.

7. Decide on M4B-1.1 only after real evidence.

   Consider a deterministic policy refinement only if EXP-005 real labels show that memory would correct baseline errors without unacceptable false changes.

## Acceptance Criteria For The Next Evidence Step

- EXP-005 blind labels are saved and the CSV is closed.
- `labels_supplied_count > 0`.
- Required fields are complete: `expert_label`, `expert_rationale`, `reviewer_id`, `review_date`, `confidence`.
- No invalid labels exist.
- Safe-label count is reported.
- `evidence_verdict.md` and `reproducibility_manifest.json` are regenerated.
- Single-reviewer results are treated as preliminary unless reviewer-2 labels or adjudication exist.
- Protected VEGO behavior paths remain unchanged:

  ```powershell
  git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval
  ```

## Required Validation Before Any Evidence Claim

```powershell
python -m pytest VEGO-AI\tests -q
python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery scripts
.\scripts\project-health.ps1
.\scripts\research-health.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox
git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval
```

## Next Move

Do not build new features. Use the existing EXP-005 package to collect expert labels, rerun the real-label gate, and then decide whether the evidence is blocked, pilot-only, or quantitatively evaluable.
