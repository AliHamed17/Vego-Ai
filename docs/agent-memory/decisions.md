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
- Decision: Generate five curated Confluence page bodies after meaningful prompts: wiki home, current state, progress dashboard, update changelog, and research operations.
- Decision: Keep Confluence target IDs in ignored `docs/confluence/wiki-sync-config.local.json`; track only `wiki-sync-config.template.json`.
- Reason: The project needs an external latest wiki without copying controlled research artifacts or local machine state into Git/Confluence.
- Consequence: Until real Confluence IDs are configured, agents generate ignored outbox pages and report live sync as pending.

## 2026-06-12 - Confluence Live Target

- Decision: Use Confluence page `294914` in `https://alih10j.atlassian.net/wiki` as `VEGO-AI Wiki Home`.
- Decision: Use child pages under `294914` for current state, progress dashboard, update changelog, and research operations.
- Decision: Store actual target/page IDs only in ignored `docs/confluence/wiki-sync-config.local.json`.
- Reason: The user provided the Confluence edit URL and requested the wiki stay updated with the latest project state.
- Consequence: Live sync is blocked until Atlassian Rovo access is granted for cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`; generated outbox remains the pending update meanwhile.

## 2026-06-13 - Dashboard/KPI Tracking

- Decision: Use tracked Markdown files under `docs/dashboards/` as the source of truth for progress, KPI, and results dashboards.
- Decision: Generate a dedicated `VEGO-AI Progress Dashboard` Confluence outbox page from those tracked dashboard sources.
- Decision: Generate an ignored runtime snapshot at `docs/dashboards/status-snapshot.generated.md` and embed it in the Confluence Progress Dashboard.
- Decision: Generate an ignored manual sync pack at `docs/confluence/manual-sync-pack.generated.md` with curated page bodies, target metadata, and hashes for approved fallback publishing.
- Decision: Add dashboard files to research health so progress tracking becomes part of the standard quality gate.
- Decision: Add `scripts/dashboard-health.ps1` to verify dashboard sources, KPI rows, Confluence builder wiring, config page slots, and generated outbox readiness.
- Reason: The user wants progress and research results visible in Confluence without copying controlled artifacts or relying on ad hoc summaries.
- Consequence: Agents should update `docs/dashboards/` whenever progress, KPI values, validated results, or Confluence tracking status changes, then regenerate the runtime snapshot/Confluence outbox/manual sync pack and run `.\scripts\dashboard-health.ps1 -RequireOutbox`.

## 2026-06-12 - Milestone Branch/PR Discipline + Baseline Preservation

- Decision: From Milestone 3 onward, milestone CODE goes on a feature branch (e.g. `feature/human-judgment-memory`) and lands on `main` via a reviewed PR. No direct commits of milestone code to `main` without review (applies to both Codex and Claude). Shared-memory/doc updates may still be committed directly.
- Decision: Preserve the official VEGO-AI baseline (`2eeccb1`) as tag `official-vego-ai-baseline` and branch `baseline/official-vego-ai` on `origin`.
- Decision: Adopt `main` as the canonical development branch (it already carries baseline + M1 + M1.2 + M2 at `217150c`). Do NOT merge `master` into `main` with `--allow-unrelated-histories`. Keep `master` + `feature/human-review-queue` as a granular-history archive; PR #1 closed as superseded.
- Reason: A clean, reviewable audit trail is required for thesis reproducibility; M1/M2 had been published directly to `main`, losing per-milestone review.
- Consequence: Future milestones use feature branches + PRs into `main`, approved before merge.
- Status: M1 (Human Review Queue) + M1.2 (review_signature) + M2 (Human Feedback Manager) complete on `main`. M3 (Human Judgment Memory) was implemented and published as commit `5e109e5`.

## 2026-06-12 - Reusable Human Judgment Research Spine

- Decision: Make reusable human judgment in AI-assisted domain model assessment the explicit research spine for VEGO-AI.
- Decision: Use the main research question: "What approaches have been proposed to support human-AI collaboration in AI-assisted domain modeling and model assessment, and how can they inform the design of reusable human judgment mechanisms in systems such as VEGO-AI?"
- Decision: Use the contribution statement: "selectively triggered, structurally captured, and stored as reusable knowledge."
- Reason: The research review identified this framing as the strongest MSc thesis foundation and the clearest bridge to PhD continuation.
- Consequence: Research docs, thesis outline, evaluation plan, roadmap, and claim/evidence tracking should align to M1 selective review, M2 structured feedback, M3 reusable memory, M4A advisory evidence, and M4B controlled reuse.

## 2026-06-12 - M3 Inert Boundary And M4 Controlled Reuse

- Decision: Treat M3 Human Judgment Memory as implemented but inert.
- Decision: Do not wire memory into Agent 4, embeddings, guideline mutation, or the visualizer until a separate controlled experiment is run.
- Reason: The thesis needs a clean distinction between building reusable knowledge and proving that reused knowledge improves AI-assisted variability interpretation.
- Consequence: M4A is advisory-only; M4B/EXP-001 is the next behavior-changing controlled experiment and behavior-improvement claims wait for C4B evidence.

## 2026-06-12 - M4A Advisory Boundary And M4B Design Gate

- Decision: Treat M4A as an advisory-only bridge from Human Judgment Memory to future model assessment.
- Decision: M4A may retrieve relevant human judgments and generate `memory_advice.json`, but it must not change Agent 4 classifications, prompts, guidelines, visualizer behavior, or baseline evaluation outputs.
- Decision: M4B is design-only until separately reviewed; it must preserve original Agent 4 output and produce a comparison rather than replacing the baseline classification.
- Reason: PR #2 showed the safe bridge needed before any behavior-changing memory-informed reclassification.
- Consequence: Future M4B plans must include `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `memory_informed_differs_from_original`, `requires_human_review_after_memory`, `evaluation_leakage_status`, `decision_trace`, `policy_version`, and `human_memory_used`.

