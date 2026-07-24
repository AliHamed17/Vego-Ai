# H-Layer Program Enhancement Plan - 2026-07-12

Last updated: 2026-07-20 by Codex. Status: ACTIVE - Phase 1 implemented; Iteration 14 is the current accepted coherence snapshot.

Purpose: a comprehensive, prioritized enhancement backlog for the H-layer experiment program, produced from a full verification sweep of the current stack. Scope covers new features, latent-defect fixes, efficiency, and consistency. Everything here is gate-safe by construction; section 2 states the boundary explicitly because it is what keeps the thesis defensible.

## 1. Verified Current State (baseline for this plan)

Verified by the final unsuppressed rerun on 2026-07-20:

| Check | Result |
| --- | --- |
| `pytest VEGO-AI/tests` | 94 passed |
| `pytest scripts/tests` | 53 passed |
| `scripts/run_hlayer_conformance_suite.py` (EXP-013..018) | PASS (`passed: true`) |
| `scripts/validate_hlayer_offline.py` | PASS |
| `scripts/validate_hlayer_program.py` | PASS |
| `scripts/build-hlayer-experiments.ps1` (EXP-006..010, 012, atomic promotion) | PASS, suite `hlayer-20260711T210005Z-0f50c087ac` - NOTE: this out-of-band recon run itself broke latest-iteration coherence (found as F8 below; repaired by iteration 014) |
| `python scripts/check_evidence_consistency.py` | 18/18 PASS |
| `scripts/check_hlayer_protected_paths.py` | PASS (all five protected dirs) |
| Health checks (project/research/dashboard) | PASS |
| Iteration ledger | 14 accepted iterations; 001-007 historical/pre-manifest, 008-014 manifest-backed; EXP-005 safe labels = 0; EXP-012 `NOT YET COMPUTABLE` |

The stack is all-green and hardened (atomic promotion, canonical manifest digests, delegated gate revalidation, protected-path hashing). Enhancements below are therefore additive layers and drift fixes, not rescue work.

## 2. Non-Negotiable Boundary (unchanged, restated)

- No credential handling, no security bypasses, no secrets in the repo - ever. This protects the user's accounts and keeps artifacts publishable.
- No VEGO-AI source-behavior changes; protected paths stay hash-verified; experiment code stays read-only over `VEGO-AI/eval_output` and `VEGO-AI/runs`.
- No accuracy/generalization/clinical claims without real EXP-005 labels (currently 0). Fabricating or relabeling evidence is the one way to actually destroy this project's value; it is excluded by design, not by preference.
- Every enhancement must leave section-1 checks green.

## 3. Findings (verified inline on the actual repo)

