# Research Plan

## Topic

Agentic AI support for variability exploration of domain models.

## Core Problem

Domain models can differ in many ways, but not every difference matters. This research investigates how a multi-agent AI pipeline can distinguish meaningful variability from harmless modeling variation or mistakes.

## Candidate Research Questions

| ID | Question | Evidence Needed |
| --- | --- | --- |
| RQ1 | How well can the agentic pipeline identify relevant variability across domain models? | Case-level compliance vectors, expert labels, agreement metrics. |
| RQ2 | Which classes of variability are meaningful, alternative, domain mistakes, or language mistakes? | Agent D classes, expert analysis, examples. |
| RQ3 | How stable are the generated language and domain guidelines across repeated runs? | Multi-run agreement, precision, recall, F1. |
| RQ4 | How do model type and domain affect performance? | Comparison across `ucd_pw`, `cd_pw`, `ucd_ch`, `cd_ch`. |
| RQ5 | How can explanations and visualization support expert review? | Visualizer usage notes, qualitative observations, review feedback. |

## Current Artifacts

- Source package: `VEGO-AI/`
- Paper-related PDF at repository root.
- Analysis files inside `VEGO-AI/analysis/`
- Evaluation outputs inside `VEGO-AI/eval_output/`
- Visualizer package inside `VEGO-AI/vego_visualizer_delivery/`

## Near-Term Milestones

1. Establish version control and architecture baseline.
2. Audit data and outputs for sensitivity and provenance.
3. Re-run or validate existing pipeline results.
4. Create experiment cards for each major result in the paper.
5. Build tests around core parsing, scoring, and evaluator behavior.
6. Prepare thesis chapter outline from validated evidence.

