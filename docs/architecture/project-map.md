# Project Map

## Layered Structure

| Layer | Folder | Rule |
| --- | --- | --- |
| Agent memory | `docs/agent-memory/` | Tracks prompt history, current state, issues, decisions, and rollback notes. |
| Preserved source package | `VEGO-AI/` | Original runnable package extracted from the delivery zip. Keep behavior stable unless an experiment requires change. |
| Future clean package | `src/` | Put reusable/refactored code here once behavior has tests. |
| Research method | `docs/research/` | Research questions, methodology, validity, ethics, and reproducibility. |
| Experiments | `experiments/` | One folder per experiment, registered in `experiments/registry.md`. |
| Data | `data/` | Controlled raw, interim, processed, and external data zones. |
| Outputs | `outputs/` | Generated result files, figures, logs, and exports. |
| Reporting | `reports/` | Human-readable reports and generated summaries. |
| Writing | `papers/`, `thesis/`, `presentations/` | Publication and degree artifacts. |

## Dependency Direction

Research notes may reference code and outputs. Code should not depend on research notes.

See `workspace-diagram.md` for a GitHub-rendered diagram of the workspace flow.

```text
research questions -> experiment protocol -> code/config -> outputs -> analysis -> paper/thesis claim
```

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
