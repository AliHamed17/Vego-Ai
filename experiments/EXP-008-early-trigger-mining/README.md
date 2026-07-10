# EXP-008 - Early-Trigger Mining From Baseline Iteration Churn

Status: iteration-009 Pareto sweep accepted (2026-07-10). Claim scope: offline mechanism/workload trade-off only - no accuracy, generalization, or clinical claims; EXP-005 remains the evaluation gate.

Question: which concrete constructs were unstable across baseline Agent B iterations (run1 -> run2 -> run3 -> best), and did the old post-Agent-4 review queue ever see them? Unstable-but-never-reviewed guidelines are candidate S2 early triggers.

Method: read-only diff of `agentB_run*_guidelines*.json` per setting (added/removed/changed guidelines, by id), cross-referenced against the run review queue's `related_guideline_id`.

Run: `python scripts/exp008_trigger_mining.py` (or the suite wrapper). Outputs (ignored): `reports/generated/exp008/{unstable_guidelines.csv, summary.json, summary.md}`.

Historical result: 167 unstable guidelines across the four settings; 7 had matching queue guideline identifiers and 160 did not. This does not prove human visibility or invisibility beyond the recorded identifier linkage.

Iteration 009 Pareto result: uniform K30 captured 0.75 of the replay-defined churn candidates; K35 captured 0.85. This is a cap/capture trade-off. Neither K value nor an adaptive policy is an approved default.

Interpretation rule: an unstable guideline without a matching queue identifier is a candidate trigger, not evidence that the final guideline is wrong or that no human could have observed it through another channel.
