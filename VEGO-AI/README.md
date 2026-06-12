# Experiment Materials for the paper: Not All Differences Matter: Variability Exploration of Domain Models via Agentic AI

## Structure

Six folders:

```
├── analysis/       # Analyzed results by the experts, for Phases B to D
├── eval/           # Evaluation scripts and configuration of the evaluator; Read the Evaluator Readme for execution.
├── eval_output/    # Evaluation results, organized by experimental condition (ucd_ch, ucd_pw, cd_ch, cd_pw)
├── framework/      # Source code for the multi-agent pipeline (orchestrator and agents); Read the Readme for execution
├── inputs/         # Domain descriptions, language bases, and scoring schema (ch, pw)
└── models/         # Case models, organized by experimental condition (CD_Ch, CD_PW, UCD_Ch, UCD_PW)
```

## Human-AI Co-Reasoning Extension

- `docs/human_review_queue.md` documents Milestone 1: selective human-review queue generation.
- `docs/human_feedback_manager.md` documents Milestone 2: validating and attaching structured human feedback to review items.
