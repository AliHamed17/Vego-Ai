# VEGO-AI Research Workspace

This repository is the working MSc thesis and PhD-continuation workspace for VEGO-AI: agentic AI support for variability exploration of domain models, centered on reusable human judgment in AI-assisted model assessment.

The workspace is organized so research context, source code, experiments, data, outputs, papers, thesis material, and agent memory stay separate but connected.

## Start Here

1. Read `PROJECT_CHARTER.md` for the purpose and boundaries.
2. Read `docs/architecture/project-map.md` for the folder map.
3. Read `docs/architecture/workspace-diagram.md` for the GitHub-rendered architecture diagram.
4. Read `docs/research/research-plan.md` for research questions and milestones.
5. Read `docs/dashboards/progress-dashboard.md` and `docs/dashboards/kpi-register.md` for progress and KPI tracking.
6. Read `experiments/registry.md` before creating or running experiments.
7. Read `docs/confluence/wiki-sync.md` for the curated wiki sync workflow.
8. Run `.\scripts\agent-memory-start.ps1` before AI-assisted work.

## Current Source Package

The original delivered project package is preserved in:

```text
VEGO-AI/
```

It contains the framework, evaluator, inputs, models, analysis files, evaluation outputs, and visualizer delivery package extracted from `VEGO-AI-20260611T112722Z-3-001.zip`.

Do not mix thesis notes, experiment notes, or project-management files inside `VEGO-AI/`. Keep those in the research scaffold at the repository root.

## Main Areas

| Area | Purpose |
| --- | --- |
| `VEGO-AI/` | Preserved source package and bundled experiment materials. |
| `docs/` | Architecture, research method, project memory, decisions, and documentation. |
| `docs/dashboards/` | Progress, KPI, and results dashboards for local and Confluence tracking. |
| `docs/confluence/` | Curated Confluence wiki sync workflow and generated outbox. |
| `experiments/` | One folder per planned or executed experiment. |
| `data/` | Controlled data zones with documentation. |
| `outputs/` | Generated results, figures, logs, and exports. |
| `reports/` | Generated and curated reports. |
| `literature/` | Papers, reading notes, and bibliography work. |
| `papers/` | Manuscript planning and submission materials. |
| `thesis/` | Thesis outline, chapter drafts, and defense preparation. |
| `src/` | Future cleaned/reusable package code. |
| `tests/` | Future regression, unit, and reproducibility tests. |
| `scripts/` | Automation for memory, experiments, health checks, and setup. |

## Daily Workflow

1. Pull memory context: `.\scripts\agent-memory-start.ps1`.
2. Check active tasks in `docs/agent-memory/progress.md`.
3. Work in the right area: code in `VEGO-AI/` or `src/`, experiments in `experiments/`, notes in `docs/` or `literature/`.
4. Record research changes in the relevant registry or template.
5. Finish with `.\scripts\agent-memory-finish.ps1` so future prompts can continue the thread.
6. Refresh the Confluence outbox, dashboard runtime snapshot, and manual sync pack with `.\scripts\build-confluence-wiki.ps1`.
7. Verify dashboard/wiki readiness with `.\scripts\dashboard-health.ps1 -RequireOutbox`.

## Reproducibility Rule

Every claim should eventually connect to:

- a research question,
- a dataset or input version,
- a runnable command/configuration,
- an output artifact,
- an interpretation note,
- and, when possible, a test or validation check.