## 2026-06-13 - M4A Reproducibility Tags

- Decision: Use lightweight Git tags for the M3 code state, M4A code state, and M4A research-state snapshot.
- Decision: Keep `milestone-m3-human-judgment-memory` at `5e109e5f9f2073d9cdc2325bcea2823d57c77882`, `milestone-m4a-memory-advisory` at `ecd097245c463089a5721d68b17d6b22a1005a43`, and `research-state-m4a` at `28289405fc7cb687665f949bf039355a97967c59`.
- Reason: Thesis and artifact review need stable, reproducible anchors for the code milestone and the surrounding research-story state.
- Consequence: Future artifact manifests should reference these tags instead of relying only on moving branch names.

## 2026-06-14 - M4B-1 Conditional Approval Contract

- Decision: Treat M4B-1 as a deterministic, experimental, parallel-comparison layer, not a baseline Agent 4 behavior change.
- Decision: Use `memory_informed_differs_from_original` and always keep `ai_behavior_changed_in_baseline=false`.
- Decision: Require `policy_version="memory-informed-classifier-v1"`, `decision_trace`, `requires_human_review_after_memory`, and `evaluation_leakage_status` on future M4B-1 outputs.
- Decision: Defer M4B-2, Agent 4 `resolve_with_answers`, LLM/API calls, embeddings, visualizer changes, and baseline output overwrites.
- Decision: Future M4B-1 implementation must use branch `feature/memory-informed-comparison` and PR review; Codex must not commit VEGO-AI milestone implementation paths directly to `main`.
- Reason: The M4B review approved the research direction only if reusable memory remains a controlled comparison mechanism with leakage tracking and reproducible deterministic rules.
- Consequence: Claude can implement only the approved M4B-1 scope after confirming `docs/research/m4b-conditional-approval.md`; improvement claims wait for EXP-001/C4B evidence.
