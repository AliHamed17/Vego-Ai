# 2026-07-15 Supervisor Meeting Preparation and Rehearsal Plan

Status: **Active meeting preparation guide for Ali. Scopes offline-only prototype and governance review.**

This document outlines the preparation steps, rehearsal instructions, and data sensitivity briefing for the July 15 supervisor meeting with Iris and Arnon.

---

## 1. Meeting Agenda and Decision Checklist

The core objective is to obtain formal outcomes for decisions **M-01** through **M-05** and strategic direction for **M-06**.

### M-01: Confirming the July 1 Record
* **Goal:** Verify timestamped paraphrases (D1-D12) row-by-row without changing the raw transcript ASR.
* **Talking Point:** Remind the supervisors that all paraphrases represent unconfirmed machine-derived transcripts until they explicitly sign off.

### M-02: H-Layer Decomposition
* **Goal:** Approve **Option B** (Observer = H1/S1-S3; Integrator = H2+H3/S4-S7).
* **Talking Point:** Emphasize that H1, H2, and H3 remain distinct functional skill groupings rather than disappearing behind an implementation boundary.

### M-03: Observation, Routing, and Dosage
* **Goal:** Approve passive observation of events E1-E14, limited active-routing triggers, and the `threshold_sev2` pilot with adaptive per-setting workload caps.
* **Talking Point:** Show that uniform caps (e.g. K30/K35) yield different workloads across settings and that adaptive limits are safer.

### M-04: H-Verify Sources and Convergence Bounds
* **Goal:** Confirm checking all four source families, deterministic-before-semantic validation ordering, and a hard limit of two question rounds before human adjudication.
* **Talking Point:** Emphasize that this protocol avoids sycophancy and infinite loops.

### M-05: Human Authority and Allowed-Touch List
* **Goal:** Confirm that every correction needs explicit human approval, timeouts preserve the baseline (parking the item), and live hooks require an approved allowed-touch list.
* **Talking Point:** Establish that no automated model adjustments can bypass human verification.

### M-06: Thesis and PhD Roadmap
* **Goal:** Finalize MSc thesis boundaries (education-domain only) and position clinical guideline adherence (MediVARIA) as PhD roadmap proposals.

---

## 2. Rehearsal and Replay Verification Runbook

Before the meeting, Ali must run the interactive CLI demo and verify the safety boundaries:

```powershell
# Step 1: Run dry-run checks for the interactive scaffold
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run

# Step 2: Test conflict handling and deterministic verification
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --test-conflict

# Step 3: Run the interactive CLI review shell demo
python scripts/hlayer_prototype/hlayer-prototype-scaffold.py --interactive
```

### Dry Run Checks:
1. Confirm that overrides with `needs_adjudication: true` are routed **only** to the isolated `adjudication_candidates.json` file.
2. Verify that ordinary feedback memory logs remain unpolluted.
3. Confirm that all local validators (`validate_hlayer_program.py` and `validate_hlayer_offline.py`) pass.

---

## 3. Data Sensitivity and IRB Briefing

Reassure the supervisors that the project follows strict ethical and privacy guidelines:

* **Protocol Identifier:** `IRB2-Iris` (enforces strict research-only bounds).
* **Data Anonymization:** No student names, email addresses, or database identifiers are stored in Git. All student models are identified only by random candidate hashes.
* **Controlled Access:** Raw student diagrams and expert worksheets are git-ignored. Only aggregated statistics, synthesized patterns, and theoretical findings are publishable.
* **Checklist Completed:** The `ethics-irb.md` and `artifact-audit.md` passes have been completed and verified.

---

## 4. Vector 1 Generalization Proof (`feedback_generalizer.py`)

Be prepared to explain how the feedback generalization boundary is protected:

* **Companion Manifest Verification:** The generalizer enforces a `trusted-feedback-export-validator-v1` manifest check.
* **No Unverified Feedbacks:** Synthetic, demo, timeout, and unadjudicated records are automatically blocked.
* **Provisional-Only Output:** Without a trusted companion manifest, the script returns a safe `BLOCKED_NO_VERIFIED_FEEDBACK` status, protecting the runtime prompt from unverified input.
