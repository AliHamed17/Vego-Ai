# EXP-012 - Accuracy-Baseline Scaffold (M-D)

Status: **Validated EXP-005 interface repaired; canonical cross-check passed; zero-label gate remains `NOT YET COMPUTABLE`.** Claim scope: measurement infrastructure only. The historical same-pattern pilot is excluded from the main research story.

Question: what IS the current accuracy baseline, and does the measurement pipeline work end-to-end before real labels arrive?

Current method: read the validated EXP-005 full export and validation summary; require explicit generalization-safe eligibility, an allowlisted leakage state, and nonblank provenance; compare calculations with the canonical EXP-003 evaluator.

Run: `python scripts/exp012_accuracy_baseline.py` (included in `.\scripts\build-hlayer-experiments.ps1` and the iteration loop). Outputs (ignored): `reports/generated/exp012/{summary.json, summary.md}`.

Current result (accepted reliability iteration 008, run `hlayer-20260710T171143Z-2a66e71a3f`): validated safe rows = 0; canonical EXP-003 cross-check = PASS; generalization-safe status = `NOT YET COMPUTABLE - no validated safe expert labels`. The historical N=3 same-pattern pilot is excluded.

Activation boundary: the repaired interface does not create evidence. At 0 valid safe labels it stops; 1-19 remain pilot-only; quantitative reporting requires at least 20 plus the existing human/supervisor gates.
