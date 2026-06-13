# KPI Register

Last curated update: 2026-06-13 13:18 +03:00.

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
| Implemented co-reasoning milestone | M1, M2, M3, and M4A are implemented; M4B is design-only. | No M4B code until design review. | Green | Tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`; `docs/agent-memory/progress.md` | Ask Claude for M4B design only. |
| Test suite health | 57 tests passing. | All tracked tests pass before publishing. | Green | `python -m pytest VEGO-AI\tests -q` on 2026-06-13 | Continue running before commits and milestone reviews. |
| Compile health | Framework and eval compile successfully. | `compileall` passes for `VEGO-AI/framework` and `VEGO-AI/eval`. | Green | `python -m compileall -q VEGO-AI\framework VEGO-AI\eval` on 2026-06-13 | Keep import/runtime changes tested. |
| AI behavior boundary | M4A is advisory-only with `ai_classification_changed=false`. | No AI classification changes before M4B experiment. | Green | `VEGO-AI/schemas/memory_advice.schema.json`, `docs/research/m4a-post-merge-confirmation.md` | Preserve original Agent 4 output in M4B design. |
| M4A advisory result | 8 advice items: none 5, strong 2, moderate 1, classification changes 0. | Advisory report can surface relevant memory without changing AI behavior. | Green | M4A review result recorded in `docs/agent-memory/session-log.md` | Include in M1-M4A artifact manifest. |
| Reproducibility anchors | M3, M4A, and research-state tags are pushed to GitHub. | Milestone tags exist and are stable. | Green | `docs/research/m4a-post-merge-confirmation.md` | Reference tags in artifact manifest. |
| Review artifact readiness | M1-M4A ZIP and manifest are requested but not refreshed yet. | `artifacts/vego-ai-M1-M2-M3-M4A-changes.zip` and manifest produced for review. | Yellow | `docs/agent-memory/claude-m4b-handoff-prompt.md` | Ask Claude to refresh artifact and manifest. |
| Experiment registry readiness | EXP-000 and EXP-001 are registered; both are planned. | EXP-000 audit and EXP-001 M4B design are actionable. | Yellow | `experiments/registry.md` | Fill EXP-000 evidence entries and draft M4B design. |
| Data/IRB audit | Deferred artifacts remain unaudited. | Controlled artifacts get provenance and publishability decisions before sharing. | Red | `docs/research/artifact-audit.md`, `docs/research/publishability-register.md` | Continue metadata-only audit. |
| Live Confluence sync | Outbox generated; live write blocked by Atlassian Rovo cloud grant. | Confluence pages update live from outbox. | Blocked | `docs/agent-memory/issues.md` ISS-005, rechecked 2026-06-13 13:18 +03:00 | Grant Atlassian access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec`. |

## Tracking Cadence

- Update this register after every milestone merge, experiment run, external review, or Confluence sync change.
- Keep test counts and result metrics tied to the command/date that produced them.
- Do not promote Yellow or Red KPIs to Green without concrete evidence.
