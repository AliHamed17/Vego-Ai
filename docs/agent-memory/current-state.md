# Current State

Fast orientation for Codex and Claude. Update this whenever the project state changes.

**Last Updated:** 2026-07-30 by Codex (Iris requirements assurance and presentation-control tranche)

---

## 1. Quick Status (< 10 lines)
* Branch `docs/iris-july29-phd-execution` preserves the ten July 29 evidence artifacts in `3d0beca` and implements the Iris assurance tranche in `28ece6e`; production VEGO-AI behavior is unchanged.
* The bilingual-review-pending July 29 registers control all 19 requirements, 15 actions, and 10 questions; the closure audit has `44/44` locators, with **2 verified complete, 6 awaiting human acceptance, 22 partial, 5 open, and 9 blocked**.
* The recommended architecture is one umbrella RQ plus three subquestions: selective intervention, governed knowledge reuse, and evaluation/transfer. Iris and Arnon approval remains pending for the August 5 checkpoint.
* Plan A is a staged medical extension; Plan B completes the doctorate in software/modeling. Any unproved critical medical prerequisite on August 26 triggers Plan B for the September proposal.
* Proposal `v0.1`, the RQ decision pack, three-study contract, legacy crosswalk, claim register, RACI/RAID register, pre-read, and governance templates now form the first controlled tranche.
* A private Ali-owned nine-folder PhD working Drive and native six-tab literature Sheet exist. They have not been shared or sent; searches and screening are prepared but not yet executed.
* Ali, Iris, and Arnon are confirmed accepted on the recurring Wednesday 09:00-10:00 Asia/Jerusalem calendar event through October 7.
* The metadata-only MIMIC audit observed 25 CSVs totaling 39.65 GiB versus 26 official MIMIC-III v1.4 tables; `NOTEEVENTS` and provenance are unresolved. No patient rows were inspected.
* Medical readiness is **NO-GO at 0/6 entry gates**. EXP-005 remains blocked at 0/24 generalization-safe labels; no medical, accuracy, or generalization gain is claimed.
* IRIS-EXP-01/03 pass; IRIS-EXP-02 awaits live rehearsal and IRIS-EXP-04 awaits the first weekly cycle. No current August/candidacy deck is claimed, and September/October dates remain provisional pending official confirmation.

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
* **Git orientation:** PR #11 is stacked on PR #10 for the experiment benchmark and BigUI. Run live Git checks for branch, revision, PR state, approval, protection, and cleanliness; durable memory intentionally does not pin volatile values.
* **Publication records:** PR #6 covers earlier schema/test hardening; PR #8 covers the thesis evidence package; PR #10 covers unified contracts, parity, security, and provenance; PR #11 covers the results-first experiment observatory and benchmark.
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
| **ISS-022** | High | July 29 Hebrew ASR, English translation, and speaker attribution remain machine-derived. | Complete bilingual and diarization review before direct quotation or final attribution. |
| **ISS-023** | High | Medical readiness is 0/6 mandatory entry gates, with all accountable Plan A roles and approvals unproved. | Name owners and collect use-case, people, authorization, ethics/privacy, environment, and protocol evidence. |
| **ISS-024** | High | The official candidacy process, deadline, reviewer count, committee rules, and presentation requirements are unverified. | Obtain written confirmation from the department or Graduate Studies coordinator. |
| **ISS-025** | High | The shared MIMIC resource has 25 observed CSVs rather than 26 official tables and lacks canonical provenance. | Reconcile the manifest inside an authorized VDI only after all six entry gates pass. |
| **ISS-026** | Medium | The private PhD Drive and literature Sheet are not shared or access-tested. | Ali reviews the exact package, then explicitly authorizes sharing and recipient access checks. |
| **ISS-027** | High | No current July-29/August supervisor PPTX/PDF, presenter notes, rendered QA, or live rehearsal exists; candidacy presentation rules are also unverified. | Confirm logistics, build from the current checklist, add source notes, render/inspect, run a human rehearsal, and archive only after Ali review. |

