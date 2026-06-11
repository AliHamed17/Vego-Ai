# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

## Last Updated

- 2026-06-11 16:11 +03:00 by Codex.

## Project Goal

- Maintain a shared project memory so every prompt can use prior context, progress, issues, decisions, and rollback notes.
- Support both Codex and Claude with plain Markdown documentation.
- Maintain a PhD-ready VEGO-AI research workspace with source, experiments, data governance, papers, thesis work, and reproducibility documentation.

## Latest Known State

- Workspace root: `c:\Users\ahamed\vego-ai`
- Git status: repository initialized, safe baseline committed, and pushed to private GitHub repo `AliHamed17/Vego-Ai` on 2026-06-11.
- Current branch: `main`, tracking `origin/main`.
- Safe baseline merge commit: `76e7277`.
- Main visible source files at setup:
  - `Variability_MAS4MODELS2026_Mar28_IRB2איריס (1).pdf`
  - `VEGO-AI-20260611T112722Z-3-001.zip`
- Original source package extracted to `VEGO-AI/`.
- PhD/research architecture scaffold exists at the repository root.
- Safe GitHub baseline intentionally excludes root PDF, zip archives, generated outputs, compiled memory, model files, analysis files, eval outputs, visualizer bundled data, generated review queues, bundled executable, and `get-pip.py`.
- Core orientation files exist:
  - `README.md`
  - `PROJECT_CHARTER.md`
  - `docs/architecture/project-map.md`
  - `docs/research/research-plan.md`
  - `experiments/registry.md`
- Shared memory files exist in `docs/agent-memory/`.
- Prompt memory automation scripts exist in `scripts/`.
- Generated compiled memory file is created at `docs/agent-memory/compiled-memory.md` by `scripts/agent-memory-start.ps1`.
- Compiled memory now includes memory files plus the core project charter, architecture, research plan, and experiment registry.
- Root agent instruction files exist:
  - `AGENTS.md`
  - `CLAUDE.md`

## Working Agreement

- At the start of each meaningful prompt, agents should read the memory files as project resources.
- Agents should run `.\scripts\agent-memory-start.ps1` at prompt start and read `compiled-memory.md`.
- Agents should run `.\scripts\agent-memory-finish.ps1` before final response when meaningful work happened.
- Before final response, agents should update the memory files if the work changed project knowledge, files, progress, issues, decisions, or rollback notes.
- Do not store secrets, credentials, tokens, or sensitive personal data in memory.

## Active Risk

- Real revert support is now available through Git for tracked safe-baseline files.
- Prompt automation depends on Codex/Claude following the project instructions and scripts; no background service or native runtime hook is configured.
- Data sensitivity and IRB constraints need an audit before sharing or publishing data/examples.

## Next Best Step

- Audit data/IRB sensitivity before deciding whether deferred research artifacts can be published.
