# Comprehensive Evaluation, Benchmark, and Architecture-Verdict Plan - 2026-07-26

Last updated: 2026-07-26 by Fable (Claude). Status: ACTIVE - Phase 1 implemented the same day (section 6).

Purpose: answer the owner's questions with evidence, in one connected system: Is the architecture good? What does each agent contribute and why? Are we better than the paper baseline, where, and where not? Everything runnable end-to-end, visualized, auto-analyzed, and honestly bounded by the evidence gates (0 independent labels = no accuracy claims; that boundary is what makes every other claim credible).

## 1. What Already Exists (do not duplicate)

Verified on 2026-07-26 after PR #10 merged (all CI green) and the `feature/evaluation-phase` work landed:

| Owner ask | Existing asset |
| --- | --- |
| Per-experiment metrics, sources, denominators, evidence classes, claim boundaries | `scripts/build_experiment_benchmark.py` + `docs/research/bigui/EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md` (41 experiments; 26 with accepted source-backed runs) |
| Progress benchmark + visualization | BigUI (`build_bigui*.py`, run store SQLite, experiment catalog), `VEGO-AI-Experiment-Benchmark-Report.html`, `VEGO-AI-Thesis-Baseline-Progress.html`, program overview + trajectory charts, https://vego-ai.ai.studio hub |
| Run + auto-analyze better/worse | Iteration ledger + `hlayer_iteration_compare.py` deltas; benchmark run history; immutable run store |
| E2E verification | `verify-hlayer-all.ps1` (16 checks), conformance suite (EXP-013..018), program validator, parity checks of the unified runtime |
| Paper-architecture comparability | Benchmark key finding: paper vs repo directly comparable for architecture/versioned counts; paper Phase D is not independent ground truth |
| LLM inside VEGO-AI | `VEGO-AI/framework/llm_client.py` (authorized, hardened: plaintext-key rejection, redaction, logging policy) + unified runtime with parity checks |

## 2. Verified Gaps (this plan's deliverables)

| # | Gap | Deliverable |
| --- | --- | --- |
| G1 | No PER-AGENT contribution/efficiency answer ("is Agent X contributing, why?") - benchmark is per-experiment, not per-component | `scripts/build_agent_contribution_report.py` -> `reports/generated/agent_contribution/` (JSON + MD): every component's purpose, what it delivers, measured signals with sources/N, efficiency, and an evidence-based verdict with reasons and with the condition that would change the verdict |
| G2 | LLM present but not used to EXPLAIN the program (owner: "understand the logic and all what we have done... enhance the experiments") | `scripts/hlayer_llm_analyst.py`: reads the benchmark projection + agent contribution + program overview and produces an analyst narrative and enhancement suggestions. Uses the authorized `llm_client` when `OPENAI_API_KEY` is configured; otherwise a deterministic rule-based narrative. Output is ADVISORY ONLY, never evidence, never touches protected paths, never influences classifications |
| G3 | Iris's July-1 points have implementations scattered across ~40 artifacts; no single point-by-point coverage matrix with real-implementation status | `docs/research/iris-july1-implementation-matrix.md` |
| G4 | No single command that runs verification + benchmark + agent verdicts + visuals + analyst and emits one consolidated verdict | `scripts/run-full-evaluation.ps1` |
| G5 | No consolidated owner-facing report of the whole journey (done/changed/added/removed) | Final report (chat) + this plan's section 6 record |

## 3. Component Verdict Method (G1)

For each component the report answers four questions with sources:

1. PURPOSE - what the component is for (paper section or H-layer spec).
2. DELIVERS - the concrete artifact it produces.
3. MEASURED - signals with value, N, source file + hash date, evidence class:
   - Agent 1 Language Advisor: template agreement (`agentA_metrics.json` per setting; paper-reported F 0.75-1.0).
   - Agent 2 Domain Advisor: guideline precision/recall/F1 (`agentB_metrics.json`; paper alignment 0.70-0.88), guideline churn (EXP-008), low-certainty share (EXP-006 E12).
   - Agent 3 Model Inspector: compliance scoring vs expert review (paper 0.80-0.96; `agentC_all_scores.json`), uncertainty signal volume (EXP-006 E6).
   - Agent 4 Variability Explorer: classification distribution + confidence (`agentD_variability_classes*.json`), review flags; baseline-preservation invariant (0 changes).
   - M1/M2/M3 + M4A/M4B-1: mechanism stats (11 queue items, 4 resolved, 3 memories, 8 advice items, 27 comparisons, 0 changes, 2 escalations).
   - H-layer S1-S7 (offline): EXP-006 coverage (481 events vs 11-item queue = 2.3% old visibility), EXP-007 routing coverage/load, EXP-009 H-Verify fixture recall/specificity, EXP-010 convergence, EXP-013..018 contract/safety rates.
4. VERDICT - one of: CONTRIBUTING (evidence positive), PARTIAL (works, target unmet), NOT-YET-MEASURABLE (needs labels/decisions), plus WHY and WHAT WOULD CHANGE IT. No component gets a verdict without a cited number.

Baseline for comparison = the paper architecture values and the frozen official tag; the report never converts engineering signals into accuracy claims.

## 4. LLM Analyst Boundaries (G2)

- Reads ONLY generated, non-controlled analysis outputs; writes ONLY under `reports/generated/llm_analyst/`.
- Every output carries: "ADVISORY ANALYSIS - generated narrative, not evidence; no accuracy/generalization claim; verify against the cited sources."
- No key in env -> deterministic fallback narrative from the same inputs (the pipeline never breaks or blocks on the LLM).
- Never invoked inside evidence-producing runs; it is a downstream reader.

## 5. Execution Order

1. Plan (this doc) -> 2. G1 script + tests -> 3. G2 analyst -> 4. G3 matrix -> 5. G4 runner -> 6. full E2E run -> 7. adversarial review -> 8. memory/finish -> 9. commit/push/PR (standing authorization) -> 10. owner report.

## 6. Phase-1 Implementation Record

Filled at completion; see `reports/generated/agent_contribution/`, `reports/generated/llm_analyst/`, `docs/research/iris-july1-implementation-matrix.md`, `scripts/run-full-evaluation.ps1`, and the session log entry of 2026-07-26.
