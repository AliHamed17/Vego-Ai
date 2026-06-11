# Codex Project Memory

This project uses shared memory files so Codex and Claude can track prompts, progress, issues, decisions, and rollback notes in the same place.

## Start Of Every Prompt

Treat the memory files as project resources. Use them to understand the flow, avoid repeating old work, and make better decisions.

1. Run `.\scripts\agent-memory-start.ps1`.
2. Read `docs/agent-memory/compiled-memory.md`.
3. Use the compiled memory to understand current state, progress, issues, decisions, recent prompt history, rollback notes, project architecture, research plan, and experiment registry.
4. Check whether the folder is a Git repository before promising revert support.

## End Of Every Prompt

Update the memory files before the final answer whenever the prompt involved analysis, file changes, debugging, planning, or decisions.

- Run `.\scripts\agent-memory-finish.ps1` with a concise summary so `session-log.md`, `revert-log.md`, and `compiled-memory.md` are updated.
- Update `docs/agent-memory/current-state.md` when the project state changes.
- Update `docs/agent-memory/progress.md` when milestones, tasks, or next steps change.
- Update `docs/agent-memory/issues.md` when an issue is found, changed, blocked, or resolved.
- Update `docs/agent-memory/decisions.md` when a durable decision is made.
- Update `docs/agent-memory/revert-log.md` for any file changes, including a short rollback note.

## Logging Rules

- Use exact dates and times when available.
- Keep entries concise but specific enough that another agent can continue the work.
- Do not log secrets, tokens, credentials, or private personal data.
- Do not invent history. If something is unknown, write `Unknown`.
- Mention commands/tests run and whether they passed.
- Mention files changed using repo-relative paths.
- Prefer updating the newest/current summary instead of forcing future agents to reconstruct everything from old entries.

## Current Project Snapshot

- Created: 2026-06-11 14:43 +03:00
- Workspace root: `c:\Users\ahamed\vego-ai`
- Git status at setup: not a Git repository
- Top-level files observed at setup:
  - `Variability_MAS4MODELS2026_Mar28_IRB2איריס (1).pdf`
  - `VEGO-AI-20260611T112722Z-3-001.zip`

## Memory Map

- `docs/agent-memory/current-state.md`: quick orientation and latest known state.
- `docs/agent-memory/progress.md`: milestones, active tasks, and next steps.
- `docs/agent-memory/session-log.md`: chronological prompt history.
- `docs/agent-memory/issues.md`: open, blocked, and resolved issues.
- `docs/agent-memory/decisions.md`: durable decisions.
- `docs/agent-memory/revert-log.md`: change and rollback notes.
- `docs/agent-memory/automation.md`: script workflow for prompt start/end.
- `docs/agent-memory/compiled-memory.md`: generated combined memory file.
