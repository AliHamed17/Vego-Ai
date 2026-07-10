# Results Dashboard

Last curated update: 2026-07-10. Historical validation rows below retain their original dates; they are not claims about the current dirty worktree unless explicitly rerun.

## Validated Implementation Results

| Result | Value | Evidence | Interpretation |
| --- | --- | --- | --- |
| Full VEGO-AI test suite | Historical: 93 passed | `python -m pytest VEGO-AI\tests -q` on 2026-06-14 after PR #7 merge | Historical snapshot only; rerun before reporting a current count. |
| Framework/eval/analysis/visualizer compile check | Historical pass | `python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery` on 2026-06-14 after PR #7 merge | Historical snapshot only, not a current clean-state claim. |
| Dashboard/wiki tracking health | Passed | `.\scripts\build-confluence-wiki.ps1` and `.\scripts\dashboard-health.ps1 -RequireOutbox` on 2026-06-14 | Runtime snapshot, manual sync pack, KPI dashboard, and generated Confluence outbox wiring are verified. |
| Visualizer real-display GUI validation | Passed | PR #7 checklist on 2026-06-14 with screenshots in `%TEMP%\vego_gui_validation_20260614_144509` | Mismatch warning, no-match stale clearing, auto-match, filters/details, read-only research panels, and graceful diagram failure handling are verified. |
| M4A advisory report validation | Passed | M4A review session log and schema validation | `memory_advice.json` conforms to the M4A schema. |
| M4A classification changes | 0 | M4A generated advice review | Advisory layer did not change AI classifications. |
| M4A advice distribution | none 5, strong 2, moderate 1 | M4A generated `ucd_ch` advice review | Memory advice surfaces relevant prior judgments where available. |
| Post-merge behavior boundary | No framework/schema/test changes in `2828940` | `docs/research/m4a-post-merge-confirmation.md` | Research-story update did not change VEGO-AI behavior. |
| M4B-1 implementation baseline | Implemented / evaluation pending | Tag `research-state-m4b1-deterministic-comparison`, `docs/research/evaluation-report.md`, and EXP-001 | M4B-1 is available as deterministic, parallel-only, leakage-labeled comparison; improvement claims still require expert-label evaluation. |
| M4B-1 release artifact | Published | GitHub release assets `vego-ai-M1-M4A-dashboard-M4B1-changes.zip` and `M1-M4A-dashboard-M4B1-manifest.md` | Artifact bundle supports external technical review, not empirical proof. |
| EXP-001 initial evaluation run | Mechanism/readiness only | `.\scripts\build-exp001-evaluation.ps1`; ignored `reports/generated/exp001/` | 27 comparisons, 0 memory-informed classification changes, 2 human-review-after-memory flags, 0 generalization-safe expert labels; no accuracy-improvement claim allowed. |
| EXP-002 expert labeling package | Ready for human labeling | `.\scripts\build-exp002-labeling-package.ps1`; ignored `reports/generated/exp002/` | 27 labeling rows across 4 settings, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets. |
| EXP-006 H-Listen event replay (historical) | 11 queue items / 481 heterogeneous reconstructed lifecycle events | `.\scripts\run-hlayer-iteration.ps1`; ignored `reports/generated/exp006/` | Count ratio only; no event-level visibility inference or linkage exists. Early-stage share 0.187; E3 answers are not persisted. |
| EXP-007 dosage-mode replay (historical iteration 6) | `threshold_sev2` load=0.799, bundled=0.891, wcov=0.96 | Ignored `reports/generated/exp007/` | Replay pilot candidate, not a default. Bundling produced a modest absolute reduction (for example 54 to 53); design evidence only. |
| EXP-008 early-trigger mining (2026-07-10, iteration 6) | 167 unstable guidelines; 160 never reviewed; rank-and-cap K=30 -> 0.75 capture | Ignored `reports/generated/exp008/` | Rank-and-cap enforces the load budget by construction but reveals a genuine trade-off: 0.8 capture and <=30 load/setting are not simultaneously achievable with a uniform K - a real design decision for Iris, not a tuning gap. Mechanism/observability evidence only. |
| EXP-009/010 synthetic prototypes (2026-07-10, iteration 7) | Provisional run complete; protocol unapproved | Ignored `reports/generated/exp009/` and `exp010/` | Assumption-driven synthetic rule tests only. They do not validate real expert mistakes or approve the four-source/two-round proposal. |
| EXP-012 validated baseline interface | Interface repaired; canonical EXP-003 cross-check PASS; safe N=0 | Ignored `reports/generated/exp012/` | Generalization-safe status remains `NOT YET COMPUTABLE`. Historical same-pattern pilot is excluded; interface readiness is not evaluation evidence. |
| EXP-013–018 conformance fixtures (2026-07-10) | Six CLIs pass; 24 focused tests; offline validator 19/19 PASS | Ignored `reports/generated/exp013/` through `exp018/` | Fixture-level contract, determinism, workload, authority, provenance, and proposal-safety evidence. No empirical-performance or runtime-authorization claim. |
| H-layer reliability iteration 008 (2026-07-10) | Accepted `NEUTRAL`; run `hlayer-20260710T171143Z-2a66e71a3f` | Ignored `reports/generated/hlayer_iterations/iter_008/` | Atomic temp execution/promotion, manifests, deferred decision snapshot, validated EXP-005 N=0 gate, and repaired EXP-012 cross-check. Reliability evidence only; protected runtime unchanged. |
| H-layer metric/contract iteration 009 (2026-07-10) | Accepted `NEUTRAL`; run `hlayer-20260710T175523Z-ab5175fd07` | Ignored `reports/generated/hlayer_iterations/iter_009/` | 481 captured + 20 explicit gaps = 501 ObservationRecords; `threshold_sev2` event/transaction load 0.799/0.796, weighted/high-severity coverage 0.981/1.0; target coverage>=0.8 at load<=0.5 remains unmet; K30/K35 capture 0.75/0.85. Pareto only; no default. |
| Separate H-layer conformance suite | Offline-only run `HLAYER-CONFORMANCE-7a426ce3a5336b158606` | Normalized `7a426ce3a5336b15860687f1a7f69da241e88b60b0e1b23f95a1d69b21ebba27` | Snapshot `681102be14d0aed854dd384fe0f18cc62081d46dfbf64ab6f1a3b47fe92cb0c1`; separate from numbered iterations; no runtime authorization. |

