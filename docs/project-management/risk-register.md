# Risk Register

| ID | Risk | Impact | Probability | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| RISK-001 | No baseline Git commit yet. | Reverts are weaker. | High | Baseline GitHub history exists on `main`; keep committing safe changes and avoid force pushes. | Resolved |
| RISK-002 | Data sensitivity is not fully audited. | Accidental disclosure. | Medium | Complete data management and IRB checklist. | Open |
| RISK-003 | LLM outputs may drift over time. | Reproducibility risk. | High | Record model/API settings and preserve outputs used in claims. | Open |
| RISK-004 | Existing outputs may be mixed with future reruns. | Analysis confusion. | Medium | Use experiment IDs and output manifests. | Open |
| RISK-005 | Code changes may alter scientific behavior. | Invalid comparisons. | Medium | Add tests and require experiment notes for behavior changes. | Open |
| RISK-006 | Confluence can drift from repository memory. | External wiki becomes misleading. | Medium | Generate curated wiki pages after memory updates at the end of every meaningful prompt. | Open |
| RISK-007 | Confluence target IDs are not configured yet. | Live wiki sync is pending. | Medium | Use `docs/confluence/wiki-sync-config.local.json` when available; otherwise generate ignored outbox pages. | Open |
| RISK-008 | Research story becomes a coding extension rather than a thesis contribution. | Contribution appears weak. | Medium | Keep the main claim centered on reusable human judgment and design-science evaluation. | Open |
| RISK-009 | "Human in the loop" is too broad. | Construct validity suffers. | Medium | Define the human role as selective review, structured decision, reuse scope, and conflict adjudication. | Open |
| RISK-010 | Future AI reuse claims are not grounded in evidence. | Overclaiming. | Medium | Keep M3 inert, keep M4A advisory-only, and reserve behavior-improvement claims for the planned C4B experiment. | Open |
| RISK-011 | Evaluation set is too small for strong claims. | Weak conclusion validity. | Medium | Report limits, use staged C0-C4 comparisons, and expand cases before final claims. | Open |
| RISK-012 | Human judgments may conflict. | Memory may encode disagreement. | Medium | Use M3 conflict detection and require adjudication before treating conflicts as reusable guidance. | Open |
| RISK-013 | M4B reuses memory from the same pattern being evaluated. | M4B can look stronger than it generalizes. | Medium | Require `evaluation_leakage_status` on every comparison item and prefer leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout evaluation. | Open |
| RISK-014 | M4B implementation lands directly on `main`. | AI decision-boundary changes bypass review. | Medium | Enforce branch `feature/memory-informed-comparison`, PR review, and Codex isolation for VEGO-AI milestone implementation files. | Open |
| RISK-015 | EXP-005 has no real expert labels yet. | Accuracy improvement and generalization cannot be evaluated. | High | Fill at least 20 generalization-safe EXP-005 labels, preferably all 24 current safe candidates and then 30-50 across audited runs. | Open |
| RISK-016 | Synthetic or same-pattern results are misreported as accuracy improvement. | Thesis claims become invalid. | Medium | State that EXP-004 is synthetic-only and same-pattern rows are mechanism validation only; require the EXP-005 gate status in all accuracy claims. | Open |
| RISK-017 | Manual CSV labeling workflow creates file locks or unsaved-label ambiguity. | EXP-005 evidence reruns can fail or use stale labels. | Medium | Stop automatic reopen loops; save and close Excel before downstream runs; validate supplied labels before running evidence scripts. | Open |
| RISK-018 | Single-reviewer labeling is treated as definitive. | Construct validity and reliability remain weak. | Medium | Add a second reviewer or supervisor adjudication for disputed rows before strong quantitative claims. | Open |
