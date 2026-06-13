# Dashboards

This folder contains tracked dashboard source pages for VEGO-AI progress, KPIs, and validated results.

The dashboards are curated Markdown, designed for two uses:

- local project tracking in Git,
- generated Confluence dashboard pages through `scripts/build-confluence-wiki.ps1`.

## Files

| File | Purpose |
| --- | --- |
| `progress-dashboard.md` | Milestone and active-work status for quick project tracking. |
| `kpi-register.md` | KPI definitions, current values, status, source evidence, and next actions. |
| `results-dashboard.md` | Validated implementation and research result snapshots. |

## Update Rules

- Update these dashboards after meaningful milestone, experiment, review, or publication-state changes.
- Keep values evidence-backed; cite commits, tags, commands, tests, or docs.
- Do not copy controlled artifact contents into dashboards.
- Use metadata-only summaries until publishability is approved.
- The Confluence outbox is generated from these pages; do not edit `docs/confluence/outbox/` directly.
