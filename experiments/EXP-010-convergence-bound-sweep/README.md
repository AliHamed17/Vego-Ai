# EXP-010 - Convergence-Bound Sweep

Status: **Provisional synthetic prototype run complete (2026-07-10); protocol unapproved.** Claim scope: assumption-driven synthetic rule test only.

Question: What escalation/agreement behavior do different S5 round bounds (1/2/3) produce on the seeded set?

Method: Policy sweep over EXP-009's synthetic dialogues.

Run: Executed as part of the research loop suite via `scripts/exp010_convergence_sweep.py`. Outputs (ignored): `reports/generated/exp010/`.

Interpretation notes: Report `resolved`, `escalated`, `timed_out`, `parked`, and `still_conflicted` separately. Escalation is not convergence or approval. The synthetic sweep may inform M-04 discussion but cannot select an optimal or approved round bound.
