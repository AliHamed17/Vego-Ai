# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

**Last Updated:** 2026-07-11 by Codex (Phase 0 H-layer feedback generalization boundary)

---

## 1. Quick Status (< 10 lines)
* Historical commits/tags contain the M1-M4B-1 reusable-human-judgment implementation. The current feature-branch worktree is dirty and is not a clean, merged, or finalized package state.
* Two constraints are active: offline H-layer architecture/experiment hardening and the EXP-005 human-label gate for the parked evaluation track.
* The machine-derived July 1 meeting record supports a **framework-first** direction pending participant confirmation. M-02 through M-05 have no recorded outcomes.
* July-15 skills, prompt requirements, and six detailed specifications are **provisional drafts**, not approved interfaces. `allowed-touch-proposal.md` is also unapproved.
* **Research Loop:** Twelve iterations (001-012) are accepted. Iteration 009 (`hlayer-20260710T175523Z-ab5175fd07`) is offline metric/contract repair; iteration 010 (`hlayer-20260710T183658Z-9199809f30`) is a reliability-only rerun; iteration 011 (`hlayer-20260711T102518Z-1ecc5dc68f`) snapshots the updated replay suite with decision snapshot synchronizations and the new offline `feedback_generalizer.py` script; iteration 012 (`hlayer-20260711T123453Z-6cca11a0c8`) snapshots the updated replay suite under the updated supervisor decision register snapshot. All are `NEUTRAL` and select no default. Separate conformance run `HLAYER-CONFORMANCE-1bf053acc473a151d37c` is offline-only.
* **MediVARIA draft added (2026-07-04):** a provisional PhD/future-work proposal exists, but it is not supervisor-endorsed clinical work. MSc evidence remains education-only; there is no patient data or clinical-performance evidence in this repo.
* **Accuracy Verdict:** *Accuracy improvement cannot be evaluated yet* (0 generalization-safe real labels exist). The EXP-005 gate now gates the PARKED evaluation track only - not framework-track doc/spec work.

---

## 2. Architecture State

```text
Original VEGO-AI Agent 1-4 pipeline (baseline)
  -> M1 Human Review Queue (routing triggers)
  -> M2 Human Feedback Manager (structured schema)
  -> M3 Human Judgment Memory (reusable knowledge storage)
  -> M4A Memory Advisory Layer (advisory retrieval, no reclassification)
  -> M4B-1 Deterministic Memory-Informed Comparison (parallel experimental comparison)
```
* **Git Repository:** Initialized; baseline pushed to private `AliHamed17/Vego-Ai`.
* **Current Branch:** `agent/publish-hlayer-and-supervisor-package` at `134ce86`, with a dirty worktree. The visualizer tag `research-state-visualizer-ux-clean` names a historical commit; it does not describe current workspace cleanliness.
* **Active PRs:** PR #6 open (schema/tests hardening, no behavior changes); draft PR #8 tracks `agent/publish-hlayer-and-supervisor-package`.
* **Tags:** `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4a-clean`, `research-state-results-dashboard`, `research-state-m4b1-deterministic-comparison`.

---

## 3. Active Blockers

| Blocker ID | Severity | Description | Next Step |
|------------|----------|-------------|-----------|
| **ISS-005** | Medium | Live Confluence sync blocked (Atlassian Rovo cloud access `724252a1-a5b7-45a5-b6ec-27a8292197ec` pending). | Use manual sync outbox files. |
| **ISS-006** | Medium | No completed generalization-safe expert labels for EXP-005 (parked evaluation track since 2026-07-04). | Supervisor/experts must label the blind sheet (27 rows; 24 generalization-safe candidates). |
| **ISS-007** | Medium | Evaluation leakage risk if same-pattern rows are claimed as generalization. | Keep same-pattern rows strictly for mechanism validation. |
| **ISS-012/013**| Medium | False-accuracy-narrative risk (synthetic vs real accuracy); weak evidence from one-reviewer. | Require κ & adjudication; quote real label status in reports. |
| **ISS-014** | High | M-02 through M-05 are unrecorded; no architecture/default/live authorization can be inferred. | Record explicit July 15 outcomes; silence remains deferred. |

