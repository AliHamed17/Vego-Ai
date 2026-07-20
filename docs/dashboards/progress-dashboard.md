# Progress Dashboard

Last curated update: 2026-07-03 by Claude.

## Executive Snapshot

The 2026-07-01 supervisor meeting redirected the project: the human-judgment layer is being reframed as an H-layer (H1/H2/H3) continuous listener over both VEGO-AI communication circles, framework redesign is the active track, and the evaluation track (M4A/M4B-1 instruments plus EXP-001..005 with the EXP-005 real-label gate) is PARKED in a separate diagram until the framework stabilizes. Active plan: `docs/research/extension-plan-2026-07-supervisor-redirect.md`. Implementation state remains frozen at M4B-1; behavior changes stay blocked.

| Area | Status | Evidence | Next Action |
| --- | --- | --- | --- |
| Supervisor redirect (2026-07-01) | Green | Meeting notes, extension plan, H-layer skills map + prompt requirements, framework/evaluation diagrams all tracked. | Present the 2026-07-15 package; capture Iris's decisions on the open questions. |
| Source baseline | Green | Safe GitHub baseline and later `main` history exist. | Continue small, reviewable commits. |
| M1 Human Review Queue | Green | Implemented and tested. | Use as upstream evidence for artifact manifest. |
| M2 Human Feedback Manager | Green | Implemented and tested. | Include schema/docs/tests in artifact manifest. |
| M3 Human Judgment Memory | Green | Tag `milestone-m3-human-judgment-memory`. | Reference tag in thesis evidence. |
| M4A Memory Advisory Layer | Green | Tag `milestone-m4a-memory-advisory`. | Include advisory-only proof in manifest. |
| M4B-1 Memory-informed parallel comparison | Green | Merged as `944c922`; tag `research-state-m4b1-deterministic-comparison`. | Run EXP-001/C4B before making improvement claims. |
| Visualizer model/result matching | Green | PR #7 real-display validated, merged as `78b261e`, tag `research-state-visualizer-ux-clean`. | Preserve no-silent-mismatch and read-only research-panel boundaries. |
| EXP-001 evaluation | Yellow | Initial mechanism/readiness run generated ignored `reports/generated/exp001/` tables. | Add held-out or cross-setting expert labels before accuracy/generalization claims. |
| EXP-002 expert labeling package | Yellow | Ignored `reports/generated/exp002/` package generated: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels. | Human/supervisor labels should fill at least 20 rows, preferably all 27 current rows. |
| Dashboard/wiki tracking gate | Green | Runtime snapshot and manual sync pack are generated; `.\scripts\dashboard-health.ps1 -RequireOutbox` passes. | Keep running after wiki outbox builds. |
| Data/IRB audit | Red | Controlled artifacts still ignored and metadata-only. | Continue audit before sharing artifacts. |
| Confluence live tracking | Blocked | Outbox/manual sync pack exists; Atlassian Rovo cloud access not explicitly granted as of 2026-06-14 14:50 +03:00; Chrome extension fallback unavailable as of 2026-06-13 13:50 +03:00. | Grant Rovo access or enable the Chrome extension route, then create/update child pages. |

## Milestone Flow

| Milestone | Research Meaning | State | Anchor |
| --- | --- | --- | --- |
| M1 | Human judgment is selectively triggered. | Done | Human Review Queue docs/tests. |
| M2 | Human decisions are structurally captured. | Done | Human Feedback Manager docs/tests. |
| M3 | Human judgment is stored as reusable memory. | Done | `milestone-m3-human-judgment-memory`. |
| M4A | Reusable judgment is retrieved as advisory evidence. | Done | `milestone-m4a-memory-advisory`. |
| M4B-1 | Memory advice may inform a deterministic parallel comparison. | Done / experimental | `research-state-m4b1-deterministic-comparison`; EXP-001 evaluation still pending. |
| M4B-2 | Optional LLM/Agent 4 mode. | Deferred | Not approved. |
| M5 | Human-approved guideline refinement. | Planned | Roadmap. |
| M6 | Evaluation and thesis synthesis. | Planned | Evaluation plan and thesis outline. |

## Immediate Work Queue

| Priority | Work Item | Owner | Status |
| --- | --- | --- | --- |
| P0 | Finalize 2026-07-15 meeting package: skills map, prompt requirements, framework diagram, open questions. | Ali / agents | In progress |
| P0 | Literature survey per extended taxonomy (Pnina's course; present mid-Aug, submit end-Sep/Oct). | Ali | Open |
| P1 | Review and merge PR #6 schema hardening if clean. | Codex / reviewer | Open |
| P1 | Use release artifact bundle for external technical review. | Research lead / agents | Available |
| P1 | Fill EXP-002 expert labeling sheet and rerun EXP-001/generalization-safe evaluation. | Research lead / agents | Next |
| P1 | Keep M4B-2 and Agent 4/LLM behavior blocked. | All agents | Active rule |
| P1 | Enforce Codex isolation for VEGO-AI milestone implementation paths on `main`. | Codex | Active rule |
| P2 | Complete metadata-only audit for deferred artifacts. | Research lead / agents | In progress |
| P2 | Fill EXP-000 evidence mapping. | Research lead / agents | In progress |
| P3 | Grant Atlassian Rovo access for live Confluence sync. | User | Blocked |

## Confluence Tracking

The generated Confluence outbox should include a dashboard page sourced from:

- `docs/dashboards/status-snapshot.generated.md` (ignored runtime snapshot)
- `docs/dashboards/progress-dashboard.md`
- `docs/dashboards/kpi-register.md`
- `docs/dashboards/results-dashboard.md`

Until live Confluence access is granted, `docs/confluence/outbox/` is the pending wiki update.
`docs/confluence/manual-sync-pack.generated.md` is the ignored fallback publishing package with the same curated page bodies and hashes.
