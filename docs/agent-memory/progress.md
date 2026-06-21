# Progress

Track milestones, current work, and next steps here.

## Milestones

| Date | Milestone | Status | Notes |
| --- | --- | --- | --- |
| 2026-06-11 | Basic shared memory created | Done | Added Codex and Claude root instructions plus memory logs. |
| 2026-06-11 | Memory upgraded for per-prompt progress tracking | Done | Added current-state and progress tracking so future prompts can orient quickly. |
| 2026-06-11 | Scripted prompt memory pull/update added | Done | Added PowerShell scripts to generate compiled memory and append prompt summaries. |
| 2026-06-11 | PhD research workspace architecture added | Done | Added source, research, experiment, data, paper, thesis, and reproducibility scaffold. |
| 2026-06-11 | Git repository initialized | Done | Added `.gitignore` and initialized Git; baseline commit pending. |
| 2026-06-11 | Safe GitHub baseline published | Done | Pushed safe code/docs baseline to private `AliHamed17/Vego-Ai` on `main`. |
| 2026-06-11 | Claude bootstrap prompt added | Done | Added a paste-ready Claude startup prompt that enforces shared memory, architecture, Git, and safety rules. |
| 2026-06-11 | Workspace architecture diagram added | Done | Added a GitHub-rendered Mermaid diagram and linked it from the architecture docs and root README. |
| 2026-06-11 | Human feedback manager files added | Done | Added structured human-feedback schema, example feedback input, manager module, and review item feedback/status fields. |
| 2026-06-12 | Human feedback manager docs/tests added | Done | Added Milestone 2 documentation and tests; full VEGO-AI test suite passes with 30 tests. |
| 2026-06-12 | Research OS and Confluence sync infrastructure added | In progress | Added research audit registers, EXP-000 folder, Confluence sync docs/config/outbox builder, and research health checks. |
| 2026-06-12 | Confluence live target configured locally | In progress | Local config targets page `294914`; live sync blocked until Atlassian Rovo cloud access is granted. |
| 2026-06-12 | M3 Human Judgment Memory published | Done | Verified 45 tests, compileall, health checks, secret/forbidden audits, then pushed commit `5e109e5` to `origin/main`. |
| 2026-06-12 | Reusable human judgment research story hardened | Done | Updated research plan, methodology, evaluation plan, literature taxonomy, thesis outline, claim/evidence table, roadmap, risks, and EXP-001 shell. |
| 2026-06-12 | M4A Memory Advisory Layer reviewed and merged | Done | Reviewed PR #2, added edge-case fixes, posted review report, and squash-merged as `ecd0972`. |
| 2026-06-13 | M4A reproducibility tags and Claude handoff prepared | Done | Tagged M3, M4A, and research-state commits; added post-merge confirmation and Claude M4B handoff prompt. |
| 2026-06-13 | Dashboard/KPI tracking layer added | Done | Added tracked progress, KPI, and results dashboards and generated a fifth Confluence outbox page for progress tracking. |
| 2026-06-13 | Dashboard health gate added | Done | Added `scripts/dashboard-health.ps1` and wired it into research/project health plus agent end-of-prompt workflow. |
| 2026-06-13 | Dashboard runtime snapshot added | Done | Added `scripts/build-dashboard-snapshot.ps1`; Confluence wiki builds now embed a fresh ignored snapshot with repo, KPI, active-work, outbox, and live-sync status. |
| 2026-06-13 | Manual Confluence sync pack added | Done | Added a generated, ignored manual sync pack with page bodies, target metadata, and hashes for approved fallback publishing. |
| 2026-06-14 | M4B-1 conditional implementation contract recorded | Done | Added deterministic M4B-1 rules, leakage guard, schema expectations, Codex isolation, and Claude branch/PR handoff. |
| 2026-06-14 | Offline VEGO-AI results dashboard merged | Done | Added static dashboard generator, snapshot schema, docs, tests, and ignored generated reports; merged as `cf78d2d`. |
| 2026-06-14 | M4B-1 deterministic comparison merged | Done | PR #4 merged as `944c922`; tag `research-state-m4b1-deterministic-comparison` exists. |
| 2026-06-14 | M4B schema hardening PR opened | In review | PR #6 adds nested required fields and schema regression coverage only. |
| 2026-06-14 | Local no-key execution/results package generated | Done | Created local configs, generated M1-M4A/M4B outputs under `VEGO-AI/runs/20260614-122150/`, rebuilt dashboard, and wrote ignored `RUN_SUMMARY.md`. |
| 2026-06-14 | Visualizer model/result mismatch fix opened | In review | PR #7 adds exact case matching, stale-model clearing, mismatch banner, helper tests, filters, and read-only research panels. |
| 2026-06-14 | Full system validation report generated | Done | Tracked report `VEGO-AI/reports/system_validation_report.md` says PASS after governance cleanup; all functional and health checks pass. |
| 2026-06-14 | QA governance warnings fixed | Done | Added narrow research-health allowlist, restored local baseline tracking branch, and prepared `system_validation_report.md` as a tracked validation artifact. |
| 2026-06-14 | Visualizer UX refresh merged and tagged | Done | PR #7 passed real-display GUI validation, merged as `78b261e`, and tag `research-state-visualizer-ux-clean` points to the merge commit. |
| 2026-06-14 | Shared Claude/Codex state report added | Done | Added `docs/agent-memory/shared-state-report.md` and wired it into compiled memory/startup instructions. |
| 2026-06-14 | Evaluation phase scaffold added | Done | Added `docs/research/evaluation-report.md`; M4B-1 is treated as implemented/evaluation-pending, with release bundle available for review. |
| 2026-06-14 | EXP-001 initial mechanism/readiness evaluation run | Done | Generated ignored `reports/generated/exp001/` tables: 27 comparisons, 0 M4B-1 classification changes, 2 review-after-memory flags, and 0 generalization-safe expert labels. |
| 2026-06-14 | EXP-002 expert labeling package generated | Done | Generated ignored `reports/generated/exp002/` package: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels, and 27 recommended labeling targets. |
| 2026-06-16 | Supervisor Zoom demo package generated | Done | Created ignored `artifacts/supervisor_demo_2026-06-17/` with 20-slide deck, brief, demo script, questions, screenshot checklist, figures, and tables for the 2026-06-17 supervisor session. |
| 2026-06-16 | EXP-003 accuracy-improvement evaluation tooling added | Done | Added full/blind labeling prep, expert-label protocol, strict accuracy gates, error-analysis/accuracy summary tooling, and ignored EXP-003 outputs. Initial EXP-003 has 0 safe expert labels, so accuracy improvement cannot be evaluated yet. |
| 2026-06-16 | Results and accuracy full report generated | Done | Created ignored `artifacts/RESULTS_AND_ACCURACY_FULL_REPORT.md` and linked it from `docs/research/evaluation-report.md`; strict verdict remains no proven accuracy improvement, with 0 generalization-safe expert-labeled rows and 0/27 memory-informed classification changes. |
| 2026-06-16 | Synthetic accuracy simulation generated | Done | Created ignored `artifacts/SYNTHETIC_ACCURACY_SIMULATION_REPORT.md` and `reports/generated/synthetic_accuracy_simulation/`; current M4B-1 has 0 synthetic accuracy delta, while counterfactual flips show synthetic-only possible deltas that are not real evidence and must not be reported as accuracy improvement. |
| 2026-06-16 | EXP-004 policy-sensitivity harness added | Done | Added reusable synthetic/candidate-policy simulation tooling and docs. Initial run shows current M4B-1 remains `+0.00 pp`; aggressive candidate policies can help or harm under different synthetic truth scenarios, so real labels remain required. |
| 2026-06-17 | EXP-005 real-label accuracy gate added | Done | Added supervisor/expert label-review tooling, validation, real-label policy gate outputs, and docs. Initial run has 27 rows, 24 safe candidates, 4 safe memory disagreements, 2 review-after-memory cases, 0 valid labels, and gate status `Accuracy improvement cannot be evaluated yet.` |
| 2026-06-21 | VEGO workbench launcher added | Done | Added one-command local launcher for dashboard, EXP-005 labels, optional GUI, optional wiki outbox, and optional health checks. |
| 2026-06-21 | VEGO topology report exported | Done | Added reusable HTML/PDF topology exporter and generated ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.html` and `.pdf`. |
| 2026-06-21 | Baseline architecture overlay exported | Done | Added reusable overlay exporter and generated ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.html` and `.pdf` showing M1-M4B-1/EXP-005 on top of the paper architecture. |

