# Claude Project Memory

This project keeps shared agent memory in `docs/agent-memory/`. Claude and Codex should both read and update these files so progress is preserved across tools.

For a full startup prompt that can be pasted into a fresh Claude chat, use `docs/agent-memory/claude-bootstrap-prompt.md`.

For the current M4A artifact refresh and M4B design-only handoff, use `docs/agent-memory/claude-m4b-handoff-prompt.md` after the normal startup routine.

## Before Working

Treat the memory files as project resources. Use them to understand the flow, avoid repeating old work, and make better decisions.

1. Run `.\scripts\agent-memory-start.ps1`.
2. Read `docs/agent-memory/compiled-memory.md`.
3. Use the compiled memory to understand current state, progress, issues, decisions, recent prompt history, rollback notes, project architecture, research plan, and experiment registry.
4. Check whether Git is available before relying on revert/rollback claims.

## After Each Prompt

If the prompt included analysis, edits, debugging, planning, or a decision, update:

- Run `.\scripts\agent-memory-finish.ps1` with a concise summary so `session-log.md`, `revert-log.md`, and `compiled-memory.md` are updated.
- `docs/agent-memory/current-state.md` when the project state changes.
- `docs/agent-memory/progress.md` when milestones, tasks, or next steps change.
- `docs/agent-memory/issues.md` with new/resolved/blocked issues.
- `docs/agent-memory/decisions.md` with durable decisions.
- `docs/agent-memory/revert-log.md` with changed files and rollback notes.
- `docs/dashboards/` when progress, KPI values, validated results, or Confluence tracking status changes.
- Run `.\scripts\build-confluence-wiki.ps1` after memory updates.
- If `docs/confluence/wiki-sync-config.local.json` contains real Confluence IDs and Atlassian Rovo has access, update the configured Confluence pages with Markdown content from `docs/confluence/outbox/`.
- If IDs are missing or Atlassian access is not granted, treat the generated `docs/confluence/outbox/` files as the pending wiki update and report the blocked live sync clearly.
- Confluence sync is an agent-enforced workflow, not a background service.

## Entry Standards

- Use exact timestamps when possible.
- Keep notes short, concrete, and useful for the next agent.
- Never record secrets, credentials, tokens, or sensitive personal data.
- Do not fabricate missing context; write `Unknown` when needed.
- Include commands/tests run and their results.
- Include repo-relative paths for changed files.
- Prefer updating the newest/current summary instead of forcing future agents to reconstruct everything from old entries.

## Memory Map

- `docs/agent-memory/current-state.md`: quick orientation and latest known state.
- `docs/agent-memory/progress.md`: milestones, active tasks, and next steps.
- `docs/agent-memory/session-log.md`: chronological prompt history.
- `docs/agent-memory/issues.md`: open, blocked, and resolved issues.
- `docs/agent-memory/decisions.md`: durable decisions.
- `docs/agent-memory/revert-log.md`: change and rollback notes.
- `docs/agent-memory/automation.md`: script workflow for prompt start/end.
- `docs/agent-memory/compiled-memory.md`: generated combined memory file.
- `docs/dashboards/`: progress, KPI, and results dashboards for local and Confluence tracking.
- `docs/confluence/wiki-sync.md`: Confluence wiki sync workflow and target configuration rules.
