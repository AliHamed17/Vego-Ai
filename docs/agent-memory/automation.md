# Memory Automation

Use these scripts so every prompt pulls the same memory resources and writes progress in a consistent format.

## Start Every Prompt

Run:

```powershell
.\scripts\agent-memory-start.ps1
```

Then read:

```text
docs/agent-memory/compiled-memory.md
```

This generated file pulls together memory plus the core project orientation docs:

- `current-state.md`
- `progress.md`
- `resource-memory.md`
- `issues.md`
- `decisions.md`
- `session-log.md`
- `revert-log.md`
- `README.md`
- root `README.md`
- `PROJECT_CHARTER.md`
- architecture map/lifecycle/reproducibility/source-package docs
- `docs/research/research-plan.md`
- `experiments/registry.md`

For HITL, Human-AI collaboration, expert-labeling, XAI, or governance prompts, `resource-memory.md` points both Codex and Claude to `literature/hitl-resource-pack/` and summarizes how those resources should be used.

## Finish Every Meaningful Prompt

Run:

```powershell
.\scripts\agent-memory-finish.ps1 `
  -Agent "Codex" `
  -Title "Short Title" `
  -Request "What the user asked for" `
  -Actions "Action one","Action two" `
  -FilesChanged "path/to/file.md","path/to/other-file.ps1" `
  -Commands "command that was run" `
  -Status "completed" `
  -NextSteps "Next best step" `
  -RollbackNote "How to undo this prompt's changes"
```

The finish script appends to `session-log.md`, optionally appends to `revert-log.md`, and regenerates `compiled-memory.md`.

Then refresh the Confluence wiki layer:

```powershell
.\scripts\build-confluence-wiki.ps1
```

If `docs/confluence/wiki-sync-config.local.json` contains real `cloudId`, `spaceId`, and page IDs, and Atlassian Rovo has access, update the configured Confluence pages through Atlassian Rovo with Markdown content from `docs/confluence/outbox/`. If the local config is missing, still has placeholders, or Atlassian access is not granted, leave the ignored outbox files as the pending wiki update.

Confluence sync is agent-enforced automation. It is not a background service.

## What Still Requires Agent Judgment

The scripts can pull files and standardize entries, but they cannot safely infer new issues, decisions, or project state. Agents must still update these files when relevant:

- `current-state.md`
- `progress.md`
- `issues.md`
- `decisions.md`
- `resource-memory.md`

This is project-level automation: Codex and Claude are instructed to run the scripts at prompt start and finish. It is not a background service or native runtime hook.
