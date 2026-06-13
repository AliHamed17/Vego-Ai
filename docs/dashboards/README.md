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

## Checks

- Run `.\scripts\dashboard-health.ps1` to verify dashboard sources, Confluence template wiring, local sync config shape, and generated outbox when present.
- Run `.\scripts\dashboard-health.ps1 -RequireOutbox` after `.\scripts\build-confluence-wiki.ps1` to require all five generated wiki page bodies.
- Run `.\scripts\dashboard-health.ps1 -RequireLivePageIds` only after Atlassian Rovo access is granted and child page IDs are recorded locally.

## Update Rules

- Update these dashboards after meaningful milestone, experiment, review, or publication-state changes.
- Keep values evidence-backed; cite commits, tags, commands, tests, or docs.
- Do not copy controlled artifact contents into dashboards.
- Use metadata-only summaries until publishability is approved.
- The Confluence outbox is generated from these pages; do not edit `docs/confluence/outbox/` directly.
