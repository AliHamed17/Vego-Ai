# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

**Last Updated:** 2026-07-25 by Codex (unified runtime, security hardening, and final review package)

---

## 1. Quick Status (< 10 lines)
* Historical commits/tags contain the M1-M4B-1 reusable-human-judgment implementation. PR #8 records the thesis evidence release; PR #10 is the active unified-runtime and security-hardening publication route. Live GitHub remains authoritative for review and merge state.
* Two constraints are active: offline H-layer architecture/experiment hardening and the EXP-005 human-label gate for the parked evaluation track.
* The machine-derived July 1 meeting record supports a **framework-first** direction pending participant confirmation. M-02 through M-05 have no recorded outcomes.
* July skills, prompt requirements, and six detailed specifications are **provisional drafts**, not approved interfaces. `allowed-touch-proposal.md` is also unapproved.
* **Research Loop:** Fifteen iterations (001-015) are accepted. Iterations 001-007 are historical/pre-manifest; 008-015 are manifest-backed. Iteration 015 (`HLAYER-UNIFIED-HARDENING-V1`) is the latest reliability-only snapshot, verdict `NEUTRAL`. It introduces legacy/unified/parity infrastructure but selects no empirical or model default. EXP-013-018 conformance remains offline-only and authorizes no live listener.
* **MediVARIA draft added (2026-07-04):** a provisional PhD/future-work proposal exists, but it is not supervisor-endorsed clinical work. MSc evidence remains education-only; there is no patient data or clinical-performance evidence in this repo.
* **Accuracy Verdict:** *Accuracy improvement cannot be evaluated yet* (0 generalization-safe real labels exist). The EXP-005 gate now gates the PARKED evaluation track only - not framework-track doc/spec work.
* **Thesis evidence package (2026-07-25):** a B0-B5 evidence ladder, canonical evidence snapshot, claim/chapter traceability, EXP-019..029 gated protocols, a 91-page review DOCX/PDF, and offline baseline-progress HTML are prepared and manifest-bound. This improves reliability and evaluation rigor; it does not establish an accuracy gain.

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
* **Git orientation:** PR #10 is the active hardening publication route. Run live Git checks for branch, revision, PR state, approval, protection, and cleanliness; durable memory intentionally does not pin volatile values. The visualizer tag `research-state-visualizer-ux-clean` names a historical commit, not current workspace state.
* **Publication records:** PR #6 covers earlier schema/test hardening; PR #8 covers the thesis evidence package; PR #10 covers unified contracts, parity, security, provenance, and final package reconciliation.
* **Tags:** `milestone-m3-human-judgment-memory`, `milestone-m4a-memory-advisory`, `research-state-m4a-clean`, `research-state-results-dashboard`, `research-state-m4b1-deterministic-comparison`.

---

## 3. Active Blockers

| Blocker ID | Severity | Description | Next Step |
|------------|----------|-------------|-----------|
| **ISS-005** | Medium | Live Confluence sync blocked (Atlassian Rovo cloud access `724252a1-a5b7-45a5-b6ec-27a8292197ec` pending). | Use manual sync outbox files. |
| **ISS-006** | Medium | No completed generalization-safe expert labels for EXP-005 (parked evaluation track since 2026-07-04). | Supervisor/experts must label the blind sheet (27 rows; 24 generalization-safe candidates). |
| **ISS-007** | Medium | Evaluation leakage risk if same-pattern rows are claimed as generalization. | Keep same-pattern rows strictly for mechanism validation. |
| **ISS-012/013**| Medium | False-accuracy-narrative risk (synthetic vs real accuracy); weak evidence from one-reviewer. | Require κ & adjudication; quote real label status in reports. |
| **ISS-014** | High | M-01 through M-06 are unrecorded; no architecture/default/live authorization can be inferred. | Record explicit outcomes with Iris and Arnon; silence remains deferred. |

---

## 4. Next Action
1. **Human evidence gate:** approve the blind-label protocol, appoint two independent reviewers plus an adjudicator, and calibrate on the three excluded same-pattern rows.
2. **EXP-020:** collect the 24 generalization-safe labels without exposing the 16/8 development/holdout split to reviewers; supplied labels remain 0 and must never be inferred or prefilled.
3. **Decision gate:** record M-01..M-06. Until then, keep architecture, dosage, H-Verify, authority, and timeout choices provisional.
4. **Offline advancement:** preserve iterations 008-015 atomic contracts and metric semantics. Iteration 15 is reliability-only; do not interpret it as an accuracy or generalization result.
5. **Policy gate:** perform development-only error analysis before proposing one deterministic candidate; open the sealed eight-row holdout only after the policy and hashes are frozen.
6. **Phase 4:** remain blocked until M-05 plus a separate exact-file implementation authorization.

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
* **Tests:** Current unsuppressed rerun on 2026-07-25: 113 passed in `VEGO-AI/tests`; 113 passed plus 7 subtests in `scripts/tests`; 46 passed in `tests/hlayer_offline`; the complete controlled/source/release gate passed.
* **Schemas:** runtime schemas remain unchanged; the evidence package adds document-level schemas for the evidence snapshot, gold labels, policy candidates, and evaluation-run manifests.
* **Latest Run ID:** `20260614-122150` (27 comparisons, 0 differences, 2 review flags, 0 changes to baseline behavior).
</details>

<details>
<summary><b>6.2 Evaluation & Experiment Details (EXP-001...027)</b></summary>

* **EXP-001 (Mechanism):** 27 rows, 3 same-pattern labels, 0 generalization-safe labels.
* **EXP-002 (Generalization candidates):** 24 safe candidate rows identified for expert labeling.
* **EXP-003 (Accuracy evaluation):** Tooling/harness ready. Blind sheets generated under `reports/generated/exp003/`.
* **EXP-004 (Sensitivity):** Synthetic policy screening only (no real evidence).
* **EXP-005 (Real-label gate):** Tooling generates blind reviews, reliability stats, and kappa metrics. Closed until expert labels are added.
* **EXP-019..027 (Preregistered next phase):** reviewer calibration, independent labeling, development-only baseline error analysis, routing/retrieval validity, deterministic policy development, one-time sealed holdout, external education replication, human-effort evaluation, and ablation/robustness. They are planned protocols, not completed evidence.
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
