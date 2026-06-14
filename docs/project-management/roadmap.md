# Roadmap

## Milestones

| ID | Milestone | Status | Exit Criteria |
| --- | --- | --- | --- |
| M0 | Architecture baseline | Done | Folder structure, Git hygiene, memory, GitHub baseline, and docs are in place. |
| M1 | Human Review Queue | Done | Selective intervention creates signed review items with trigger reasons. |
| M2 | Human Feedback Manager | Done | Structured feedback validates, attaches to review items, and preserves status/signatures. |
| M3 | Human Judgment Memory | Done | Reusable resolved judgments are stored with provenance, explainable retrieval, and conflict detection; published as commit `5e109e5`. |
| M4A | Memory Advisory Layer | Done | Advisory report retrieves relevant memory for Agent 4 patterns with `ai_classification_changed=false`; PR #2 squash-merged as `ecd0972`. |
| M4B | Memory-informed parallel comparison experiment | Design contract approved | M4B-1 must write only a parallel `memory_informed_comparison.json`, preserve original Agent 4 output, label leakage, and land implementation through a reviewed branch/PR. |
| M5 | Human-approved guideline refinement | Planned | Guideline changes require explicit human approval and traceable provenance. |
| M6 | MSc thesis evidence and PhD continuation | Planned | Claim/evidence table, C0-C4 results, validity analysis, and continuation roadmap are coherent. |
| OPS-1 | Data and artifact audit | In progress | Data sensitivity, provenance, and publishability recorded without exposing controlled contents. |
| OPS-2 | Reproducibility baseline | In progress | Framework/evaluator commands rerun or validated; generated outputs are linked to experiment records. |
| OPS-3 | Confluence wiki sync | Blocked | Curated wiki pages generated after meaningful prompts; live Confluence updates wait for Atlassian Rovo cloud access. |

## Weekly Review

At least once per week:

- update `experiments/registry.md`,
- update active issues,
- review risks,
- archive or label outputs,
- refresh Confluence outbox or live wiki pages,
- summarize progress in agent memory.
