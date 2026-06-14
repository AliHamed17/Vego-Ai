# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

## Last Updated

- 2026-06-14 18:52 +03:00 by Codex.

## Project Goal

- Maintain a shared project memory so every prompt can use prior context, progress, issues, decisions, and rollback notes.
- Support both Codex and Claude with plain Markdown documentation.
- Maintain an MSc-thesis-ready and PhD-continuation VEGO-AI research workspace with source, experiments, data governance, papers, thesis work, and reproducibility documentation.
- Keep reusable human judgment in AI-assisted domain model assessment as the explicit research spine.

## Latest Known State

- Workspace root: `c:\Users\ahamed\vego-ai`
- Git status: repository initialized, safe baseline committed, and pushed to private GitHub repo `AliHamed17/Vego-Ai` on 2026-06-11.
- Current local branch: `main`, tracking `origin/main`.
- Current `main` / `origin/main`: includes PR #7 merge `78b261e` plus the follow-up memory/dashboard sync for that merge; use `git log -1` for the exact moving HEAD.
- Results dashboard is merged on `main` as `cf78d2d`; reproducibility tag `research-state-results-dashboard` exists.
- M4B-1 deterministic comparison is merged on `main` as `944c922`; reproducibility tag `research-state-m4b1-deterministic-comparison` exists.
- The `research-state-m4b1-deterministic-comparison` GitHub release contains `vego-ai-M1-M4A-dashboard-M4B1-changes.zip` and `M1-M4A-dashboard-M4B1-manifest.md` for external technical review.
- The implementation is now treated as complete through M4B-1 for research-evaluation purposes; the next major work is EXP-001/C4B empirical evaluation, not more feature building.
- Follow-up schema hardening PR #6 is open: `https://github.com/AliHamed17/Vego-Ai/pull/6`.
- Safe baseline merge commit: `76e7277`.
- Main visible source files at setup:
  - `Variability_MAS4MODELS2026_Mar28_IRB2איריס (1).pdf`
  - `VEGO-AI-20260611T112722Z-3-001.zip`
- Original source package extracted to `VEGO-AI/`.
- PhD/research architecture scaffold exists at the repository root.
- Safe GitHub baseline intentionally excludes root PDF, zip archives, generated outputs, compiled memory, model files, analysis files, eval outputs, visualizer bundled data, generated review queues, bundled executable, and `get-pip.py`.
- Human-feedback workflow files now include `VEGO-AI/framework/human_feedback_manager.py`, `VEGO-AI/inputs/human_feedback.example.jsonl`, `VEGO-AI/schemas/human_feedback.schema.json`, and feedback attachment/status fields in `VEGO-AI/schemas/human_review_item.schema.json`.
- Human-feedback manager documentation and tests now exist at `VEGO-AI/docs/human_feedback_manager.md` and `VEGO-AI/tests/test_human_feedback_manager.py`.
- Milestone 3 Human Judgment Memory is implemented and published on `origin/main` as commit `5e109e5`.
- M3 remains inert: no Agent 4 wiring, no embeddings, and no visualizer changes.
- Milestone 4A Human Judgment Memory Advisory Layer was reviewed by Codex in PR #2 and squash-merged to `origin/main` as commit `ecd0972`.
- M4A retrieves relevant Human Judgment Memory for Agent 4 patterns and emits advisory-only memory advice; it does not change AI classifications.
- Reproducibility tags now exist on GitHub:
  - `milestone-m3-human-judgment-memory` -> `5e109e5f9f2073d9cdc2325bcea2823d57c77882`
  - `milestone-m4a-memory-advisory` -> `ecd097245c463089a5721d68b17d6b22a1005a43`
  - `research-state-m4a` -> `28289405fc7cb687665f949bf039355a97967c59`
