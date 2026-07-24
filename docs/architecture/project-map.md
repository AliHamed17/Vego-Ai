# Project Map

## Layered Structure

| Layer | Folder | Rule |
| --- | --- | --- |
| Agent memory | `docs/agent-memory/` | Tracks prompt history, current state, issues, decisions, and rollback notes. |
| Dashboards | `docs/dashboards/` | Tracks progress, KPIs, results, generated visualizations, and the E2E report for local review and Confluence dashboards. |
| Confluence sync | `docs/confluence/` | Generates curated wiki pages after memory updates; live sync requires local target IDs. |
| Operations workflows | `docs/operations/` | Documents alignment control, workbench, review, next-step, and progress-update architectures. |
| Preserved source package | `VEGO-AI/` | Original runnable package extracted from the delivery zip. Keep behavior stable unless an experiment requires change. |
| Future clean package | `src/` | Put reusable/refactored code here once behavior has tests. |
| Research method | `docs/research/` | Research questions, methodology, validity, ethics, reproducibility, and PhD capability planning. |
| Experiments | `experiments/` | One folder per experiment, registered in `experiments/registry.md`. |
| Data | `data/` | Controlled raw, interim, processed, and external data zones. |
| Outputs | `outputs/` | Generated result files, figures, logs, and exports. |
| Reporting | `reports/` | Human-readable reports and generated summaries. |
| Writing | `papers/`, `thesis/`, `presentations/` | Publication and degree artifacts. |

## Dependency Direction

Research notes may reference code and outputs. Code should not depend on research notes.

See `framework-diagram.md` for the H-layer framework view and `evaluation-diagram.md` for the parked evaluation track (July 2026 supervisor redirect; active plan: `../research/extension-plan-2026-07-supervisor-redirect.md`).
See `workspace-diagram.md` for a GitHub-rendered diagram of the workspace flow.
See `../operations/alignment-control.md` for the current implementation, evidence, and claim-boundary checkpoint.
See `../research/phd-thesis-optimization-plan.md` for the MSc-to-PhD trajectory and doctoral capability stack.
See `progress-update-diagram.md` for the architecture view of the memory, dashboard, E2E report, Confluence, and 4-hour update flow.
See `../operations/progress-update-architecture.md` for the operational update contract.

```text
research questions -> experiment protocol -> code/config -> outputs -> analysis -> paper/thesis claim -> curated wiki summary
```

## Doctoral Capability Direction

PhD extension work should strengthen one of these explicit capabilities:

- baseline preservation and reproducible comparison;
- human judgment capture and adjudication;
- governed reuse of expert knowledge;
- evaluation gates and sealed holdout discipline;
- thesis/research operations and claim traceability;
- literature/theory framing for human-AI co-reasoning.

If a proposed extension does not fit one of these capabilities, define the research rationale before editing
code or thesis structure.

## Source Package Boundary

`VEGO-AI/` is the current runnable artifact. Treat it as a preserved source package until a refactor plan exists.

See `source-package-manifest.md` for archive provenance and package contents.

Allowed inside `VEGO-AI/`:

- code fixes,
- config changes needed for runs,
- evaluator and visualizer improvements,
- tests added close to existing code when useful.

Keep outside `VEGO-AI/`:

- thesis drafts,
- paper drafts,
- meeting notes,
- broad project plans,
- prompt memory,
- new experiment notebooks unless they are part of the delivered package.
