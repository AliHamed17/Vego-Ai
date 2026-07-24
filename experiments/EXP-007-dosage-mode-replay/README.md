# EXP-007 - S2 Dosage-Mode Replay

Status: initial run complete (2026-07-05). Claim scope: design/mechanism evidence (load-coverage trade-off only) - no accuracy, generalization, or clinical claims; EXP-005 remains the accuracy gate.

Question: what expert review load does each S2 H-Triage dosage mode produce, and what share of uncertainty-marked events does each mode surface? (Directly informs Iris's dosage calibration concern and skills-map open question 1.)

Method: replay the EXP-006 event stream through `every_decision`, `threshold` (uncertainty-marked only), `first_n_then_auto` (N=10 cases, then severe-only), and `silent`. Consumes `reports/generated/exp006/events.csv`.

Run: `python scripts/exp007_dosage_replay.py` after EXP-006. Outputs (ignored): `reports/generated/exp007/{summary.json, summary.md}`.

Iteration 1 results (v1, binary signals): every_decision = 289; threshold = 235 (load 0.81, coverage 1.0 by construction - uninformative); first_n_then_auto = 91; silent = 0. Finding: signals too coarse -> hypothesis H1 (severity grading).

Iteration 2 results (v2, severity model 0-3 + weighted metrics): threshold_sev1 load 0.889 / weighted coverage 1.0; **threshold_sev2 load 0.799 / weighted coverage 0.96 / high-severity coverage 1.0 (replay pilot candidate, not a default)**; threshold_sev3 load 0.578 but high-severity coverage 0.723 (guardrail fail); first_n_then_auto load 0.581 (definition changed vs v1: post-N routes sev>=3). The M-B3 target (coverage >= 0.8 at load <= 0.5) is not met. M-03 must select any pilot/cap policy; no result authorizes automatic H3 advice. Full history: `docs/research/h-layer/experiment-iteration-ledger.md`.

Iteration 009 repaired metrics: `threshold_sev2` event load 0.799, transaction load 0.796, weighted coverage 0.981, and high-severity coverage 1.0. The aggregate target of coverage >=0.8 at load <=0.5 remains unmet. Report the Pareto point only; it is not a default or validated operating point.
