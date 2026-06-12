# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

## Last Updated

- 2026-06-12 20:41 +03:00 by Codex.

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
- Human-feedback workflow files now include `VEGO-AI/framework/human_feedback_manager.py`, `VEGO-AI/inputs/human_feedback.example.jsonl`, `VEGO-AI/schemas/human_feedback.schema.json`, and feedback attachment/status fields in `VEGO-AI/schemas/human_review_item.schema.json`.
- Human-feedback manager documentation and tests now exist at `VEGO-AI/docs/human_feedback_manager.md` and `VEGO-AI/tests/test_human_feedback_manager.py`.
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
- A paste-ready Claude startup prompt exists at `docs/agent-memory/claude-bootstrap-prompt.md`.
- A GitHub-rendered Mermaid workspace diagram exists at `docs/architecture/workspace-diagram.md`.
- Research OS registers exist for artifact audit, provenance, and publishability under `docs/research/`.
- Confluence wiki sync infrastructure exists under `docs/confluence/`; local target config points to `https://alih10j.atlassian.net/wiki`, cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`, space `~71202099edcf0e26ec40cea521806deb9e9687`, home page `294914`.
- `scripts/build-confluence-wiki.ps1` generates ignored curated wiki pages in `docs/confluence/outbox/`.
- `scripts/research-health.ps1` checks research infrastructure, experiment folders, Confluence config template JSON, and forbidden tracked artifacts.

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
- Local Claude permission state is ignored via `.claude/*.local.json`.
- Confluence sync currently operates as generated outbox only because Atlassian Rovo reports cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted.

## Next Best Step

- Grant Atlassian Rovo access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`; then create/update the Confluence child pages and record their IDs locally.