## Reproducibility Anchors

| State | Tag / Commit | Purpose |
| --- | --- | --- |
| M3 code state | `milestone-m3-human-judgment-memory` / `5e109e5` | Human Judgment Memory milestone. |
| M4A code state | `milestone-m4a-memory-advisory` / `ecd0972` | Advisory memory layer milestone. |
| M4A research state | `research-state-m4a` / `2828940` | Research story and documentation state after M4A. |
| M4B-1 comparison state | `research-state-m4b1-deterministic-comparison` / `944c922` | Deterministic parallel comparison milestone. |
| Visualizer UX clean state | `research-state-visualizer-ux-clean` / `78b261e` | Model/result matching and read-only research-panel UX cleanup. |
| Current workspace | `main` / `c72b845` | Dirty local workspace; use `phase-0-boundary-record.md` for protected-path fingerprints. |

## Research Result Claims

| Claim | Current Support | Status |
| --- | --- | --- |
| VEGO-AI can route selected AI decisions to human review. | M1 implementation and tests. | Supported |
| VEGO-AI can capture structured human feedback. | M2 schema, manager, docs, and tests. | Supported |
| VEGO-AI can store reusable human judgment with provenance. | M3 implementation, schema, docs, and tests. | Supported |
| VEGO-AI can retrieve reusable judgment as advisory evidence without changing AI behavior. | M4A implementation, schema, docs, tests, and review metrics. | Supported |
| Reusable memory improves AI variability interpretation. | Not yet tested; requires M4B-1/C4B evidence with leakage labels. | Not claimed |

## Boundaries

- No controlled model, analysis, evaluation-output, PDF, archive, or executable contents are copied into this dashboard.
- Existing M4A result numbers are metadata-level review results.
- Any future performance or improvement claim must be linked to an experiment record and publishability decision.
