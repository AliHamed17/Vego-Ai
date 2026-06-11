# Decisions

Durable decisions for this project.

## 2026-06-11 - Shared Agent Memory

- Decision: Use root-level `AGENTS.md` for Codex instructions and `CLAUDE.md` for Claude instructions.
- Decision: Store shared progress, issues, decisions, and rollback notes in `docs/agent-memory/`.
- Reason: Both agents can read plain Markdown files, which keeps the history portable and easy to review.
- Consequence: Every future prompt that involves meaningful work should update the memory files before the final response.

## 2026-06-11 - Current-State First Workflow

- Decision: Add `docs/agent-memory/current-state.md` and `docs/agent-memory/progress.md`.
- Reason: Future prompts need a quick way to understand project flow without rereading every historical entry.
- Consequence: Agents should use current-state and progress as the first memory resources, then consult detailed logs/issues/decisions as needed.

## 2026-06-11 - Scripted Prompt Memory

- Decision: Add PowerShell scripts for prompt start and prompt finish.
- Reason: The user wants memory files pulled and updated automatically at each prompt.
- Consequence: Agents should run `scripts/agent-memory-start.ps1` at prompt start, then `scripts/agent-memory-finish.ps1` before the final response when meaningful work happened.
- Boundary: Scripts can standardize memory updates, but agents must still use judgment for issues, decisions, and current-state changes.

## 2026-06-11 - PhD Research Workspace Architecture

- Decision: Preserve the extracted source package in `VEGO-AI/` and build the PhD research architecture around it at the repository root.
- Decision: Use dedicated folders for experiments, data zones, literature, papers, thesis, reports, outputs, tests, future cleaned source, and project documentation.
- Reason: The project needs to support scientific traceability, reproducibility, writing, data governance, prompt memory, and software evolution at the same time.
- Consequence: Research notes and thesis/paper materials should stay outside `VEGO-AI/`; source behavior changes inside `VEGO-AI/` should be linked to experiments or decisions.

## 2026-06-11 - Git And Generated Artifact Policy

- Decision: Initialize Git and add `.gitignore` before the first baseline commit.
- Decision: Ignore large archives, generated outputs, raw/interim/processed/external data zones, Python caches, virtual environments, and generated compiled memory.
- Reason: Version control should track source, docs, templates, and lightweight reproducibility records without accidentally committing secrets, bulky generated data, or disposable artifacts.
- Consequence: A baseline commit is still needed before Git gives strong rollback support.

## 2026-06-11 - Safe GitHub Baseline

- Decision: Publish directly to private GitHub repo `AliHamed17/Vego-Ai` on `main` without force-pushing.
- Decision: Preserve remote README-only history with an `ours` merge.
- Decision: Exclude root PDF, zip archives, generated outputs, compiled memory, model files, analysis files, eval outputs, visualizer bundled data, generated review queues, bundled executable, and `get-pip.py` from the safe baseline.
- Reason: The repo should have durable GitHub history while avoiding premature upload of research artifacts that need data/IRB review.
- Consequence: Deferred artifacts remain local and ignored until the data/provenance audit decides what can be shared.
