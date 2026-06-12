# EXP-001 - M4B Memory-Informed Agent 4 Controlled Experiment

## Metadata

- Experiment ID: EXP-001
- Title: M4B memory-informed Agent 4 controlled experiment
- Owner: Ali Hamed
- Date started: Not started
- Date completed: Not completed
- Status: Planned
- Related research question: RQ4

## Purpose

Test whether reusable Human Judgment Memory can improve or stabilize Agent 4 variability interpretation when M4A advisory evidence is supplied as explicit context.

## Inputs

- Dataset: TBD after data/IRB and publishability audit.
- Source files: `VEGO-AI/framework/human_judgment_memory.py`, `VEGO-AI/framework/memory_advisor.py`, Agent 4 implementation, selected C0-C4A records.
- Config files: TBD.
- Prompt/version notes: Must record the exact memory advice and memory items supplied to Agent 4.

## Method

- Condition: C4B from `docs/research/evaluation-plan.md`.
- Compare against C0 original VEGO-AI, C1-C3 human-review/memory records, and C4A advisory reports.
- Keep memory use controlled and explicit; do not turn M4B into default behavior without a separate decision.
- Preserve original Agent 4 output and produce a comparison: `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `classification_changed?`, `change_reason`, and `human_memory_used`.

## Outputs

- Output folder: controlled local output folder TBD; keep ignored until publishability is approved.
- Key files: planned C4 run logs, supplied-memory manifest, classification comparison table.
- Figures/tables: TBD.

## Results

Not run.

## Interpretation

Not available. Do not claim behavior improvement until this M4B experiment has evidence.

## Limitations

- Requires audited input/output selection.
- Requires clear handling for conflicting human judgments.
- Results may be sensitive to LLM model/API settings.

## Reproducibility

Pending. The future experiment must record code commit, config, prompt, model/API settings, supplied memory advice, supplied memory items, outputs, and interpretation notes.
