# Progress Dashboard

Last curated update: 2026-07-10.

## Executive Snapshot

The machine-derived July 1 record supports a FRAMEWORK-FIRST direction pending participant confirmation. The July 15 package and H-layer specifications are provisional; M-02 through M-05 are not recorded. Ten H-layer iterations are accepted: iteration 008 reliability-only, iteration 009 metric/contract repair, and iteration 010 reliability-only are `NEUTRAL`. The canonical replay runner contains six experiments. EXP-009/010 remain provisional synthetic prototypes, EXP-011 is parked, and EXP-012 stops at safe N=0 / `NOT YET COMPUTABLE`. Live listener and prompt/context integration work remain blocked.

Run `.\scripts\build-progress-visualizations.ps1` for generated Mermaid status charts and a local HTML progress dashboard at `docs/dashboards/progress-visualizations.generated.html`.
Run `.\scripts\build-e2e-progress-report.ps1` for the full E2E progress report and local web page at `reports/generated/e2e_dashboard/index.html`.

| Area | Status | Evidence | Next Action |
| --- | --- | --- | --- |
| July 2026 supervisor redirect | Yellow / awaiting decisions | Machine-derived notes, enhanced evidence appendix, decision register, provisional skills/specs, and split diagrams. | Confirm M-01; record M-02..M-05 before selecting defaults or architecture. |
| Phase 0 truth/governance reconciliation | Complete | `docs/research/h-layer/phase-0-boundary-record.md`; source reconciliation, generated memory/wiki refreshes, focused tests, and protected-path checks pass. | Preserve unrelated changes and keep runtime work gated by recorded authorization. |
| Offline experiment program | Yellow / gated | Ten accepted iterations; iteration 009 repairs contracts/metrics, iteration 010 is a reliability-only rerun, and the separate conformance suite passes offline. | Preserve the six-experiment replay contract; keep iteration 011 and live integration blocked until their gates clear. |
| Passive shadow listener | Blocked | `allowed-touch-proposal.md` and template are proposals only. | Require M-05 plus separate exact-file authorization; default-off/fail-open if later approved. |
| MediVARIA PhD-track study plan | Yellow (draft; MV-P0 supervisor endorsement pending 2026-07-15) | `docs/research/medivaria/medivaria-study-plan.md` (2026-07-04): clinical transfer mapping, MV-RQ1-6, MV-P0..P5, clinical claim boundaries; one-pager archived ignored. Education-domain TRL3 metrics are not clinical evidence; no MediVARIA performance claims exist. | Present at 2026-07-15 (agenda section 8); confirm role split and first clinical guideline domain with Iris/Arnon. |
| Source baseline | Historical baseline available; current tree dirty | Safe GitHub baseline and tagged historical states exist; current branch is `agent/publish-hlayer-and-supervisor-package` at `134ce86` with local changes. | Preserve the dirty tree; compare protected fingerprints before/after offline work. |
| M1 Human Review Queue | Green | Implemented and tested. | Use as upstream evidence for artifact manifest. |
| M2 Human Feedback Manager | Green | Implemented and tested. | Include schema/docs/tests in artifact manifest. |
| M3 Human Judgment Memory | Green | Tag `milestone-m3-human-judgment-memory`. | Reference tag in thesis evidence. |
| M4A Memory Advisory Layer | Green | Tag `milestone-m4a-memory-advisory`. | Include advisory-only proof in manifest. |
| M4B-1 Memory-informed parallel comparison | Historical implementation / evaluation pending | Historical merge `944c922`; tag `research-state-m4b1-deterministic-comparison`. | Keep as evaluation history; do not infer current worktree cleanliness or improvement. |
| Visualizer model/result matching | Green | PR #7 real-display validated, merged as `78b261e`, tag `research-state-visualizer-ux-clean`. | Preserve no-silent-mismatch and read-only research-panel boundaries. |
| EXP-001 evaluation | Yellow | Initial mechanism/readiness run generated ignored `reports/generated/exp001/` tables. | Add held-out or cross-setting expert labels before accuracy/generalization claims. |
| EXP-002 expert labeling package | Yellow | Ignored `reports/generated/exp002/` package generated: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels. | Human/supervisor labels should fill at least 20 rows, preferably all 27 current rows. |
| Dashboard/wiki tracking gate | Historical pass / refresh needed | Runtime snapshot and manual sync pack exist; curated dashboard sources changed on 2026-07-10. | Announce generated-file refreshes, rebuild the outbox, then rerun `dashboard-health -RequireOutbox`. |
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
| P1 | Review and merge PR #6 schema hardening if clean. | Codex / reviewer | Open |
| P1 | Use release artifact bundle for external technical review. | Research lead / agents | Available |
| P1 | Record M-01..M-06; keep unaccepted architecture/dosage/verifier choices configurable. | Iris, Arnon, Ali | Awaiting meeting |
| P1 | Preserve iteration-009 metric semantics and iteration-010 reliability snapshot; keep iteration 011 and live prompt/context work gated. | Research agents | Blocked on decisions |
| P1 | Approve EXP-005 protocol and schedule two human reviewers; never prefill labels. | Supervisors / research lead | Human-gated |
| P1 | Keep M4B-2 and Agent 4/LLM behavior blocked. | All agents | Active rule |
| P1 | Enforce Codex isolation for VEGO-AI milestone implementation paths on `main`. | Codex | Active rule |
| P2 | Complete metadata-only audit for deferred artifacts. | Research lead / agents | In progress |
| P2 | Fill EXP-000 evidence mapping. | Research lead / agents | In progress |
| P3 | Grant Atlassian Rovo access for live Confluence sync. | User | Blocked |

## Confluence Tracking

The generated Confluence outbox should include a dashboard page sourced from:

- `docs/dashboards/status-snapshot.generated.md` (ignored runtime snapshot)
- `docs/dashboards/progress-visualizations.generated.md` (ignored generated visual summary)
- `docs/dashboards/e2e-dashboard.generated.md` (ignored generated E2E report)
- `docs/dashboards/progress-dashboard.md`
- `docs/dashboards/kpi-register.md`
- `docs/dashboards/results-dashboard.md`

Until live Confluence access is granted, `docs/confluence/outbox/` is the pending wiki update.
`docs/confluence/manual-sync-pack.generated.md` is the ignored fallback publishing package with the same curated page bodies and hashes.
