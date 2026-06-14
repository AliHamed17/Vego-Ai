# Experiment Registry

| ID | Title | Status | RQ | Code/Config | Outputs | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-000 | Existing packaged results audit | Planned | RQ1-RQ4 | `VEGO-AI/`, `experiments/EXP-000-existing-packaged-results-audit/` | Metadata registers; controlled outputs local/ignored | Map existing paper results to reproducible records without copying controlled artifacts into Git. |
| EXP-001 | M4B-1 memory-informed parallel comparison experiment | Initial mechanism/readiness run complete | RQ4 | `VEGO-AI/framework/human_judgment_memory.py`, `VEGO-AI/framework/memory_advisor.py`, `VEGO-AI/framework/memory_informed_classifier.py`, `scripts/build-exp001-evaluation.ps1`, `experiments/EXP-001-memory-assisted-agent4-controlled-experiment/` | Ignored `reports/generated/exp001/` tables and summary JSON; controlled source outputs local/ignored | Initial run: 27 comparisons, 3 same-pattern expert labels, 0 generalization-safe expert labels, 0 memory-informed classification changes, 2 human-review-after-memory flags. No accuracy-improvement claim allowed yet. |
