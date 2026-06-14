# KPI Register

Last curated update: 2026-06-14 19:20 +03:00.

## Status Legend

| Status | Meaning |
| --- | --- |
| Green | On track or verified. |
| Yellow | In progress or needs follow-up. |
| Red | At risk and needs active work. |
| Blocked | Waiting for external access or decision. |

## KPI Snapshot

| KPI | Current Value | Target | Status | Evidence | Next Action |
| --- | --- | --- | --- | --- | --- |
| Research spine clarity | Reusable human judgment is the explicit MSc/PhD research spine. | Research docs, roadmap, thesis outline, and claim/evidence table stay aligned. | Green | `docs/research/research-plan.md`, `thesis/outline.md` | Keep M4B design tied to reusable human judgment. |
| Implemented co-reasoning milestone | M1, M2, M3, M4A, and M4B-1 are implemented; M4B-1 remains experimental/parallel-only. | EXP-001/C4B evidence before any improvement claim; no M4B-2. | Green | Tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4b1-deterministic-comparison`; `docs/research/m4b-conditional-approval.md` | Review PR #6 schema hardening, then prepare controlled evaluation. |
| Test suite health | 93 tests passing. | All tracked tests pass before publishing. | Green | `python -m pytest VEGO-AI\tests -q` on 2026-06-14 after PR #7 merge | Continue running before commits and milestone reviews. |
| Compile health | Framework, eval, analysis, and visualizer modules compile successfully. | `compileall` passes for tracked Python implementation areas. | Green | `python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery` on 2026-06-14 after PR #7 merge | Keep import/runtime changes tested. |
| Dashboard tracking health | Dashboard sources, runtime snapshot, manual sync pack, Confluence builder wiring, config page slots, and generated outbox are verified. | `dashboard-health` passes after wiki outbox build. | Green | `.\scripts\build-confluence-wiki.ps1` and `.\scripts\dashboard-health.ps1 -RequireOutbox` on 2026-06-14 | Run after every meaningful dashboard/wiki update. |
| AI behavior boundary | M4A is advisory-only and M4B-1 must keep `ai_behavior_changed_in_baseline=false`. | No baseline AI behavior changes before reviewed M4B evidence. | Green | `VEGO-AI/schemas/memory_advice.schema.json`, `docs/research/m4a-post-merge-confirmation.md`, `docs/research/m4b-conditional-approval.md` | Preserve original Agent 4 output in M4B-1 implementation. |
| M4A advisory result | 8 advice items: none 5, strong 2, moderate 1, classification changes 0. | Advisory report can surface relevant memory without changing AI behavior. | Green | M4A review result recorded in `docs/agent-memory/session-log.md` | Include in M1-M4A artifact manifest. |
| Reproducibility anchors | M3, M4A, and research-state tags are pushed to GitHub. | Milestone tags exist and are stable. | Green | `docs/research/m4a-post-merge-confirmation.md` | Reference tags in artifact manifest. |
| Visualizer UX correctness | Model/result pairing is explicit and no stale model is silently treated as valid. | Mismatch/no-match/match states stay visible and research panels stay read-only. | Green | PR #7, real-display GUI validation, tag `research-state-visualizer-ux-clean` | Preserve this boundary in future visualizer work. |
| Review artifact readiness | M1-M4A + dashboard + M4B-1 ZIP and manifest are published in the GitHub release for `research-state-m4b1-deterministic-comparison`. | Artifact bundle is available for external technical review. | Green | GitHub release assets `vego-ai-M1-M4A-dashboard-M4B1-changes.zip` and `M1-M4A-dashboard-M4B1-manifest.md` | Download/review externally if needed; do not treat artifact release as empirical proof. |
| Experiment registry readiness | EXP-000 and EXP-001 are registered; EXP-001 is ready for evaluation using implemented M4B-1. | EXP-001/C4B evidence is gathered before improvement claims. | Yellow | `experiments/registry.md`, `docs/research/evaluation-report.md` | Fill EXP-000 evidence entries and run EXP-001 with expert labels/leakage status. |
| Evaluation report readiness | Initial EXP-001 mechanism/readiness run is recorded; empirical generalization evidence is incomplete. | Thesis evaluation tables and figures include held-out expert-label results. | Yellow | `docs/research/evaluation-report.md`, ignored `reports/generated/exp001/` | Collect expert labels and rerun EXP-001. |
| Expert-label readiness | EXP-002 labeling package generated: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels. | At least 20 labeled patterns, preferably all 27 current rows before more feature work. | Yellow | `scripts/build-exp002-labeling-package.ps1`, `docs/research/evaluation-report.md`, ignored `reports/generated/exp002/` | Human/supervisor should fill labels and rationale, then rerun evaluation. |
| M4B leakage control | Initial EXP-001 run has 19 no-memory rows, 5 cross-setting memory rows, and 3 same-pattern expert-labeled rows; generalization-safe expert-labeled rows = 0. | No improvement claim without leakage status and clean evaluation design. | Yellow | `docs/research/evaluation-report.md`, `reports/generated/exp001/exp001_summary.json` (ignored) | Prefer leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout evaluation. |
| Data/IRB audit | Deferred artifacts remain unaudited. | Controlled artifacts get provenance and publishability decisions before sharing. | Red | `docs/research/artifact-audit.md`, `docs/research/publishability-register.md` | Continue metadata-only audit. |
| Live Confluence sync | Outbox and manual sync pack generated; live write blocked by Atlassian Rovo cloud grant; Chrome fallback unavailable after retry. | Confluence pages update live from outbox. | Blocked | `docs/agent-memory/issues.md` ISS-005, Rovo rechecked 2026-06-14 14:50 +03:00, Chrome checked 2026-06-13 13:50 +03:00 | Grant Atlassian access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` or enable the Codex Chrome Extension route. |

## Tracking Cadence

- Update this register after every milestone merge, experiment run, external review, or Confluence sync change.
- Keep test counts and result metrics tied to the command/date that produced them.
- Do not promote Yellow or Red KPIs to Green without concrete evidence.
