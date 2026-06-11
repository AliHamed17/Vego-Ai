# Agent Memory

This folder is the shared project memory for Codex and Claude.

## Files

- `automation.md`: scripts and workflow for automatic prompt start/end memory handling.
- `claude-bootstrap-prompt.md`: paste-ready startup prompt for a fresh Claude session.
- `compiled-memory.md`: generated combined memory context from all memory files.
- `current-state.md`: latest known project state and short orientation.
- `progress.md`: milestones, current tasks, next steps, and completion status.
- `session-log.md`: chronological history of prompts and progress.
- `issues.md`: open, blocked, and resolved issues.
- `decisions.md`: durable project decisions and why they were made.
- `revert-log.md`: changed files and rollback notes.

## Workflow

1. At the start of a prompt, run `.\scripts\agent-memory-start.ps1`.
2. Read `compiled-memory.md`.
3. Do the requested work.
4. Before the final response, run `.\scripts\agent-memory-finish.ps1` with the prompt summary.
5. Update current state, progress, issues, and decisions manually when the work changes them.
6. If Git is initialized later, include commit hashes in the session and revert logs.

## Prompt Checklist

Use this checklist for every meaningful prompt:

- What did the user ask for?
- What context did memory provide?
- What changed?
- What commands/tests were run?
- What issues or decisions were discovered?
- What is the next best step?
- How can this be reverted?

## Revert Note

This folder was not a Git repository when memory tracking was created. Markdown logs help document rollback steps, but real file-level revert support needs Git or another version-control system. Before initializing Git, decide whether large archives such as `*.zip` should be committed or ignored.