- Post-merge behavior confirmation exists at `docs/research/m4a-post-merge-confirmation.md`.
- M4B-1 is implemented and merged as a deterministic, experimental, parallel-comparison layer; it preserves original Agent 4 output, writes only `memory_informed_comparison.json`, sets `ai_behavior_changed_in_baseline=false`, and labels evaluation leakage.
- M4B-2, Agent 4 `resolve_with_answers`, LLM/API calls, embeddings, visualizer changes, and baseline output overwrites remain not approved.
- Progress, KPI, and results dashboards exist under `docs/dashboards/`; an ignored runtime snapshot is generated at `docs/dashboards/status-snapshot.generated.md`, checked by `scripts/dashboard-health.ps1`, and embedded in the generated Confluence Progress Dashboard page.
- A local/offline VEGO-AI results dashboard generator exists on `main` at `VEGO-AI/analysis/build_results_dashboard.py`.
- The results dashboard reads existing JSON/JSONL outputs only and generates ignored static files under `VEGO-AI/reports/results_dashboard/`.
- Latest generated dashboard snapshot reported 4 settings, 179 cases, 27 variability patterns, 11 human-review queue items, 4 resolved feedback items, 3 reusable memory entries, 8 memory-advice items, and `ai_classification_changed_count=0`.
- Results dashboard docs/tests/schema exist at `VEGO-AI/docs/results_dashboard.md`, `VEGO-AI/tests/test_results_dashboard.py`, and `VEGO-AI/schemas/results_dashboard_snapshot.schema.json`.
- M4B-1 follow-up PR #6 is open and ready for separate review: `https://github.com/AliHamed17/Vego-Ai/pull/6`; it hardens nested schema requirements and tests only and changes no classifier behavior.
- Visualizer UX refresh PR #7 was real-display validated, marked ready, and squash-merged on 2026-06-14 as commit `78b261e`.
- Reproducibility tag `research-state-visualizer-ux-clean` points to `78b261e033fc4f3f66170985a884aa5cd0a0cfd2`.
- PR #7 adds pure visualizer matching helpers, exact `<case_id>_` model/result pairing, stale-model clearing, a persistent Matched/Mismatch/Unknown/No matching model found banner, search/status filters, and read-only research panels for M1/M2/M3/M4A/M4B-1 sidecars.
- PR #7 is UI/read-only: it does not change Agent 2/3/4, evaluator/orchestrator behavior, baseline outputs, feedback/memory/advice/comparison files, OpenAI/API behavior, M4B-2, or controlled artifacts.
- Real-display GUI validation passed on 2026-06-14 for mismatch warning, no-match stale-model clearing, auto-load matching model, filters/details, read-only research panels, and graceful diagram failure handling. Screenshots are stored outside the repo at `%TEMP%\vego_gui_validation_20260614_144509`.
- System validation report generated at `VEGO-AI/reports/system_validation_report.md` on 2026-06-14 and updated after governance cleanup with status `PASS`: 93 pytest tests passed, direct runners passed, schema/CLI/compile/dashboard/visualizer/generated-output smoke checks passed, `project-health`, `research-health`, and `dashboard-health` pass, and the report is tracked as a research validation artifact.
- Post-merge PR #7 validation on `main` passed: `python -m pytest VEGO-AI\tests -q` (93 passed), `python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery`, `.\scripts\project-health.ps1`, `.\scripts\research-health.ps1`, and `.\scripts\dashboard-health.ps1 -RequireOutbox`.
- Latest local execution package uses run ID `20260614-122150`:
  - Local configs: `VEGO-AI/framework/run_config.local.json`, `VEGO-AI/eval/eval_config.local.json`, smoke configs.
  - Generated local human outputs: `VEGO-AI/runs/20260614-122150/human/`.
  - Generated dashboard and run summary: `VEGO-AI/reports/results_dashboard/`.
  - Live LLM runs were skipped because `OPENAI_API_KEY` was not set.
  - Generated M4A advice across four settings kept `ai_classification_changed_count=0`.
  - Generated M4B-1 comparisons across four settings: 27 comparisons, 0 memory-informed differences, 2 human-review-after-memory flags, and 0 baseline behavior changes.
- The main research question now centers on reusable human judgment in human-AI collaboration for AI-assisted domain modeling and model assessment.
- Planning artifacts define the literature-review taxonomy, C0-C4B evaluation plan, thesis outline, claim/evidence table, and EXP-001 M4B-1 deterministic comparison contract.
- `docs/research/evaluation-report.md` now provides the evaluation scaffold for reusable human judgment evidence, leakage policy, dashboard figures, and thesis claims.
- Initial EXP-001 mechanism/readiness evaluation has been generated locally with `.\scripts\build-exp001-evaluation.ps1`; ignored outputs are under `reports/generated/exp001/`.
- Initial EXP-001 result: 27 comparisons, 3 expert-labeled rows from same-pattern Human Judgment Memory, 0 generalization-safe expert-labeled rows, 0 memory-informed classification changes, 2 human-review-after-memory flags, and 0 conflicting memory flags. This supports mechanism/readiness only, not accuracy improvement.
- Core orientation files exist:
  - `README.md`
  - `PROJECT_CHARTER.md`
  - `docs/architecture/project-map.md`
  - `docs/research/research-plan.md`
  - `experiments/registry.md`
