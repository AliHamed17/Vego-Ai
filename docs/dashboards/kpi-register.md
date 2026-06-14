# KPI Register

Last curated update: 2026-06-14 11:05 +03:00.

## Status Legend

| Status | Meaning |
| --- | --- |
| Green | On track or verified. |
| Yellow | In progress or needs follow-up. |
| Red | At risk and needs active work. |
| Blocked | Waiting for external access or decision. |

## KPI Snapshot

| KPI | Current Value | Target | Status | Evidence | Next Action |
| --- | --- | --- | --- | --- | --- |
| Research spine clarity | Reusable human judgment is the explicit MSc/PhD research spine. | Research docs, roadmap, thesis outline, and claim/evidence table stay aligned. | Green | `docs/research/research-plan.md`, `thesis/outline.md` | Keep M4B design tied to reusable human judgment. |
| Implemented co-reasoning milestone | M1, M2, M3, and M4A are implemented; M4B-1 design contract is conditionally approved. | M4B-1 implementation only through branch/PR; no M4B-2. | Green | Tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`; `docs/research/m4b-conditional-approval.md` | Ask Claude to implement M4B-1 only on `feature/memory-informed-comparison`. |
| Test suite health | 57 tests passing. | All tracked tests pass before publishing. | Green | `python -m pytest VEGO-AI\tests -q` on 2026-06-14 | Continue running before commits and milestone reviews. |
| Compile health | Framework and eval compile successfully. | `compileall` passes for `VEGO-AI/framework` and `VEGO-AI/eval`. | Green | `python -m compileall -q VEGO-AI\framework VEGO-AI\eval` on 2026-06-14 | Keep import/runtime changes tested. |
| Dashboard tracking health | Dashboard sources, runtime snapshot, manual sync pack, Confluence builder wiring, config page slots, and generated outbox are verified. | `dashboard-health` passes after wiki outbox build. | Green | `.\scripts\build-confluence-wiki.ps1` and `.\scripts\dashboard-health.ps1 -RequireOutbox` on 2026-06-14 | Run after every meaningful dashboard/wiki update. |
| AI behavior boundary | M4A is advisory-only and M4B-1 must keep `ai_behavior_changed_in_baseline=false`. | No baseline AI behavior changes before reviewed M4B evidence. | Green | `VEGO-AI/schemas/memory_advice.schema.json`, `docs/research/m4a-post-merge-confirmation.md`, `docs/research/m4b-conditional-approval.md` | Preserve original Agent 4 output in M4B-1 implementation. |
| M4A advisory result | 8 advice items: none 5, strong 2, moderate 1, classification changes 0. | Advisory report can surface relevant memory without changing AI behavior. | Green | M4A review result recorded in `docs/agent-memory/session-log.md` | Include in M1-M4A artifact manifest. |
| Reproducibility anchors | M3, M4A, and research-state tags are pushed to GitHub. | Milestone tags exist and are stable. | Green | `docs/research/m4a-post-merge-confirmation.md` | Reference tags in artifact manifest. |
| Review artifact readiness | M1-M4A ZIP and manifest are requested but not refreshed yet. | `artifacts/vego-ai-M1-M2-M3-M4A-changes.zip` and manifest produced for review. | Yellow | `docs/agent-memory/claude-m4b-handoff-prompt.md` | Ask Claude to refresh artifact and manifest. |
| Experiment registry readiness | EXP-000 and EXP-001 are registered; EXP-001 has an M4B-1 deterministic policy contract. | EXP-000 audit and EXP-001 M4B-1 implementation are actionable. | Yellow | `experiments/registry.md`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md` | Fill EXP-000 evidence entries; implement M4B-1 only through branch/PR. |
| M4B leakage control | M4B-1 requires `evaluation_leakage_status` on every comparison item. | No improvement claim without leakage status and clean evaluation design. | Yellow | `docs/research/m4b-conditional-approval.md`, `docs/research/evaluation-plan.md` | Prefer leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout evaluation. |
| Data/IRB audit | Deferred artifacts remain unaudited. | Controlled artifacts get provenance and publishability decisions before sharing. | Red | `docs/research/artifact-audit.md`, `docs/research/publishability-register.md` | Continue metadata-only audit. |
| Live Confluence sync | Outbox and manual sync pack generated; live write blocked by Atlassian Rovo cloud grant; Chrome fallback unavailable after retry. | Confluence pages update live from outbox. | Blocked | `docs/agent-memory/issues.md` ISS-005, Rovo rechecked 2026-06-14 13:40 +03:00, Chrome checked 2026-06-13 13:50 +03:00 | Grant Atlassian access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` or enable the Codex Chrome Extension route. |

## Tracking Cadence

- Update this register after every milestone merge, experiment run, external review, or Confluence sync change.
- Keep test counts and result metrics tied to the command/date that produced them.
- Do not promote Yellow or Red KPIs to Green without concrete evidence.
