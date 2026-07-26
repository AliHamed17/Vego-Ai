# H-Layer Experiment Iteration Loop

Last updated: 2026-07-25. Status: **ACTIVE; LEGACY DEFAULT WITH EXPLICIT UNIFIED/PARITY MODES.** Iterations 008-009 delivered the initial hardening, Iteration 14 restored suite/iteration coherence, and Iteration 15 adds the user-authorized canonical M1–M4B-1 runtime and security boundary. M-01 through M-06 remain unrecorded: no routing, H-Verify, automatic-correction, live-listener, or model default is supervisor-approved. Companion to `docs/research/h-layer/experiment-expansion-plan.md`, `docs/research/h-layer/enhancement-plan-2026-07-12.md`, and the tracked `program-status-snapshot-v1.json`; accepted history lives in the ledger.

Purpose: a repeatable enhancement loop - run the experiment suite, analyze results, derive enhancement hypotheses, implement them, re-run, and compare against the previous iteration with explicit better/worse verdicts. The loop makes improvement MEASURED, not asserted.

## The Honest Boundary (read first)

"Getting better" has two regimes:

1. **Now (no real labels):** the loop optimizes DESIGN metrics - dosage efficiency, trigger capture, observability coverage. These are mechanism measurements, not classification accuracy. Improving them is real progress (it is exactly the calibration work Iris asked for), but no iteration may claim accuracy improvement.
2. **After the EXP-005 gate passes (>=20 generalization-safe real labels):** the SAME ledger gains accuracy columns (expert-alignment deltas via the EXP-003/EXP-005 downstream tooling, later EXP-011 V0-vs-V1). Policy changes that alter classifications remain supervisor-gated regardless of what the metrics say.

Standing guardrails per iteration: Agents 1–4, Agent 4 policy/prompts/classifications, original evaluation logic, and baseline outputs remain immutable. Iteration 15 permits only the reviewed M1–M4B-1, adapter, schema, credential/logging, and test allowlist in `configs/protected-change-authorization-v1.json`; every other protected-path change fails. Synthetic inputs stay labeled and isolated, and the evidence guard must pass.

Iteration 008 established atomic runner reliability. Iteration 009 preserved that contract while repairing observation/metric semantics. Iterations 010-013 are accepted reliability-only snapshots. Iteration 014 is the coherence snapshot. Iteration 15 is the latest reliability-only unified-runtime parity and security snapshot. Legacy remains the default; no iteration selects a routing, verification, correction, accuracy, or model default.

## Loop Protocol (one iteration)

| Step | What | Output |
| --- | --- | --- |
| 1 Run | `.\scripts\run-hlayer-iteration.ps1` executes the registered offline suite in a fresh temporary directory, validates it, and promotes a complete `iter_NNN` only on success | Atomic fresh summaries + run manifest |
| 2 Analyze | Read the generated summaries; list findings (surprises, weak spots, misleading metrics) | Findings list |
| 3 Hypothesize | Turn findings into enhancement hypotheses H-n with an expected metric effect ("severity grading should raise dosage efficiency at load <= 0.5") | Hypotheses with predictions |
| 4 Implement | Change the ANALYSIS side only (event severity model, triage policies, trigger definitions, metrics); never VEGO-AI behavior | Script/spec changes |
| 5 Re-run | Same runner - new iteration folder | New summaries |
| 6 Compare | `python scripts/hlayer_iteration_compare.py` (called by the runner) diffs key metrics vs. the previous iteration | `iteration_report.md` with deltas |
| 7 Verdict | Better / worse / neutral per metric, against the acceptance criteria below; record in the ledger with the decision (keep / revert / revise) | Ledger row |
| 8 Escalate | Findings that change DESIGN choices (dosage default, trigger set, S5 protocol) go to the supervisor loop (next meeting agenda), not silently into the spec | Meeting agenda items |

## Tracked Metrics And Acceptance Criteria

