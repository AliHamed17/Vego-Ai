# Agent Memory Index

This page is the central navigator and index for the VEGO-AI prompt memory system (`docs/agent-memory/`). It maps each file's purpose, scope, and cross-references to help agents and human reviews find context quickly.

---

## 1. Memory Catalog

| File | Type | Target size | Purpose | Main Cross-References |
|---|---|---|---|---|
| [current-state.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/current-state.md) | State | < 5 KB | Restructured orientation snapshot (blockers, next action, agreement) | `issues.md`, `review-state.md`, `progress.md` |
| [shared-state-report.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/shared-state-report.md) | Report | < 25 KB | High-level research context and allowed/blocked claim framework | `phd-thesis-optimization-plan.md` |
| [review-state.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/review-state.md) | Review | < 2 KB | Active project review verdict (gated state checks) | `alignment-control.md` |
| [progress.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/progress.md) | Log | < 40 KB | Chronological tasks list and completed milestone timeline | `PROGRESS_TRACKER.md` |
| [issues.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/issues.md) | Tracker | < 10 KB | Outstanding, blocked, and resolved issues/risks | `current-state.md` |
| [decisions.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/decisions.md) | Archive | < 30 KB | Durable design and governance decisions with justifications | `current-state.md` |
| [resource-memory.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/resource-memory.md) | Index | < 15 KB | Indexes literature, presentations, meeting notes, chapters, and script tools | `2026-07-03-supervisor-meeting.md` |
| [session-log.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/session-log.md) | Log | < 120 KB | Pruned chronological prompt history (last 14 days) | `session-log-archive.md` |
| [session-log-archive.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/session-log-archive.md) | Archive | Unlimited | Historical prompt summaries older than 14 days | `session-log.md` |
| [revert-log.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/revert-log.md) | Log | < 80 KB | Active file rollback notes and Git tags (last 30 days) | `revert-log-archive.md` |
| [revert-log-archive.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/revert-log-archive.md) | Archive | Unlimited | Historical revert entries older than 30 days | `revert-log.md` |
| [compiled-memory-t1.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/compiled-memory-t1.md) | Compiled | < 25 KB | Tier 1 Quick Start compiled orientation (start script generated) | `current-state.md`, `review-state.md` |
| [compiled-memory-t2.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/compiled-memory-t2.md) | Compiled | < 130 KB | Tier 2 Working Context compiled files (start script generated) | `issues.md`, `decisions.md`, `progress.md` |
| [compiled-memory.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/compiled-memory.md) | Compiled | < 500 KB | Tier 3 Full Archive compilation (start script generated) | All memory and project docs |

---

## 2. Meeting Notes Index

Meeting notes from supervisor/collaborator presentations and syncs are stored under `docs/agent-memory/meeting-notes/`:

* [2026-07-03-supervisor-meeting.md](file:///c:/Users/ahamed/vego-ai/docs/agent-memory/meeting-notes/2026-07-03-supervisor-meeting.md) — Hebrew video transcribed. Action items include Agent Skills definitions and configurable bi-directional feedback interfaces.

---

## 3. Memory Navigation & Commands

### Search memory
Search across all memory and meeting notes for a specific query:
```powershell
.\scripts\search-memory.ps1 -Query "M4B"
```

### Health check
Validate the format, size, staleness, and integrity of the memory files:
```powershell
.\scripts\memory-health.ps1
```

### Pull memory (start of prompt)
Generate all tiered compiled files (T1, T2, T3) and show quick health:
```powershell
.\scripts\agent-memory-start.ps1
```

### Update memory (end of prompt)
Record actions, changes, and rollback notes, auto-archiving entries:
```powershell
.\scripts\agent-memory-finish.ps1 -Agent "Codex" -Title "Title" -Request "User Request" -Actions "Action" -FilesChanged "file.md" -RollbackNote "Rollback note"
```