- Shared memory files exist in `docs/agent-memory/`.
- A high-level shared Claude/Codex state report exists at `docs/agent-memory/shared-state-report.md` and is included in generated compiled memory.
- Prompt memory automation scripts exist in `scripts/`.
- Generated compiled memory file is created at `docs/agent-memory/compiled-memory.md` by `scripts/agent-memory-start.ps1`.
- Compiled memory now includes memory files plus the core project charter, architecture, research plan, and experiment registry.
- Root agent instruction files exist:
  - `AGENTS.md`
  - `CLAUDE.md`
- A paste-ready Claude startup prompt exists at `docs/agent-memory/claude-bootstrap-prompt.md`.
- A paste-ready Claude M4B handoff prompt exists at `docs/agent-memory/claude-m4b-handoff-prompt.md`.
- A GitHub-rendered Mermaid workspace diagram exists at `docs/architecture/workspace-diagram.md`.
- Research OS registers exist for artifact audit, provenance, and publishability under `docs/research/`.
- Confluence wiki sync infrastructure exists under `docs/confluence/`; local target config points to `https://alih10j.atlassian.net/wiki`, cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, space `~71202099edcf0e26ec40cea521806deb9e9687`, home page `294914`.
- `scripts/build-confluence-wiki.ps1` generates ignored curated wiki pages in `docs/confluence/outbox/`, including the progress dashboard.
- `scripts/build-dashboard-snapshot.ps1` generates the ignored dashboard runtime snapshot used in the Confluence Progress Dashboard.
- `scripts/build-confluence-manual-sync-pack.ps1` generates ignored `docs/confluence/manual-sync-pack.generated.md` for manual or browser-assisted Confluence publishing when live Rovo access is unavailable.
- `scripts/dashboard-health.ps1` verifies dashboard sources, KPI rows, Confluence builder wiring, config page slots, and generated outbox readiness.
- `scripts/research-health.ps1` checks research infrastructure, experiment folders, Confluence config template JSON, dashboard health, generated Confluence pack safety, and forbidden tracked artifacts.

## Working Agreement

- At the start of each meaningful prompt, agents should read the memory files as project resources.
- Agents should run `.\scripts\agent-memory-start.ps1` at prompt start and read `compiled-memory.md`.
- Agents should run `.\scripts\agent-memory-finish.ps1` before final response when meaningful work happened.
- Before final response, agents should update the memory files if the work changed project knowledge, files, progress, issues, decisions, or rollback notes.
- Do not store secrets, credentials, tokens, or sensitive personal data in memory.

## Active Risk

- Real revert support is now available through Git for tracked safe-baseline files.
- Prompt automation depends on Codex/Claude following the project instructions and scripts; no background service or native runtime hook is configured.
- Data sensitivity and IRB constraints need an audit before sharing or publishing data/examples.
- M4B-1 memory-informed parallel comparison is merged and available only as an experimental comparison; do not claim behavior improvement until the controlled C4B experiment is run with leakage status recorded.
- `scripts/research-health.ps1` now has a narrow allowlist for the intentionally tracked dashboard generator `VEGO-AI/analysis/build_results_dashboard.py`; controlled/generated analysis artifacts remain forbidden.
- Codex isolation is active for M4B implementation paths on `main`.
- Local Claude permission state is ignored via `.claude/*.local.json`.
- Confluence sync currently operates as generated outbox/manual sync pack only because Atlassian Rovo reports target cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted; rechecked 2026-06-14 14:50 +03:00. A Chrome UI fallback was also checked on 2026-06-13 13:50 +03:00, but the extension-backed browser channel was unavailable after retry.

## Next Best Step

- Review and merge PR #6 for M4B schema hardening.
- Freeze the M4B-1 implementation baseline for empirical evaluation; treat PR #6 as schema/governance hardening only, not a new feature direction.
- Keep the merged PR #7 visualizer UX boundary intact: no silent model/result mismatch, no stale model selection, and research panels remain read-only.
- Run EXP-001 as the controlled M4B/C4B experiment after selecting audited inputs and documenting the supplied memory advice, memory items, deterministic policy version, and leakage status.
- Collect or define held-out expert labels, then rerun EXP-001 so expert alignment/generalization can be evaluated.
- Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, or enable a working Chrome extension route; then create/update the Confluence child pages using the outbox/manual sync pack, including the Progress Dashboard, and record their IDs locally.