| Metric | Definition | Direction | Current design target |
| --- | --- | --- | --- |
| M-A1 reconstructed event records | EXP-006 total records reconstructed | informational | - |
| M-A2 early-stage share | EXP-006 early events / total | informational | - |
| M-A3 instrumentation gaps | EXP-006 gap list length | lower over time (needs listener hooks - gated) | - |
| M-B1 dosage load | routed items / triageable items, per mode | lower at fixed coverage | - |
| M-B5 bundled case load | unique cases with at least one routed event / total cases | lower at fixed coverage | - |
| M-B2 weighted severity coverage | routed severity mass / total severity mass, per mode | higher at fixed load | - |
| M-B3 dosage efficiency | M-B2 / M-B1 per mode | higher | Find a mode with coverage >= 0.8 of severity mass at load <= 0.5 |
| M-B6 bundled efficiency | M-B2 / M-B5 per mode | higher | Find a mode with coverage >= 0.8 of severity mass at bundled load <= 0.5 |
| M-B4 high-severity coverage | routed sev>=2 events / all sev>=2 events | must stay 1.0 for any accepted default mode | 1.0 |
| M-C1 churn capture | unstable-never-reviewed guidelines surfaced by a churn trigger / 160 baseline | higher | >= 0.8 at M-C2 budget |
| M-C2 churn trigger load | extra routed items added by the churn trigger (per setting) | lower | <= 30 per setting |
| M-D measurement gate | canonical evaluator result over validated EXP-005 downstream rows | informational until gate passes | Interface repaired and canonical cross-check PASS; validated safe rows = 0, so `NOT YET COMPUTABLE`. It never becomes claim evidence from code readiness alone. |

Verdict rule: an iteration is BETTER if at least one target metric improves and no guardrail metric (M-B4, governance checks) degrades; WORSE if a target degrades; otherwise NEUTRAL. Verdicts are recorded per metric, not as one global number.

## M-D Activation (accuracy, once real labels exist)

EXP-012 now consumes the validated EXP-005 full export and validation summary, requires explicit safe-candidate/leakage/provenance fields, and matches the canonical EXP-003 evaluator at the current N=0 gate. Its historical N=3 same-pattern pilot is excluded from the main story. At 0 real safe labels it stops; 1-19 valid safe labels remain pilot-only; quantitative reporting still requires at least 20 plus the existing approvals.

## Historical Hypotheses (iterations 1-2; not current defaults)

| ID | Finding (iter 1) | Hypothesis | Prediction |
| --- | --- | --- | --- |
| H1 | Threshold dosage barely cuts load (0.81) because uncertainty markers are binary and E6 fires on 163/165 cases | Grade events by severity (fragment counts, certainty bands, confidence tiers); add threshold modes at severity cutoffs 1/2/3 | A sev>=2 threshold reaches high coverage of severity mass at materially lower load, moving toward the M-B3 target |
| H2 | 160/167 unstable guidelines never reached review | Add a churn trigger (instability >= t) to triage; sweep t = 1..3 | t=2 captures most churn within the M-C2 budget |
| H3 | Coverage 1.0 "by construction" in iter-1 threshold mode was uninformative | Replace with weighted severity coverage + high-severity coverage | Metrics become discriminative between modes |

## Program Views And The Standing Gate (added 2026-07-12)

- `python scripts/build_hlayer_program_overview.py` regenerates the unified program overview - replay suite + conformance suite + program validation + EXP-005 gate + decision snapshot + all accepted iterations + per-mode metric trajectories - at `reports/generated/hlayer_program_overview/{program_overview.json, program_overview.md, metric_trajectories.csv}` (read-only join; creates no evidence).
- `.\scripts\verify-hlayer-all.ps1` is the one-command verification gate (protected paths, VEGO-AI git cleanliness, evidence consistency, offline + program validators, conformance suite, both pytest suites; `-WithOverview` also rebuilds the overview; `-SkipSlow` skips pytest). Run it before every memory finish and after any suite/iteration run.
- Coherence rule (learned in iteration 014): never run `build-hlayer-experiments.ps1` out-of-band; the replay suite reruns only through `run-hlayer-iteration.ps1`, otherwise the latest-iteration snapshot no longer matches the promoted suite and the program validator fails by design.

## Cadence

Iteration 015 is the latest accepted state and is `NEUTRAL`/`reliability_only` (unified-runtime parity, security, and provenance) under the still-deferred decision register. Its controlled check covers 27 comparison rows with zero classification changes. EXP-012 remains `NOT YET COMPUTABLE` at validated-safe N=0.
