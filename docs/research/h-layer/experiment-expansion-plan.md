# H-Layer Experiment Expansion Plan (EXP-006 .. EXP-018)

Last updated: 2026-07-10. Status: **ACTIVE, GATED.** Nine iterations are accepted. Iteration 009 is offline metric/contract repair, `NEUTRAL`; it reports Pareto trade-offs and selects no default. EXP-009/010 remain provisional synthetic prototypes with unapproved protocol, EXP-011 is parked, and EXP-012 N=0 remains not computable. Iterations 010/011 are blocked.

Latest numbered run: `hlayer-20260710T175523Z-ab5175fd07`, normalized `dff1c3b21502c06a99683b1639b4e33543792dcc68afb958026c755b9fe3d7cd`, suite normalized `441b30087bd4e28cc8bd0c0feca979f02cb2514e3b9990685e1cc9f6566403d4`. Separate offline conformance run: `HLAYER-CONFORMANCE-7a426ce3a5336b158606`, normalized `7a426ce3a5336b15860687f1a7f69da241e88b60b0e1b23f95a1d69b21ebba27`, snapshot `681102be14d0aed854dd384fe0f18cc62081d46dfbf64ab6f1a3b47fe92cb0c1`.

Purpose: give the project a continuous stream of real, legitimate, trackable experimental results NOW, without violating any gate. The trick is scope: accuracy and generalization results stay locked behind real expert labels (EXP-005), but the H-layer redesign raises MEASURABLE mechanism questions that the existing baseline outputs can answer today by offline replay - no VEGO-AI behavior changes, read-only over `VEGO-AI/eval_output` and `VEGO-AI/runs`, all outputs generated and git-ignored.

## 1. Design Principles

1. Read-only replay: every new experiment reads existing baseline/run outputs; nothing under `VEGO-AI/` is modified or re-executed.
2. Claim discipline: results are OBSERVABILITY / MECHANISM / DESIGN evidence. No accuracy, no generalization, no clinical claims. Every generated summary carries its claim-scope line.
3. Reproducible: the runner must be hardened to use fresh temporary output, fail fast, validate guards, and promote atomically before another numbered iteration is accepted. Outputs remain generated and ignored.
4. Tracked in the same registry/dashboard machinery as EXP-001..005.
5. Synthetic inputs (EXP-009/010) are labeled synthetic everywhere and never counted as evidence - same rule as EXP-004.

## 2. Experiment Matrix

| ID | Question | Method | Data | Key metrics | Claim scope | Gate | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXP-006 H-Listen event replay | How many E1-E14 records can be reconstructed, at which stages, and what gaps remain? | Offline reconstruction from baseline artifacts plus separate queue-item counts | `VEGO-AI/eval_output/<setting>/`, `VEGO-AI/runs/20260614-122150/human/<setting>/` | Records per E-type; early-stage share; queue-item/event-count ratio (not visibility); instrumentation gaps | Observability/mechanism | None - runnable now | IMPLEMENTED |
| EXP-007 Dosage-mode replay | What review load does each S2 dosage mode produce, and what share of uncertainty-marked events does each mode surface? | Replay the EXP-006 event stream through `every_decision` / `threshold` / `first_n_then_auto` / `silent` policies | EXP-006 events.csv | Routed items per mode per setting; load reduction vs `every_decision`; uncertainty coverage per mode | Design/mechanism (load-coverage trade-off, NOT quality) | None - runnable now | IMPLEMENTED |
| EXP-008 Trigger mining | Which concrete constructs were unstable across baseline iterations (candidate early triggers), and did the old review queue ever see them? | Diff templates/guidelines across run1..run3/best; cross-reference queue items' `related_guideline_id`; link Q&A questions to templates | `VEGO-AI/eval_output/<setting>/agentA_run*`, `agentB_run*`, run queues | Unstable guidelines per setting; revision churn; overlap unstable-vs-reviewed; unstable-but-never-reviewed candidates | Observability/mechanism | None - runnable now | IMPLEMENTED |
| EXP-009 H-Verify seeded-conflict dry run | Under encoded assumptions, do draft S5 rules flag seeded conflicts? | Isolated `SYNTHETIC_NOT_HUMAN` fixtures | Synthetic seeds + source snapshots | TP/FP/FN, per-rule coverage, unresolved cases, zero-contamination check | Assumption-driven synthetic rule test | M-04 protocol approval before interpreting/rerunning | PROVISIONAL PROTOTYPE RUN COMPLETE |
| EXP-010 Convergence-bound sweep | How do candidate round bounds classify synthetic traces as resolved, escalated, timed out, parked, or still conflicted? | Sweep EXP-009 dialogue traces | EXP-009 synthetic traces | Separate terminal-state counts; never combine escalation with resolution | Assumption-driven synthetic rule test | M-04 protocol approval | PROVISIONAL PROTOTYPE RUN COMPLETE |
| EXP-011 V0 vs V1 comparison | Does the H-layer (Version 1) improve error counts / expert alignment over the baseline (Version 0)? | Iris's design: agreed criteria + usability questionnaire, real experts | Real expert labels (EXP-005 gate) + pilot deployment | Error counts, agreement, usability scores | ACCURACY - blocked | PARKED evaluation track; >=20 generalization-safe labels; supervisor go-ahead | PARKED |
| EXP-012 validated baseline interface | Can the validated EXP-005 export feed the canonical evaluator safely? | Explicit eligibility/leakage/provenance filters + canonical cross-check | Validated EXP-005 export | Eligibility counts and evaluator agreement | Measurement infrastructure only | Real-label gate | INTERFACE REPAIRED; N=0 NOT YET COMPUTABLE |