---

## 4. Next Action
1. **Ali review gate:** inspect the exact August 5 pre-read, RQ pack, proposal, Drive structure, and literature Sheet before any external sharing.
2. **August 5 decision gate:** obtain and record Iris/Arnon decisions on the one-plus-three hierarchy, study map, Plan A/B labels, literature categories, medical owner, Penina dates, and official-process owner.
3. **Presentation gate:** turn the 12-checkpoint outline into the exact meeting artifact only after logistics are confirmed; add source notes, render QA, and complete a dated human rehearsal without copying simulated outcomes into the decision log.
4. **Literature tranche:** execute the recorded searches, deduplicate, screen, verify identities/claims, and prepare the August 12 synthesis without treating tools as evidence.
5. **Transcript gate:** complete bilingual and speaker review; continue using paraphrases only until then.
6. **EXP-005 gate:** appoint two independent reviewers plus an adjudicator and collect the 24 safe labels; do not infer or prefill labels.
7. **Medical gate:** keep all row-level work blocked at 0/6 and collect only documentary proof for the six prerequisites.
8. **August 26 fallback:** run the medical go/no-go review and default the September proposal to Plan B if any critical prerequisite remains unproved.
9. **Administrative gate:** obtain written confirmation of the official candidacy process and rebaseline within one working day if required.

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
* **Tests:** The 2026-07-26 benchmark pass added source, schema, run-history, comparison, report, and browser tests. Final unsuppressed suite counts must be taken from the latest verification record rather than copied from this orientation page.
* **Schemas:** runtime schemas remain unchanged; the evidence package adds document-level schemas for the evidence snapshot, gold labels, policy candidates, and evaluation-run manifests.
* **Latest Run ID:** `20260614-122150` (27 comparisons, 0 differences, 2 review flags, 0 changes to baseline behavior).
</details>

<details>
<summary><b>6.2 Evaluation & Experiment Details (EXP-001...040)</b></summary>

* **EXP-001 (Mechanism):** 27 rows, 3 same-pattern labels, 0 generalization-safe labels.
* **EXP-002 (Generalization candidates):** 24 safe candidate rows identified for expert labeling.
* **EXP-003 (Accuracy evaluation):** Tooling/harness ready. Blind sheets generated under `reports/generated/exp003/`.
* **EXP-004 (Sensitivity):** Synthetic policy screening only (no real evidence).
* **EXP-005 (Real-label gate):** Tooling generates blind reviews, reliability stats, and kappa metrics. Closed until expert labels are added.
* **EXP-019..027 (Preregistered next phase):** reviewer calibration, independent labeling, development-only baseline error analysis, routing/retrieval validity, deterministic policy development, one-time sealed holdout, external education replication, human-effort evaluation, and ablation/robustness. They are planned protocols, not completed evidence.
* **EXP-030..040:** BigUI integrity, gated human-value protocols, runtime parity, topology trade-offs, authority fault injection, operational scale, paper reconciliation, architecture scorecard, valid cross-experiment deltas, and thesis-claim readiness. Only source-backed mechanism/offline results are populated; human and empirical cells remain empty.
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

* **Topic:** Reusable human judgment for auditable, reliable, and transferable human-AI co-reasoning in agentic assessment.
* **Canonical working hierarchy:** one umbrella RQ plus SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer.
* **Study map:** Study 1 intervention architecture; Study 2 judgment lifecycle; Study 3 evaluation and transfer.
* **Plans:** Plan A adds a gated medical transfer pilot; Plan B completes all questions through software/modeling and non-clinical replication.
* **Control interfaces:** master traceability, RQ crosswalk, three-study contract, five-state claim register, six-gate medical scorecard, weekly pre-read, and decision/change log.
* **Decision dates:** August 5 supervisor checkpoint; August 26 medical go/no-go; September/October proposal checkpoints are provisional pending official confirmation.
</details>
