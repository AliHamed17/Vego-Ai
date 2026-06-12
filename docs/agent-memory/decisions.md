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

## 2026-06-11 - Claude Bootstrap Prompt

- Decision: Keep a paste-ready Claude startup prompt at `docs/agent-memory/claude-bootstrap-prompt.md` and link it from `CLAUDE.md`.
- Reason: Fresh Claude sessions need a reliable way to load shared memory, respect the PhD architecture, and follow the same Git/data-safety workflow as Codex.
- Consequence: When starting Claude, the user can paste the bootstrap prompt so Claude treats project memory as context and updates it before final responses.

## 2026-06-11 - Workspace Diagram Format

- Decision: Use Markdown plus Mermaid for the first workspace architecture diagram at `docs/architecture/workspace-diagram.md`.
- Reason: GitHub renders Mermaid diagrams directly, so the diagram stays reviewable as text and avoids binary asset management.
- Consequence: Future architecture diagrams can follow the same text-first pattern unless a paper-quality figure export is needed.

## 2026-06-12 - Claude Local Settings Policy

- Decision: Ignore `.claude/*.local.json`.
- Reason: Claude local settings can contain machine-specific permission state and absolute paths that are not portable project configuration.
- Consequence: Portable Claude instructions remain tracked in `CLAUDE.md` and `docs/agent-memory/claude-bootstrap-prompt.md`; local permission state stays untracked.

## 2026-06-12 - Research OS And Confluence Sync

- Decision: Use metadata-only research registers for artifact audit, provenance, and publishability before exposing deferred artifacts.
- Decision: Generate four curated Confluence page bodies after meaningful prompts: wiki home, current state, update changelog, and research operations.
- Decision: Keep Confluence target IDs in ignored `docs/confluence/wiki-sync-config.local.json`; track only `wiki-sync-config.template.json`.
- Reason: The project needs an external latest wiki without copying controlled research artifacts or local machine state into Git/Confluence.
- Consequence: Until real Confluence IDs are configured, agents generate ignored outbox pages and report live sync as pending.

## 2026-06-12 - Confluence Live Target

- Decision: Use Confluence page `294914` in `https://alih10j.atlassian.net/wiki` as `VEGO-AI Wiki Home`.
- Decision: Use child pages under `294914` for current state, update changelog, and research operations.
- Decision: Store actual target/page IDs only in ignored `docs/confluence/wiki-sync-config.local.json`.
- Reason: The user provided the Confluence edit URL and requested the wiki stay updated with the latest project state.
- Consequence: Live sync is blocked until Atlassian Rovo access is granted for cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`; generated outbox remains the pending update meanwhile.

## 2026-06-12 - Milestone Branch/PR Discipline + Baseline Preservation

- Decision: From Milestone 3 onward, milestone CODE goes on a feature branch (e.g. `feature/human-judgment-memory`) and lands on `main` via a reviewed PR. No direct commits of milestone code to `main` without review (applies to both Codex and Claude). Shared-memory/doc updates may still be committed directly.
- Decision: Preserve the official VEGO-AI baseline (`2eeccb1`) as tag `official-vego-ai-baseline` and branch `baseline/official-vego-ai` on `origin`.
- Decision: Adopt `main` as the canonical development branch (it already carries baseline + M1 + M1.2 + M2 at `217150c`). Do NOT merge `master` into `main` with `--allow-unrelated-histories`. Keep `master` + `feature/human-review-queue` as a granular-history archive; PR #1 closed as superseded.
- Reason: A clean, reviewable audit trail is required for thesis reproducibility; M1/M2 had been published directly to `main`, losing per-milestone review.
- Consequence: Future milestones use feature branches + PRs into `main`, approved before merge.
- Status: M1 (Human Review Queue) + M1.2 (review_signature) + M2 (Human Feedback Manager) complete on `main`. M3 (Human Judgment Memory) is design-approved-pending — not yet coded.