## 3. Tracking Architecture

- Registry: every experiment has a row in `experiments/registry.md` and a folder `experiments/EXP-00X-*/README.md` (protocol, inputs, outputs, claim scope).
- Generated results: per-experiment ignored directories under `reports/generated/expNNN/`, with machine-readable summaries and any experiment-specific details.
- One-command build: `.\scripts\build-hlayer-experiments.ps1`. Numbered-iteration acceptance uses the hardened atomic runner and its manifest/guard gates.
- Dashboard surfacing: headline numbers flow into `docs/dashboards/results-dashboard.md` (curated row per experiment) and the Confluence outbox via the existing wiki build; the combined suite summary is written to `reports/generated/hlayer_experiments_summary.md`.
- Meeting integration: historical headline results inform open questions about event subset, dosage pilot, workload-cap policy, and decomposition; they do not select defaults.

## 4. Evaluation Criteria (how we judge each experiment)

| Experiment | Success looks like | Failure/null result still useful because |
| --- | --- | --- |
| EXP-006 | Stable reconstructed-record counts, explicit capture status/lineage, and a concrete gap list | Without event-level linkage, it cannot identify which reconstructed records correspond to queue items |
| EXP-007 | A clearly labeled load-vs-coverage frontier with stable denominators | If no mode meets the targets, report the Pareto boundary rather than selecting or tuning a default silently |
| EXP-008 | A non-empty list of unstable-but-never-reviewed constructs (early-trigger candidates) | If instability always reached review, the old triggers were sufficient and S2 can start conservative |
| EXP-009 | Balanced synthetic fixtures report TP/FP/FN and unresolved cases with zero contamination | A failed rule is useful design feedback; no result validates real expert-error handling |
| EXP-010 | Terminal outcomes remain separated and persistent conflicts end at adjudication | No synthetic sweep can approve a bound; M-04 decides the protocol |
| EXP-011 | (Parked) V1 vs V0 on agreed criteria | - |
| EXP-012 | Validated EXP-005 export and canonical evaluator agree; gate stops safely at N=0 | Real labels and approval remain external human gates; repair alone is not evaluation evidence |

## 5. Schedule

| When | What |
| --- | --- |
| 2026-07-05 (now) | EXP-006/007/008 implemented, run on all four settings, results generated and tracked; registry + dashboards updated |
| 2026-07-15 | Present historical replay and provisional synthetic results with their limits; record M-02..M-05 outcomes |
| 2026-07-15 .. 2026-08-15 | Preserve accepted iterations 008/009 and prepare iterations 010/011 without running them until their stated gates clear |
| On evaluation unpark | EXP-011 via the EXP-005 real-label gate |

## 6. Architecture-Conformance Series

| ID | Current evidence | Boundary |
| --- | --- | --- |
| EXP-013 | Individual fixture run passes schema, lineage, explicit-gap, and E15-parking checks | Fixture mechanism evidence; no live hook |
| EXP-014 | Three normalized replays have identical hashes and no duplicate review IDs | Fixture determinism only |
| EXP-015 | Fixed-denominator fixture reports bundling, caps, aging, and deferred recovery | No approved cap or workload forecast |
| EXP-016 | Synthetic timeout/denial fixtures preserve baseline and write/apply nothing | No authority granted |
| EXP-017 | Synthetic deterministic-first source trace passes; semantic checks absent | M-04 unrecorded |
| EXP-018 | Disposable-copy proposal diff is reproducible and not applied | No correction authorization |

These runs are separate offline conformance evidence. Current conformance run `HLAYER-CONFORMANCE-7a426ce3a5336b158606` is atomic and offline-only; it is not a numbered iteration and grants no runtime authority.

## 7. Governance

- No file under `VEGO-AI/` is created, modified, or executed; scripts read JSON/JSONL only.
- All outputs are ignored generated artifacts; tracked docs carry only curated summaries.
- Claim boundary carried in every summary: "Mechanism/observability evidence only. No accuracy, generalization, or clinical claims. 0 generalization-safe expert labels exist; EXP-005 remains the accuracy gate."
- EXP-009/010 synthetic rule: seeded feedback lives only under `reports/generated/exp009*/`, is marked `SYNTHETIC_NOT_HUMAN`, and is never merged into real memory/feedback stores (hard isolation, per the PhD idea-log rule).
