# Experiment Registry

| ID | Title | Status | RQ | Code/Config | Outputs | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-000 | Existing packaged results audit | Planned | RQ1-RQ4 | `VEGO-AI/`, `experiments/EXP-000-existing-packaged-results-audit/` | Metadata registers; controlled outputs local/ignored | Map existing paper results to reproducible records without copying controlled artifacts into Git. |
| EXP-001 | M4B-1 memory-informed parallel comparison experiment | Ready for evaluation | RQ4 | `VEGO-AI/framework/human_judgment_memory.py`, `VEGO-AI/framework/memory_advisor.py`, `VEGO-AI/framework/memory_informed_classifier.py`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/` | `memory_informed_comparison.json` records; controlled outputs local/ignored | Deterministic M4B-1 experiment where M4A advisory evidence informs a separate comparison artifact without changing baseline Agent 4 output; improvement claims still require leakage-aware expert-label evaluation. |