## Active Work

| ID | Started | Status | Summary | Next Step |
| --- | --- | --- | --- | --- |
| TASK-001 | 2026-06-11 | Done | Durable revert support started by adding `.gitignore`, initializing Git, and pushing a safe baseline. | Continue using commits for every meaningful change. |
| TASK-003 | 2026-06-11 | Open | Audit data sensitivity and provenance. | Review `VEGO-AI/inputs/`, `VEGO-AI/models/`, `VEGO-AI/analysis/`, and the IRB-related PDF. |
| TASK-004 | 2026-06-11 | In progress | Map existing paper/package results to experiments. | Continue `EXP-000-existing-packaged-results-audit` without copying controlled artifacts into Git. |
| TASK-005 | 2026-06-12 | Blocked | Keep curated Confluence wiki current. | Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, then create/update child pages and store page IDs in local config. |
| TASK-006 | 2026-06-12 | Done | Design and merge M4B-1 memory-informed parallel comparison. | Keep M4B-1 experimental and run EXP-001/C4B before making improvement claims. |
| TASK-007 | 2026-06-13 | Done | Release M1-M4A + dashboard + M4B-1 artifact bundle for external technical review. | Use GitHub release assets for review; do not treat the bundle as empirical proof. |
| TASK-008 | 2026-06-13 | Open | Keep progress, KPI, and results dashboards current. | Update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes. |
| TASK-009 | 2026-06-13 | Open | Keep dashboard/wiki tracking health verified. | Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after every Confluence outbox build. |
| TASK-010 | 2026-06-13 | Open | Keep runtime dashboard snapshot fresh. | Run `.\scripts\build-confluence-wiki.ps1` after memory/dashboard updates; it regenerates `docs/dashboards/status-snapshot.generated.md`. |
| TASK-011 | 2026-06-13 | Open | Keep manual Confluence sync pack fresh while live access is blocked. | Run `.\scripts\build-confluence-wiki.ps1`; it regenerates `docs/confluence/manual-sync-pack.generated.md`. |
| TASK-012 | 2026-06-14 | Done | Add local/offline visual metrics dashboard for VEGO-AI result artifacts. | Keep generated `VEGO-AI/reports/results_dashboard/` ignored. |
| TASK-013 | 2026-06-14 | In review | Harden M4B nested schema requirements. | Review and merge PR #6. |
| TASK-014 | 2026-06-14 | Done | Fix research-health allowlist for the tracked dashboard generator. | Narrow allowlist added; `project-health`, `research-health`, and `dashboard-health` pass. |
| TASK-015 | 2026-06-14 | Done | Fix VEGO-AI visualizer model/result mismatch UX. | Preserve the no-silent-mismatch and read-only research-panel boundaries in future visualizer work. |
| TASK-016 | 2026-06-14 | Open | Complete EXP-001 expert-label evaluation. | Add held-out/cross-setting expert labels, rerun `.\scripts\build-exp001-evaluation.ps1`, and update the evaluation report with generalization-safe metrics. |
| TASK-017 | 2026-06-14 | Open | Fill EXP-002 expert labeling package. | Human/supervisor should label at least 20 rows, preferably all 27 current rows, then rerun evaluation with leakage-aware partitions. |
| TASK-018 | 2026-06-16 | Done | Prepare supervisor Zoom package for 2026-06-17. | Use the ignored package locally during the meeting, capture supervisor decisions, and convert accepted labels/decisions into tracked research docs afterward. |
| TASK-019 | 2026-06-16 | Open | Collect EXP-003 independent expert labels. | Fill the blind/full EXP-003 sheets with at least 20 generalization-safe labels before any accuracy-improvement claim or M4B-1 policy refinement. |
| TASK-020 | 2026-06-16 | Open | Use EXP-004 to screen policy candidates after real labels exist. | Rerun `.\scripts\build-policy-sensitivity-simulation.ps1` after EXP-003 has real labels; treat current synthetic results as pipeline/risk screening only. |
| TASK-021 | 2026-06-17 | Open | Collect EXP-005 supervisor/expert labels through the real-label gate. | Fill `reports/generated/exp005_label_review/exp005_label_review_blind.csv`, then run `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream`. |
| TASK-022 | 2026-06-21 | Open | Use the VEGO workbench launcher for daily local review. | Run `.\scripts\open-vego-workbench.ps1` from the repo root, or `.\scripts\open-vego-workbench.ps1 -Gui` when the visualizer is needed. |

