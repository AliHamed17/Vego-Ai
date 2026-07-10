# Paper B — Claim / Evidence Table (pre-wired; all Pending until labels)

| Claim | Evidence Source | Experiment ID | Figure/Table | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Selective review queues a defined share of patterns at stated cost. | M1 queue (11/27 = 40.7%); trigger distribution. | EXP-001 | T-targeting | Available (descriptive) | Coverage of errors needs labels. |
| Escalation flags correspond to actual baseline errors (precision/recall). | M4B-1 `requires_human_review_after_memory` (2/27) vs expert errors. | EXP-003 | F-escalation | **Pending labels** | Computed on safe rows only. |
| Original vs memory-informed accuracy on generalization-safe rows. | Expert gold vs comparison labels. | EXP-003 | T-accuracy | **Gated (≥20 safe)** | v1 delta expected 0 by construction. |
| Inter-rater reliability supports label validity. | Two reviewers, Cohen's κ, adjudication. | EXP-002 | T-reliability | **Pending labels** | Reported with every accuracy figure. |
| Development-row error taxonomy identifies where Agent 4 errs. | `error_analysis.csv` (dev rows). | EXP-003 | T-errors | **Pending labels** | Drives the M4B-1.1 decision. |
| A deterministic refinement (M4B-1.1) is/ isn't justified. | Dev leave-one-pattern-out; sealed holdout (once). | EXP-005 | T-holdout | **Conditional / Blocked** | Only if dev evidence passes §4 rule. |
