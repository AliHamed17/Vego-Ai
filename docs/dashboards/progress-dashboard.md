# Progress Dashboard

Last curated update: 2026-06-14 11:05 +03:00.

## Executive Snapshot

VEGO-AI is currently at the M4A research state with an M4B-1 conditional design contract recorded. The project has a validated staged human-AI co-reasoning path through advisory memory reuse, while future memory-informed comparison work must stay deterministic, experimental, parallel-only, and reviewed through a feature-branch PR.

| Area | Status | Evidence | Next Action |
| --- | --- | --- | --- |
| Source baseline | Green | Safe GitHub baseline and later `main` history exist. | Continue small, reviewable commits. |
| M1 Human Review Queue | Green | Implemented and tested. | Use as upstream evidence for artifact manifest. |
| M2 Human Feedback Manager | Green | Implemented and tested. | Include schema/docs/tests in artifact manifest. |
| M3 Human Judgment Memory | Green | Tag `milestone-m3-human-judgment-memory`. | Reference tag in thesis evidence. |
| M4A Memory Advisory Layer | Green | Tag `milestone-m4a-memory-advisory`. | Include advisory-only proof in manifest. |
| Dashboard/wiki tracking gate | Green | Runtime snapshot and manual sync pack are generated; `.\scripts\dashboard-health.ps1 -RequireOutbox` passes. | Keep running after wiki outbox builds. |
| M4B-1 Memory-informed parallel comparison | Yellow | Conditional design contract recorded in `docs/research/m4b-conditional-approval.md` and EXP-001. | Claude may implement M4B-1 only on `feature/memory-informed-comparison` with PR review. |
| Data/IRB audit | Red | Controlled artifacts still ignored and metadata-only. | Continue audit before sharing artifacts. |
| Confluence live tracking | Blocked | Outbox/manual sync pack exists; Atlassian access not granted as of 2026-06-14 13:40 +03:00; Chrome extension fallback unavailable as of 2026-06-13 13:50 +03:00. | Grant Rovo access or enable the Chrome extension route, then create/update child pages. |

## Milestone Flow

| Milestone | Research Meaning | State | Anchor |
| --- | --- | --- | --- |
| M1 | Human judgment is selectively triggered. | Done | Human Review Queue docs/tests. |
| M2 | Human decisions are structurally captured. | Done | Human Feedback Manager docs/tests. |
| M3 | Human judgment is stored as reusable memory. | Done | `milestone-m3-human-judgment-memory`. |
| M4A | Reusable judgment is retrieved as advisory evidence. | Done | `milestone-m4a-memory-advisory`. |
| M4B-1 | Memory advice may inform a deterministic parallel comparison. | Design contract approved | EXP-001 and `docs/research/m4b-conditional-approval.md`. |
| M4B-2 | Optional LLM/Agent 4 mode. | Deferred | Not approved. |
| M5 | Human-approved guideline refinement. | Planned | Roadmap. |
| M6 | Evaluation and thesis synthesis. | Planned | Evaluation plan and thesis outline. |

## Immediate Work Queue

| Priority | Work Item | Owner | Status |
| --- | --- | --- | --- |
| P1 | Refresh M1-M2-M3-M4A artifact ZIP and manifest. | Claude | Planned |
| P1 | Implement M4B-1 only after confirming the design contract. | Claude | Branch/PR only |
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
