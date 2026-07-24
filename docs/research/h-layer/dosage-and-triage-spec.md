# S2/S3 Dosage and Triage Specification

Status: **PROVISIONAL WORKING DRAFT.** M-03 and M-05 have not been recorded. The modes, thresholds, caps, timeout duration, and routing rules below are comparison parameters, not approved defaults or runtime behavior.

This document proposes triage policies, severity grading models, event-routing rules, and expert workload limits for H-Layer Skills S2 (Triage) and S3 (Ask). Passive observation covers framework events E1-E14; E15 is evaluation-only and cannot trigger a framework action. Initial active-routing candidates are guideline churn, significant uncertainty, recurring ambiguity, and source conflicts.

---

## 1. Event Severity Model

To support configurable dosage thresholds, incoming event streams (E1-E9) are scored on a severity scale from `0` (lowest, passive log) to `3` (highest, critical intervention opportunity):

| Severity | Definition | Examples | Triage Behavior |
| --- | --- | --- | --- |
| **0** | Pure Informational | Standard E1 template write, regular compliance check pass. | Logged passively; never routed. |
| **1** | Minor Deviation / Low Confidence | Agent C returns marginal classification confidence (< 0.70). | Flagged; routed only in `every_decision` or custom debug modes. |
| **2** | Structural Conflict / Explicit Uncertainty | E6 uncertainty signal, Q&A circle unresolved questions, mismatch warnings. | Promoted in `threshold` and `first_n_then_auto` modes. |
| **3** | Direct Contradiction / Churn | E9 systematic guideline/template ambiguity, E11 verification conflict, unstable guideline revisions. | Always promoted across all active routing modes (except `silent`). |

---

## 2. Dosage Modes and Logic

### Threshold Dosage Mode (Pilot Candidate)
Candidate triage rules for replay and supervisor review:
* **Trigger Condition:** Route an event $e$ if:
  $$\text{Severity}(e) \geq \text{DosageThreshold}$$
  The replay candidate `DosageThreshold = 2` preserved replay-defined high-severity coverage but retained about 80% of the full event-count load. It is not an approved default.
* **Workload policy choice:** Uniform and adaptive per-setting limits remain alternatives for M-03. No queue-size threshold is approved.

### First-N-Then-Auto Mode
Proposed for grading, tutoring, or cohort alignment settings; its name is retained for traceability and does not authorize automatic use of H3 advice:
* **Logic:**
  1. Route all severity $\geq 1$ events for the first $N$ model runs (e.g., $N = 5$).
  2. For runs $> N$, preserve baseline behavior and apply the separately selected routing policy.
  3. H3 retrieval may be displayed as evidence only after separate approval; it is never applied automatically on timeout or missing review.

### Silent Mode
All observations are logged to the run directory without generating user-facing review items or blocking execution. Used for regression testing and benchmarking.

---

## 3. Advanced Workload Mitigations

### H4: Rank-and-Cap Churn Trigger (Comparison Parameter)
To study expert workload in high-revision settings (such as the `cd_pw` and `cd_ch` datasets), replay may compare uniform and setting-specific budgets:
* **Algorithm:**
  1. For each run, calculate the *Guideline Instability Score* (number of revisions divided by total run count).
  2. Sort unstable guidelines in descending order of instability.
  3. Compare candidate limits $K_s$ per setting $s$; the historical values below are replay parameters, not approved limits:
     $$K_{\text{cd\_pw}} = 35, \quad K_{\text{cd\_ch}} = 30, \quad K_{\text{other}} = 20$$
  4. Only route the top-$K_s$ items. Items outside the cap are logged with status `triaged_out_budget_cap`.

### H5: Case-Level Event Bundling
To reduce review overhead, individual element-level uncertainty signals (E6) are bundled at the case/model level:
* **Grouping Rule:** If a model run generates $M$ separate uncertainty observations across different elements, S3 aggregates them into a single transactional review item:
  * **Unified Review Item ID:** `REV-<case_id>-<run_timestamp>`
  * **Unified Evidence Bundle:** Combines the $M$ elements, their compliance outcomes, and the relevant guideline sections.
* **Observed workload effect:** Historical replay showed only a modest reduction in absolute review items in the cited setting (for example, 54 to 53 under `threshold_sev2`, and 67 to 60 under `every_decision`). The earlier unsupported large-reduction claim is withdrawn. These results were not rerun for this reconciliation.

---

## 4. Timeout and Pipeline Progress Safeguards (M-05 Pending)

To prevent pipeline lockups when experts are unavailable:
* **Review timeout:** A future implementation may attach a configurable TTL to a routed review item. No duration is approved.
* **Only permitted phase-one fallback:** Preserve baseline behavior, mark the review `timed_out_parked`, and park it for later human review.
* **Prohibited fallback:** Never apply H3 advice, a correction proposal, or a changed Agent 4 classification automatically.
* The timeout and parking resolution must be recorded in the transaction log. This is a proposed M-05 safety rule and is not live runtime behavior.
