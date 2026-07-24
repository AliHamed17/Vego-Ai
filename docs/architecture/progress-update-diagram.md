# Progress Update Diagram

This architecture view shows how progress updates move through VEGO-AI from project work to user-facing 4-hour check-ins.

For the operational contract, commands, and guardrails, see `../operations/progress-update-architecture.md`.

## Architecture Flow

```mermaid
flowchart TD
    Work[Project work, review, or experiment update] --> MemoryStart[agent-memory-start.ps1]
    MemoryStart --> Compiled[compiled-memory.md]

    Compiled --> MemoryDocs[Tracked memory docs<br/>current-state.md<br/>progress.md<br/>session-log.md]
    Compiled --> DashboardSources[Tracked dashboard sources<br/>progress-dashboard.md<br/>kpi-register.md<br/>results-dashboard.md]

    MemoryDocs --> VisualBuilder[build-progress-visualizations.ps1]
    DashboardSources --> VisualBuilder
    VisualBuilder --> VisualMd[progress-visualizations.generated.md<br/>Mermaid and summary tables]
    VisualBuilder --> VisualHtml[progress-visualizations.generated.html<br/>local card and bar dashboard]

    MemoryDocs --> E2EBuilder[build-e2e-progress-report.ps1]
    DashboardSources --> E2EBuilder
    E2EBuilder --> E2EMd[e2e-dashboard.generated.md<br/>full E2E report]
    E2EBuilder --> E2EHtml[reports/generated/e2e_dashboard/index.html<br/>local web dashboard]

    MemoryDocs --> WikiBuilder[build-confluence-wiki.ps1]
    DashboardSources --> WikiBuilder
    VisualMd --> WikiBuilder
    E2EMd --> WikiBuilder

    WikiBuilder --> Snapshot[status-snapshot.generated.md]
    WikiBuilder --> Outbox[docs/confluence/outbox<br/>curated wiki pages]
    WikiBuilder --> ManualPack[manual-sync-pack.generated.md]

    Snapshot --> Health[dashboard-health.ps1 -RequireOutbox]
    Outbox --> Health
    ManualPack --> Health
    VisualMd --> Health
    VisualHtml --> Health
    E2EMd --> Health
    E2EHtml --> Health

    Health --> Finish[agent-memory-finish.ps1]
    Finish --> Logs[session-log.md and revert-log.md]
    Logs --> Heartbeat[Codex heartbeat<br/>vego-ai-4-hour-progress-updates]
    Heartbeat --> User[Thread update to user]
```

## Update Responsibilities

| Component | Responsibility | Tracked |
| --- | --- | --- |
| `docs/agent-memory/current-state.md` | Latest project orientation. | Yes |
| `docs/agent-memory/progress.md` | Milestones, active work, completed work, and next steps. | Yes |
| `docs/dashboards/*.md` | Curated progress, KPI, and result dashboard source pages. | Yes |
| `docs/dashboards/progress-visualizations.generated.*` | Generated local visual views. | No |
| `docs/dashboards/e2e-dashboard.generated.md` | Generated full E2E progress report for Confluence/dashboard tracking. | No |
| `reports/generated/e2e_dashboard/index.html` | Generated local static web dashboard. | No |
| `docs/confluence/outbox/**` | Generated sanitized wiki page bodies. | No |
| `docs/confluence/manual-sync-pack.generated.md` | Generated manual publishing pack. | No |
| `vego-ai-4-hour-progress-updates` | Scheduled thread update automation. | Codex app |

## Minimal Update Path

```mermaid
sequenceDiagram
    participant A as Agent
    participant M as Memory
    participant D as Dashboards
    participant G as Generated Views
    participant H as Health Checks
    participant U as User

    A->>M: Update current-state/progress/session log
    A->>D: Update dashboard sources when KPI or result status changes
    A->>G: Build progress visualizations and wiki outbox
    A->>H: Run dashboard/research/project health
    H->>U: Report concise status, blockers, and next action
```

## Reading Order

1. `project-map.md` for workspace placement.
2. `progress-update-diagram.md` for architecture flow.
3. `../operations/progress-update-architecture.md` for commands, guardrails, and scheduled update rules.
4. `../dashboards/progress-visualizations.generated.html` for the current local visual state.
5. `../../reports/generated/e2e_dashboard/index.html` for the full E2E web dashboard.