## Completed Work

| Date | Summary | Files |
| --- | --- | --- |
| 2026-06-11 | Created shared memory foundation for Codex and Claude. | `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/*` |
| 2026-06-11 | Added clearer current-state and progress tracking requirements. | `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/README.md`, `docs/agent-memory/current-state.md`, `docs/agent-memory/progress.md` |
| 2026-06-11 | Added scripted memory automation for prompt start/end. | `scripts/agent-memory-start.ps1`, `scripts/agent-memory-finish.ps1`, `docs/agent-memory/automation.md` |
| 2026-06-11 | Extracted original VEGO-AI package and added PhD research architecture scaffold. | `VEGO-AI/`, `README.md`, `PROJECT_CHARTER.md`, `docs/architecture/`, `docs/research/`, `experiments/`, `data/`, `papers/`, `thesis/`, `scripts/` |
| 2026-06-11 | Published safe baseline to private GitHub repo. | `main` branch on `AliHamed17/Vego-Ai` |
| 2026-06-11 | Added reusable Claude bootstrap prompt and linked it from Claude instructions. | `CLAUDE.md`, `docs/agent-memory/claude-bootstrap-prompt.md`, `docs/agent-memory/README.md` |
| 2026-06-11 | Added and linked the workspace architecture diagram. | `README.md`, `docs/architecture/README.md`, `docs/architecture/project-map.md`, `docs/architecture/workspace-diagram.md` |
| 2026-06-11 | Added human-feedback manager files and schema fields. | `VEGO-AI/framework/human_feedback_manager.py`, `VEGO-AI/inputs/human_feedback.example.jsonl`, `VEGO-AI/schemas/human_feedback.schema.json`, `VEGO-AI/schemas/human_review_item.schema.json` |
| 2026-06-12 | Added human-feedback manager docs/tests and ignored local Claude settings. | `.gitignore`, `VEGO-AI/README.md`, `VEGO-AI/docs/human_feedback_manager.md`, `VEGO-AI/docs/human_review_queue.md`, `VEGO-AI/tests/test_human_feedback_manager.py` |
| 2026-06-12 | Added Research OS and Confluence sync infrastructure. | `docs/research/`, `docs/confluence/`, `experiments/EXP-000-existing-packaged-results-audit/`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1` |
| 2026-06-12 | Configured ignored local Confluence target. | `docs/confluence/wiki-sync-config.local.json` (ignored), `docs/confluence/wiki-sync.md`, agent instruction files |
| 2026-06-12 | Published M3 Human Judgment Memory to GitHub. | Commit `5e109e5` on `origin/main` |
| 2026-06-12 | Hardened the MSc/PhD research story around reusable human judgment. | `PROJECT_CHARTER.md`, `docs/research/*`, `thesis/outline.md`, `papers/mas4models2026/claim-evidence-table.md`, `docs/project-management/*`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md` |
| 2026-06-12 | Reviewed and merged M4A advisory layer. | PR #2, commit `ecd0972`, `VEGO-AI/framework/memory_advisor.py`, `VEGO-AI/schemas/memory_advice.schema.json`, `VEGO-AI/tests/test_memory_advisor.py`, `VEGO-AI/docs/memory_advisor.md` |
| 2026-06-13 | Tagged reproducible M3/M4A states and added Claude handoff. | `docs/research/m4a-post-merge-confirmation.md`, `docs/agent-memory/claude-m4b-handoff-prompt.md`, tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4a` |
| 2026-06-13 | Added progress/KPI/results dashboard tracking. | `docs/dashboards/`, `scripts/build-confluence-wiki.ps1`, `scripts/research-health.ps1`, agent instructions, Confluence sync docs |
| 2026-06-13 | Added dashboard health enforcement. | `scripts/dashboard-health.ps1`, `scripts/research-health.ps1`, agent instructions, dashboard docs |
| 2026-06-13 | Added generated dashboard runtime snapshot. | `scripts/build-dashboard-snapshot.ps1`, `scripts/build-confluence-wiki.ps1`, `.gitignore`, dashboard/confluence workflow docs |
| 2026-06-13 | Added generated manual Confluence sync pack. | `scripts/build-confluence-manual-sync-pack.ps1`, `docs/confluence/manual-sync.md`, `scripts/build-confluence-wiki.ps1`, `scripts/dashboard-health.ps1`, `scripts/research-health.ps1` |
| 2026-06-14 | Recorded M4B-1 conditional approval contract and Claude handoff. | `docs/research/m4b-conditional-approval.md`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md`, `docs/agent-memory/claude-m4b-handoff-prompt.md`, research/planning/dashboard docs |
| 2026-06-14 | Added offline VEGO-AI results dashboard branch and PR. | PR #5, `.gitignore`, `VEGO-AI/analysis/build_results_dashboard.py`, `VEGO-AI/docs/results_dashboard.md`, `VEGO-AI/schemas/results_dashboard_snapshot.schema.json`, `VEGO-AI/tests/test_results_dashboard.py` |
| 2026-06-14 | Ran no-key local execution package and generated results summary. | Ignored `VEGO-AI/runs/20260614-122150/`, ignored `VEGO-AI/reports/results_dashboard/`, local configs, PR #6 |
| 2026-06-14 | Opened visualizer mismatch UX PR. | PR #7, `VEGO-AI/vego_visualizer_delivery/visualizer_utils.py`, `VEGO-AI/vego_visualizer_delivery/visualize_compliance.py`, `VEGO-AI/tests/test_visualizer_helpers.py`, `VEGO-AI/vego_visualizer_delivery/README.md` |
| 2026-06-14 | Ran full QA/system validation. | `VEGO-AI/reports/system_validation_report.md` (untracked), ignored `VEGO-AI/runs/system_validation_20260614-142018/`, ignored `VEGO-AI/reports/results_dashboard/` |
| 2026-06-14 | Fixed QA governance warnings after validation. | `scripts/research-health.ps1`, `VEGO-AI/reports/system_validation_report.md`, local `baseline/official-vego-ai` tracking branch, memory files |
| 2026-06-14 | Merged and tagged visualizer mismatch UX fix. | PR #7, commit `78b261e`, tag `research-state-visualizer-ux-clean`, real-display screenshots in `%TEMP%\vego_gui_validation_20260614_144509` |
| 2026-06-14 | Added shared state report for Claude and Codex. | `docs/agent-memory/shared-state-report.md`, `scripts/agent-memory-start.ps1`, `AGENTS.md`, `CLAUDE.md`, `docs/agent-memory/README.md`, `docs/agent-memory/claude-bootstrap-prompt.md` |
| 2026-06-14 | Added evaluation report scaffold and updated research dashboard state. | `docs/research/evaluation-report.md`, `docs/research/evaluation-plan.md`, `experiments/registry.md`, `docs/dashboards/`, `docs/agent-memory/` |
| 2026-06-14 | Ran initial EXP-001 mechanism/readiness evaluation. | `scripts/build-exp001-evaluation.ps1`, `docs/research/evaluation-report.md`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md`, ignored `reports/generated/exp001/` |
| 2026-06-14 | Generated EXP-002 expert labeling package. | `scripts/build-exp002-labeling-package.ps1`, `experiments/EXP-002-expert-label-expansion-holdout-evaluation/README.md`, `docs/research/evaluation-report.md`, ignored `reports/generated/exp002/` |
| 2026-06-16 | Generated supervisor Zoom demo package. | Ignored `artifacts/supervisor_demo_2026-06-17/`, ignored `outputs/manual-20260616-supervisor/`, refreshed `reports/generated/exp001/`, `reports/generated/exp002/`, and `VEGO-AI/reports/results_dashboard/` |
| 2026-06-16 | Added EXP-003 accuracy-improvement evaluation path. | `docs/research/accuracy-improvement-plan.md`, `docs/research/expert-labeling-protocol.md`, `experiments/EXP-003-accuracy-improvement-evaluation/README.md`, `scripts/build-exp003-error-analysis.ps1`, EXP-003 evaluator/test, ignored `reports/generated/exp003/` |
| 2026-06-16 | Generated full results and accuracy report. | `docs/research/evaluation-report.md`, ignored `artifacts/RESULTS_AND_ACCURACY_FULL_REPORT.md` |
| 2026-06-16 | Ran synthetic accuracy simulation. | `docs/research/evaluation-report.md`, ignored `artifacts/SYNTHETIC_ACCURACY_SIMULATION_REPORT.md`, ignored `reports/generated/synthetic_accuracy_simulation/` |
| 2026-06-16 | Added EXP-004 policy-sensitivity simulation harness. | `scripts/policy_sensitivity_simulation.py`, `scripts/build-policy-sensitivity-simulation.ps1`, `experiments/EXP-004-policy-sensitivity-simulation/README.md`, `experiments/registry.md`, research docs, ignored `reports/generated/policy_sensitivity/`, ignored `artifacts/POLICY_SENSITIVITY_EXPERIMENT_REPORT.md` |
| 2026-06-17 | Added EXP-005 real-label accuracy gate package. | `scripts/exp005_label_review.py`, `scripts/build-exp005-label-review.ps1`, `experiments/EXP-005-real-label-accuracy-gate/README.md`, `experiments/registry.md`, research docs, ignored `reports/generated/exp005_label_review/`, ignored `artifacts/EXP005_LABEL_REVIEW_PACKAGE.md` |
| 2026-06-21 | Added one-command VEGO workbench launcher. | `scripts/open-vego-workbench.ps1`, `docs/operations/vego-workbench.md`, `README.md`, memory files |
| 2026-06-21 | Exported VEGO topology/flow report to HTML and PDF. | `scripts/export-topology-report.ps1`, `docs/operations/vego-workbench.md`, ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.html`, ignored `artifacts/topology-export/VEGO_TOPOLOGY_FLOW_REPORT.pdf` |
| 2026-06-21 | Exported baseline architecture overlay to HTML and PDF. | `scripts/export-baseline-overlay-report.ps1`, `docs/operations/vego-workbench.md`, ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.html`, ignored `artifacts/topology-export/VEGO_BASELINE_OVERLAY_REPORT.pdf` |

## Next Steps

1. Run `.\scripts\open-vego-workbench.ps1` for daily local review, or `.\scripts\open-vego-workbench.ps1 -Gui` when the visualizer is needed.
2. Fill `reports/generated/exp005_label_review/exp005_label_review_blind.csv` with at least 20 generalization-safe expert labels, preferably 30-50.
3. Rerun `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream` and review `reports/generated/exp005_label_review/label_validation_summary.json`.
4. Review the EXP-005 real-label policy gate plus rerun EXP-003/EXP-004 generated outputs before any M4B-1.1 design change.
4. Keep M4B-2, Agent 4 calls, LLM/API calls, embeddings, baseline output overwrites, and non-read-only visualizer behavior changes blocked.
5. If EXP-003 shows enough safe labels and baseline errors that memory can plausibly address, write or update `docs/research/m4b1-policy-refinement-plan.md`; do not implement policy refinement before approval.
6. Capture supervisor decisions on thesis framing, label protocol, target label count, leakage policy, and M4B-2 gating.
7. Review and merge PR #6 for M4B schema hardening when ready.
8. Keep `docs/dashboards/` current after meaningful progress, KPI, result, or Confluence status changes.
9. Run `.\scripts\build-confluence-wiki.ps1` to refresh the runtime dashboard snapshot, wiki outbox, and manual sync pack.
10. Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after building the Confluence outbox.
11. Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`.
12. Create/update the four Confluence child pages from the outbox/manual sync pack and store their IDs in ignored local config.
13. Audit data/IRB sensitivity before publishing or sharing deferred artifacts.
14. Convert existing package results into evidence entries under `EXP-000`.
15. Continue running the prompt start/end memory and wiki sync scripts for every meaningful prompt.