---

## 4. Next Action
1. **Phase 0:** source reconciliation and focused validation are complete; preserve the protected fingerprints and refresh compiled-memory/Confluence derivatives only after the final harness outcome.
2. **Phase 1:** record M-01..M-06. Until then, keep architecture, dosage, H-Verify, authority, and timeout choices provisional.
3. **Offline advancement:** preserve iterations 008-010 atomic contracts and metric semantics. Keep iteration 011, prompt/context integration, and trusted-memory reuse blocked by the decision and evidence gates.
4. **Phase 4:** remain blocked until M-05 plus a separate exact-file implementation authorization.
5. **EXP-005:** obtain protocol approval and schedule two human reviewers; supplied generalization-safe real labels remain 0 and must never be inferred or prefilled.

---

## 5. Working Agreement
* **Prompt Start:** Run `.\scripts\agent-memory-start.ps1` and read `docs/agent-memory/compiled-memory-t1.md`.
* **Prompt End:** Run `.\scripts\agent-memory-finish.ps1` with conciseness when file changes or decisions happen.
* **Guards:** Run `python scripts\check_evidence_consistency.py` before any review/claim update (must PASS).
* **Boundaries:** Keep Agent 4, M4B-2, LLM/API calls, and baseline output overwrites blocked.
* **Git:** Record the actual dirty/clean state; never assume cleanliness. Do not stage unrelated local directories or data zones.

---

## 6. Deep Context (Expandable)

<details>
<summary><b>6.1 Source, Run, and Schema Context</b></summary>

* **Original Package:** Extracted to `VEGO-AI/`.
* **Framework Code:** `VEGO-AI/framework/human_feedback_manager.py`, `memory_advisor.py`, `build_results_dashboard.py`.
* **Tests:** 94 passing pytests is a historical count; rerun before reporting it as current.
* **Schemas:** `human_feedback.schema.json`, `human_review_item.schema.json`, `memory_advice.schema.json`, `results_dashboard_snapshot.schema.json`.
* **Latest Run ID:** `20260614-122150` (27 comparisons, 0 differences, 2 review flags, 0 changes to baseline behavior).
</details>

<details>
<summary><b>6.2 Evaluation & Experiment Details (EXP-001...005)</b></summary>

* **EXP-001 (Mechanism):** 27 rows, 3 same-pattern labels, 0 generalization-safe labels.
* **EXP-002 (Generalization candidates):** 24 safe candidate rows identified for expert labeling.
* **EXP-003 (Accuracy evaluation):** Tooling/harness ready. Blind sheets generated under `reports/generated/exp003/`.
* **EXP-004 (Sensitivity):** Synthetic policy screening only (no real evidence).
* **EXP-005 (Real-label gate):** Tooling generates blind reviews, reliability stats, and kappa metrics. Closed until expert labels are added.
</details>

<details>
<summary><b>6.3 Confluence & Dashboard Infrastructure</b></summary>

* **Target URL:** `https://alih10j.atlassian.net/wiki`
* **Cloud ID:** `724252a1-a5b7-45a5-b6ec-27a8292197ec`
* **Local outbox:** `docs/confluence/outbox/` containing manual sync files.
* **Dashboard Snapshots:** Generated by `scripts/build-dashboard-snapshot.ps1`.
* **E2E Progress Dashboard:** Generated by `scripts/build-e2e-progress-report.ps1`.
</details>

<details>
<summary><b>6.4 PhD Research Trajectory (Direct Track)</b></summary>

* **Topic:** Reusable human judgment for governed human-AI co-reasoning in AI-assisted domain model assessment.
* **Phased Roadmap:** P0 (MSc Gate) -> P1 (Baseline taxonomy) -> P2 (Reuse validity) -> P3 (Policy v1.1 refinement on 16 dev / 8 holdout) -> P4 (Broader medical/class cohorts) -> P5 (Framework synthesis).
* **Iris Action Items:** (1) Define agent skills mapping (A1-A4), (2) Specify prompt/context requirements, (3) Define interface contracts, (4) Separate framework/evaluation phases.
</details>
