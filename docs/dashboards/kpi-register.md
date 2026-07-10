# KPI Register

Last curated update: 2026-07-10 by Codex. Dated validation rows are historical until rerun; the current worktree is dirty.

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
| Implemented co-reasoning milestone | M1, M2, M3, M4A, and M4B-1 are implemented; M4B-1 remains experimental/parallel-only. | EXP-001/C4B evidence before any improvement claim; no M4B-2. | Green | Tags `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4b1-deterministic-comparison`; `docs/research/m4b-conditional-approval.md` | Review PR #6 schema hardening, then prepare controlled evaluation. |
| Test suite health | Historical 93-test pass; not rerun for the current dirty worktree. | All tracked tests pass before publishing. | Yellow | `python -m pytest VEGO-AI\tests -q` on 2026-06-14 after PR #7 merge | Rerun before reporting a current count or after authorized runtime work. |
| Compile health | Historical compile pass; not rerun for the current dirty worktree. | `compileall` passes for tracked Python implementation areas. | Yellow | Dated 2026-06-14 command in the results dashboard | Rerun after authorized runtime work. |
| Dashboard tracking health | Historical pass; current curated sources changed. | `dashboard-health` passes after wiki outbox build. | Yellow | Last recorded pass 2026-06-23 | Refresh generated dashboard/wiki files only after announcing their writes, then rerun health. |
| AI behavior boundary | M4A is advisory-only and M4B-1 must keep `ai_behavior_changed_in_baseline=false`. | No baseline AI behavior changes before reviewed M4B evidence. | Green | `VEGO-AI/schemas/memory_advice.schema.json`, `docs/research/m4a-post-merge-confirmation.md`, `docs/research/m4b-conditional-approval.md` | Preserve original Agent 4 output in M4B-1 implementation. |
| M4A advisory result | 8 advice items: none 5, strong 2, moderate 1, classification changes 0. | Advisory report can surface relevant memory without changing AI behavior. | Green | M4A review result recorded in `docs/agent-memory/session-log.md` | Include in M1-M4A artifact manifest. |
| Reproducibility anchors | M3, M4A, and research-state tags are pushed to GitHub. | Milestone tags exist and are stable. | Green | `docs/research/m4a-post-merge-confirmation.md` | Reference tags in artifact manifest. |
| Visualizer UX correctness | Model/result pairing is explicit and no stale model is silently treated as valid. | Mismatch/no-match/match states stay visible and research panels stay read-only. | Green | PR #7, real-display GUI validation, tag `research-state-visualizer-ux-clean` | Preserve this boundary in future visualizer work. |
| Review artifact readiness | M1-M4A + dashboard + M4B-1 ZIP and manifest are published in the GitHub release for `research-state-m4b1-deterministic-comparison`. | Artifact bundle is available for external technical review. | Green | GitHub release assets `vego-ai-M1-M4A-dashboard-M4B1-changes.zip` and `M1-M4A-dashboard-M4B1-manifest.md` | Download/review externally if needed; do not treat artifact release as empirical proof. |
| Experiment registry readiness | EXP-000..018 registered; nine H-layer iterations accepted; iteration 009 is metric/contract repair, NEUTRAL. | Every accepted run has atomic outputs, manifest, guard pass, and ledger verdict. | Green | Registry, ledger, run `hlayer-20260710T175523Z-ab5175fd07` | Preserve Pareto-only reporting; iterations 010/011 remain blocked. |
| H-layer decision authority | M-02..M-05 outcomes are not recorded. | Every selected default and live authorization traces to an explicit decision outcome. | Blocked | July 15 supervisor decision register | Keep all architecture, dosage, H-Verify, authority, and timeout details provisional. |
| Passive shadow-listener gate | Allowed-touch proposal/template exist; no implementation approval. | M-05 plus separate exact-five-file authorization before protected paths change. | Blocked | `docs/research/h-layer/allowed-touch-proposal.md` | Remain offline-only and preserve protected fingerprints. |
| Evaluation report readiness | Initial EXP-001 mechanism/readiness run is recorded; empirical generalization evidence is incomplete. | Thesis evaluation tables and figures include held-out expert-label results. | Yellow | `docs/research/evaluation-report.md`, ignored `reports/generated/exp001/` | Collect expert labels and rerun EXP-001. |
| Expert-label readiness | EXP-002 labeling package generated: 27 rows, 24 generalization-safe candidates, 3 existing same-pattern labels. | At least 20 labeled patterns, preferably all 27 current rows before more feature work. | Yellow | `scripts/build-exp002-labeling-package.ps1`, `docs/research/evaluation-report.md`, ignored `reports/generated/exp002/` | Human/supervisor should fill labels and rationale, then rerun evaluation. |
| EXP-005 evidence gate | Current generated verdict is blocked: 27 rows, 24 safe candidates, 0 supplied labels, 0 valid labels, 0 safe labels. | 20+ generalization-safe valid labels, with reviewer-2 or adjudication for disputed rows. | Red | `reports/generated/exp005_label_review/evidence_verdict.md` (ignored), `docs/research/strategic-review-and-hardening-plan.md` | Fill blind labels, use adjudication sheet, rerun EXP-005 downstream. |
| EXP-005 synthetic trial | Synthetic pipeline trial completed: 27 synthetic labels, 24 synthetic safe rows, current M4B-1 accuracy delta 0.00 pp. | Treat as pipeline/policy-risk evidence only, not real accuracy evidence. | Yellow | `artifacts/SYNTHETIC_EXP005_TRIAL_REPORT.md` (ignored), `docs/research/m4b1-synthetic-policy-candidate-review.md` | Use only to prioritize real-label review and possible future M4B-1.1 design discussion. |
| Reviewer reliability | Adjudication sheet and reliability summary are generated; no reviewer-2 or adjudicated labels exist yet. | Reviewer-2 agreement or supervisor adjudication exists before strong quantitative claims. | Yellow | `reports/generated/exp005_label_review/exp005_adjudication_sheet.csv` (ignored), `docs/research/expert-labeling-protocol.md` | Add second reviewer/supervisor adjudication after first-pass labels. |
| Evidence reproducibility manifest | EXP-005 now generates ignored verdict and manifest files with commit, label counts, protected diff, and validation commands. | Every evidence rerun has a manifest and protected behavior paths unchanged. | Green | `reports/generated/exp005_label_review/reproducibility_manifest.json` (ignored) | Review manifest before tagging or reporting evidence. |
| M4B leakage control | Initial EXP-001 run has 19 no-memory rows, 5 cross-setting memory rows, and 3 same-pattern expert-labeled rows; generalization-safe expert-labeled rows = 0. | No improvement claim without leakage status and clean evaluation design. | Yellow | `docs/research/evaluation-report.md`, `reports/generated/exp001/exp001_summary.json` (ignored) | Prefer leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout evaluation. |
| Data/IRB audit | Deferred artifacts remain unaudited. | Controlled artifacts get provenance and publishability decisions before sharing. | Red | `docs/research/artifact-audit.md`, `docs/research/publishability-register.md` | Continue metadata-only audit. |
| Live Confluence sync | Outbox and manual sync pack generated; live write blocked by Atlassian Rovo cloud grant; Chrome fallback unavailable after retry. | Confluence pages update live from outbox. | Blocked | `docs/agent-memory/issues.md` ISS-005, Rovo rechecked 2026-06-14 14:50 +03:00, Chrome checked 2026-06-13 13:50 +03:00 | Grant Atlassian access to cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` or enable the Codex Chrome Extension route. |

## Tracking Cadence

- Update this register after every milestone merge, experiment run, external review, or Confluence sync change.
- Keep test counts and result metrics tied to the command/date that produced them.
- Do not promote Yellow or Red KPIs to Green without concrete evidence.
