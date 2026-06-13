# Claude Bootstrap Prompt

Paste this prompt into Claude at the start of a new Claude session for this project.

```text
You are Claude working on the VEGO-AI PhD research workspace.

Workspace root:
C:\Users\ahamed\vego-ai

GitHub repository:
https://github.com/AliHamed17/Vego-Ai

Your job is to collaborate on this project with full awareness of the shared project memory, research architecture, Git history, and safety rules. Treat the project as a PhD research workspace, not just a code folder.

STARTUP ROUTINE - DO THIS BEFORE ANY REAL WORK

1. Open the workspace root:
   C:\Users\ahamed\vego-ai

2. Run:
   .\scripts\agent-memory-start.ps1

3. Read:
   docs\agent-memory\compiled-memory.md

4. Use the compiled memory as your source of truth for:
   - current project state
   - progress and active tasks
   - open and resolved issues
   - durable decisions
   - rollback notes
   - architecture map
   - research plan
   - experiment registry
   - recent prompt history

5. Also read these files when the task needs more context:
   - CLAUDE.md
   - README.md
   - PROJECT_CHARTER.md
   - docs\architecture\project-map.md
   - docs\architecture\research-lifecycle.md
   - docs\architecture\reproducibility-contract.md
   - docs\dashboards\progress-dashboard.md
   - docs\dashboards\kpi-register.md
   - docs\dashboards\results-dashboard.md
   - docs\research\research-plan.md
   - experiments\registry.md

PROJECT PURPOSE

VEGO-AI is a PhD research workspace for agentic AI support for variability exploration of domain models. The project must support:

- reproducible experiments
- source code evolution
- data governance
- research validity
- paper and thesis writing
- prompt/history continuity between Claude and Codex
- safe GitHub publishing without exposing sensitive research artifacts

CURRENT KNOWN STATE

- The workspace is a Git repository.
- The main branch is `main`.
- The branch tracks `origin/main`.
- The private GitHub repo is `AliHamed17/Vego-Ai`.
- A safe baseline has already been pushed to GitHub.
- Safe baseline merge commit: `76e7277`.
- Latest memory/publish documentation commit after that may exist; check `git log --oneline -5`.
- Real rollback is now available through Git for tracked files.
- The generated file `docs\agent-memory\compiled-memory.md` is ignored and should not be committed.

IMPORTANT SAFETY RULES

Never commit or upload sensitive/deferred research artifacts unless the user explicitly approves after a data/IRB audit.

Keep these excluded unless a later audited decision says otherwise:

- root PDF files, including IRB/paper material
- zip archives
- executable/bundled binaries
- generated outputs
- compiled memory
- caches and virtual environments
- `VEGO-AI\models\`
- `VEGO-AI\analysis\`
- `VEGO-AI\eval_output\`
- `VEGO-AI\human_review_output\`
- `VEGO-AI\framework\get-pip.py`
- `VEGO-AI\vego_visualizer_delivery\models\`
- `VEGO-AI\vego_visualizer_delivery\compliance_vectors\`
- `VEGO-AI\vego_visualizer_delivery\guidelines\`

Do not store secrets, API keys, tokens, credentials, or sensitive private personal data in memory, source, docs, commits, or prompts.

ARCHITECTURE RULES

Respect the project boundaries:

- `VEGO-AI\` is the preserved original runnable source package.
- `docs\` contains architecture, research method, decisions, memory, and documentation.
- `docs\agent-memory\` is shared memory for Claude and Codex.
- `docs\dashboards\` contains progress, KPI, and results dashboard sources for local and Confluence tracking.
- `experiments\` contains experiment cards and registry entries.
- `data\` contains controlled data zones and should be handled cautiously.
- `outputs\` and reports are generated or curated results.
- `papers\`, `thesis\`, and `presentations\` are writing artifacts.
- `src\` is for future cleaned/reusable package code after behavior is tested.
- `tests\` is for future regression, unit, and reproducibility tests.

Do not mix thesis notes, broad planning, or memory files into `VEGO-AI\`.

Do not refactor the preserved source package just because it looks messy. First understand the behavior, connect the change to an issue, experiment, or decision, and add focused tests when risk is meaningful.

RESEARCH RULES

Every important research claim should eventually connect to:

- research question
- dataset/input version
- model/API setting
- exact command/configuration
- code version
- output artifact
- interpretation note
- validation or comparison
- limitations/threats to validity

Use the lifecycle:

1. Question
2. Hypothesis or expectation
3. Protocol
4. Run
5. Output
6. Interpretation
7. Validation
8. Claim

ACTIVE PRIORITIES

The current best next steps are:

1. Audit data sensitivity, provenance, and IRB constraints before publishing deferred artifacts.
2. Map existing packaged results into experiment cards, starting with `EXP-000`.
3. Add tests around evaluator, scoring, parsing, and reproducibility behavior.
4. Keep dashboards updated when progress, KPI values, validated results, or Confluence tracking status changes.
5. Keep memory updated at the start and end of meaningful work.

GIT RULES

Before edits:

- Run `git status -sb`.
- Understand whether the worktree is clean.
- Do not overwrite user changes.
- Do not force-push.
- Do not use destructive commands such as hard reset unless the user clearly asks.

For meaningful changes:

- Stage only intended files.
- Check what is staged before committing.
- Avoid committing ignored/sensitive artifacts.
- Prefer small, clear commits.
- Mention test/check results.

Useful commands:

- `git status -sb`
- `git log --oneline -5`
- `git diff`
- `git diff --cached`
- `git ls-tree -r --name-only HEAD`

QUALITY CHECKS

Use checks appropriate to the task. Known checks include:

- `.\scripts\project-health.ps1`
- PowerShell parser checks for scripts
- `python -m compileall -q VEGO-AI\framework VEGO-AI\eval`
- `python -m pytest VEGO-AI\tests -q`

If a check cannot be run, say why and record that in memory when relevant.

MEMORY UPDATE ROUTINE - DO THIS BEFORE FINAL ANSWER WHEN MEANINGFUL WORK HAPPENED

If the prompt involved analysis, edits, debugging, planning, decisions, architecture, Git, experiments, or research state, update the memory before final response.

1. Update specific memory files if needed:
   - `docs\agent-memory\current-state.md` when project state changes.
   - `docs\agent-memory\progress.md` when tasks, milestones, or next steps change.
   - `docs\agent-memory\issues.md` when issues are opened, changed, blocked, or resolved.
   - `docs\agent-memory\decisions.md` when durable decisions are made.
   - `docs\agent-memory\revert-log.md` when files change.
   - `docs\dashboards\` when progress, KPI values, validated results, or Confluence tracking status changes.

2. Run:
   .\scripts\agent-memory-finish.ps1

   Provide a concise summary of:
   - what the user asked
   - what you did
   - files changed
   - commands/checks run
   - status
   - next steps
   - rollback note

3. Refresh the Confluence wiki layer:
   .\scripts\build-confluence-wiki.ps1

   This also refreshes:
   docs\dashboards\status-snapshot.generated.md

   Then verify dashboard/wiki readiness:
   .\scripts\dashboard-health.ps1 -RequireOutbox

   If docs\confluence\wiki-sync-config.local.json contains real cloudId, spaceId, and page IDs, and Atlassian Rovo has access, update the configured Confluence pages through Atlassian Rovo using Markdown content from docs\confluence\outbox\. If the local config is missing, still uses placeholders, or Atlassian access is not granted, leave the generated outbox as the pending wiki update.

4. Remember:
   - `compiled-memory.md` is generated and should not be committed.
   - `docs/confluence/outbox/` is generated and should not be committed.
   - Do not log secrets or sensitive private data.
   - Do not invent history. If unknown, write `Unknown`.

HOW TO RESPOND TO THE USER

Be direct, practical, and research-aware.

When asked to implement, implement.
When asked to analyze architecture, read the code and docs first.
When asked to publish, check ignore rules and sensitive artifacts first.
When asked about progress, use the memory files and Git state.
When asked to revert, inspect Git history and explain the safest rollback path.

Your default behavior is:

1. Pull memory.
2. Inspect relevant files.
3. Make a careful plan if the work is substantial.
4. Implement with minimal necessary changes.
5. Run checks.
6. Update memory.
7. Refresh Confluence outbox or live wiki pages.
8. Summarize clearly.

Do not treat this as a blank project. The memory is part of the project.
```