| # | Category | Finding | Evidence | Severity |
| --- | --- | --- | --- | --- |
| F1 | consistency | Iteration ledger header says "Current accepted count: twelve iterations (001-012)" while the table contains 13 accepted rows (001-013) and the loop doc names 013 the latest accepted run | `experiment-iteration-ledger.md` line 5 vs. table row 013; `experiment-iteration-loop.md` cadence section | medium |
| F2 | consistency | Loop doc status line still says "HARDENING REQUIRED BEFORE NEXT NUMBERED RUN" although the hardening it demanded was delivered and accepted in iterations 008-009 (atomic promotion, manifests, contract repairs) | `experiment-iteration-loop.md` line 3 vs. ledger rows 008/009 | medium |
| F3 | feature-gap | No unified program overview: the replay suite (EXP-006..010, 012) reports through `hlayer_suite_manifest.json`, the conformance family (EXP-013..018) through `hlayer_conformance`, iterations through 13 `iter_NNN` folders, and the gate/decision state through separate snapshots - nothing joins them into one human-readable + machine-readable status | `reports/generated/` inventory; no overview artifact exists | high (for the user's tracking goal) |
| F4 | feature-gap | No metric trajectory view across iterations: the ledger holds prose verdicts, but nobody can see load/coverage/efficiency evolve 001->013 without opening 13 JSON files by hand | `hlayer_iterations/iter_*/exp007-summary.json` exist but are never aggregated | high |
| F5 | feature-gap | Verification is scattered: proving "everything works" takes 8 separate commands (two pytest suites, conformance, two validators, evidence guard, protected paths, dashboard health) | section 1 was produced manually this way | medium |
| F6 | efficiency | `pytest scripts/tests` takes ~56s, dominated by subprocess-spawning hardening tests; and each replay experiment re-parses the same `VEGO-AI/eval_output` JSONs | timing observed 2026-07-11; exp006/007/008 each load overlapping inputs | low (annoyance, not correctness) |
| F7 | consistency | Stale `.pyc`/`__pycache__` files sit in `scripts/` root (e.g. `hlayer-prototype-scaffold.cpython-313.pyc`) - noise, risk of confusion, should be ignored/cleaned | `scripts/` listing | low |
| F8 | latent-defect (process) | Running `build-hlayer-experiments.ps1` out-of-band desynchronizes the promoted suite from the latest accepted iteration snapshot; `validate_hlayer_program.py` then fails (`latest_iteration: latest iteration does not snapshot current replay suite`). Found LIVE by the new E3 gate during Phase-1 verification - the section-1 "program validator PASS" row predated the recon suite run | verify-hlayer-all first run, 2026-07-12 | medium |

## 4. Enhancement Backlog (prioritized)

| ID | What | Type | Effort | Phase |
| --- | --- | --- | --- | --- |
| E1 | Fix F1 + F2 (ledger count line; loop status line) | fix | S | 1 (done) |
| E2 | `scripts/build_hlayer_program_overview.py`: one read-only generator joining suite manifest + conformance result + program validation + EXP-005 gate + decision snapshot + iteration ledger + metric trajectories (drift-tolerant across iteration schema versions) into `reports/generated/hlayer_program_overview/{program_overview.json, program_overview.md, metric_trajectories.csv}` + pytest coverage | feature | M | 1 (done) |
| E3 | `scripts/verify-hlayer-all.ps1`: one command running the full section-1 gauntlet with a single PASS/FAIL table and nonzero exit on any failure | feature | S | 1 (done) |
| E4 | Doc/registry sync: overview + verify-all referenced from the loop doc, h-layer README row, results dashboard | fix | S | 1 (done) |
| E5 | Clean stray `.pyc` from `scripts/` root and ensure ignore coverage (F7) | fix | S | 1 (done) |
| E6 | Speed: share one parsed-eval_output cache across exp006/007/008 within a suite run (justified-equivalence outputs), and mark the slowest hardening tests for an opt-in `-m slow` lane (F6) | efficiency | M | 2 |
| E7 | Wire the program overview into `build-confluence-wiki.ps1` as a wiki page source, so Confluence tracking gains the unified view | feature | M | 2 |
| E8 | Overview HTML rendering (chart of trajectories) for the supervisor package, reusing the existing visualization agent conventions | feature | M | 2 |
| E9 | EXP-019 candidate: cross-setting reuse-opportunity replay (which validated judgments in one setting would have been retrievable in another - mechanism-only, leakage-labeled) | new experiment | L | 3 (design first, needs registry + protocol) |
| E10 | EXP-020 candidate: observation-completeness audit replaying `evaluator.log` against reconstructed events to bound what the offline replay misses | new experiment | L | 3 |
| E11 | Post-M-03 (Iris decisions): re-parameterize dosage modes per her chosen default and re-run the loop | gated | M | after 2026-07-15 |

Phase 2/3 items are deliberately NOT implemented in this pass: E6 touches hardened runner semantics (needs its own careful equivalence proof), E7/E8 expand the publication surface (better after the July-15 meeting confirms what Iris wants to see), and E9/E10 need registered protocols before code, per the program's own experiment discipline.

## 5. Phase-1 Implementation Record (2026-07-12)

- E1: ledger header corrected to thirteen accepted iterations (001-013); loop status line updated to reflect accepted hardening (008-013) and Phase-1 transition state.
- E2: `build_hlayer_program_overview.py` implemented (read-only; tolerant of missing/renamed metrics across iteration schemas; carries the claim boundary and the EXP-005 gate sentence in both JSON and MD outputs) + `scripts/tests/test_build_hlayer_program_overview.py`.
- E3: `verify-hlayer-all.ps1` implemented; single table, ordered fast-to-slow, `-SkipSlow` flag for the two pytest suites.
- E4: references added (loop doc "Program Views" section, results dashboard row, h-layer plan row in `docs/research/README.md` remains valid).
- E5: stray `.pyc` removed from `scripts/` root (cache dirs remain ignored).
- F8 remediation: Iteration 014 (`reliability_only`, generated 2026-07-20) re-snapshotted the promoted suite; coherence rule recorded in the loop doc ("Program Views And The Standing Gate").
- Verification: a dated 2026-07-20 full `verify-hlayer-all.ps1 -WithOverview` run recorded 9/9 PASS, including 94 + 53 tests and no VEGO-AI diffs. Treat those counts as historical until the July 21 package records its final unsuppressed rerun.

## 6. Tracking

Progress: TASK-047 (this plan + Phase 1). Phase-2/3 items enter the normal iteration/hypothesis flow and the supervisor agenda where they change design decisions. The program overview itself becomes the standing artifact that makes "a lot of experiments and results" visible in one place - regenerate with `python scripts/build_hlayer_program_overview.py` after any suite/iteration run, or as part of `verify-hlayer-all.ps1 -WithOverview`.
