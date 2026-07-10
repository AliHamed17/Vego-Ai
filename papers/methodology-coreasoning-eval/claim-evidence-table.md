# Paper A — Claim / Evidence Table

> All claims are **methodology or mechanism** claims. **No accuracy-improvement claim appears.**

| Claim | Evidence Source | Experiment ID | Figure/Table | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Human judgment can be captured as structured, provenance-tracked, reusable records. | Ch 5; M1–M3 schemas (Appendix A.2). | EXP-001 | Schema chain | Implemented | Mechanism only. |
| Reusable judgment can be retrieved as advisory evidence without altering AI output. | M4A; `ai_classification_changed=false` (const). | EXP-001 | Advice-strength dist. | Implemented | Non-destruction machine-verified. |
| A non-destructive deterministic parallel comparison is feasible. | M4B-1; `memory-informed-classifier-v1`. | EXP-001 | Policy outcome dist. | Implemented | 0/27 changed (design + data). |
| A repository may lack an independent benchmark; author labels can be byte-identical to AI output. | `evaluation_summary.json → benchmark_status` (0 field diffs). | EXP-006 audit | — | Verified | Reframes the evaluation; circular labels excluded. |
| Same-pattern reuse must be excluded from generalization metrics via per-row tags. | Ch 6.5; leakage distribution (none 19 / cross-setting 5 / same-pattern 3). | EXP-001 | Leakage dist. | Implemented | 24 safe candidates; 3 same-pattern excluded. |
| A bias-controlled blind annotation protocol yields admissible ground truth. | Ch 6.6; Appendix A.3 blind sheet; reviewer/κ/adjudication. | EXP-002 | Annotation sequence | Designed/Ready | Awaiting supervisor approval + reviewers. |
| Pre-committed evidence gates bound permissible claims by label count. | Ch 6.8; outline gates (0 / 1–19 / ≥20). | EXP-003/005 | Gate ladder | Implemented | Enforced by guard + harness. |
| Sealed dev/holdout (16/8) prevents tuning-on-test for any policy refinement. | `m4b1-policy-refinement-plan.md` §0. | EXP-005 | — | Designed | Holdout evaluated once, after freeze. |
| The methodology transfers to other co-reasoning artifacts lacking clean benchmarks. | Discussion; design-science framing (Gregor & Hevner 2013). | N/A | — | Argued | Paper A thesis; not an effect claim. |
