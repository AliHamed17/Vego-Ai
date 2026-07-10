# Paper A — Evaluation Methodology for Reusable Human Judgment (no-accuracy-claim)

**Working title:** *Evaluating Reusable Human Judgment in AI-Assisted Model Assessment When No
Independent Benchmark Exists: A Bias- and Leakage-Controlled Methodology.*

**Status:** Draft scaffold (2026-06-30). Writable *now* — this paper makes **no accuracy-improvement
claim** and therefore is not blocked by the EXP-005 label gate.

**Contribution (one line):** a reusable, design-science evaluation methodology for human–AI co-reasoning
artifacts in settings where the only on-hand labels are circular (author labels byte-identical to the AI),
combining a "no-clean-benchmark" diagnosis, a bias-controlled blind annotation protocol, per-row leakage
discipline, sealed dev/holdout splitting, and pre-committed evidence gates.

**Why it stands alone:** the methodology is evaluable and defensible independently of any measured effect.
It reports *how to obtain admissible evidence honestly*, not a result. (The empirical paper — Paper B —
follows once labels exist.)

**Candidate venues (to reconcile with `docs/research/publication-plan.md`):** ER (Conceptual Modeling),
CAiSE, SoSyM journal; the human–AI interaction angle could suit a CSCW/CHI venue.

**Evidence boundary:** carries the project guardrails verbatim — no accuracy claim; baseline never modified;
synthetic ≠ real; sealed holdout; every claim maps to data/code/limitations/provenance.

## Folder contents
- `outline.md` — section structure and argument
- `claim-evidence-table.md` — every claim → source → admissibility (mechanism/methodology only)
- `figures.md` — figure list (reuses existing repo + deck assets)
- `submission-checklist.md` — pre-submission gates

Sources: thesis Ch 6 (methodology), Ch 8 (threats), Appendix A; `docs/research/{evaluation-plan,
expert-labeling-protocol,m4b1-policy-refinement-plan}.md`; `reports/generated/` summaries.
