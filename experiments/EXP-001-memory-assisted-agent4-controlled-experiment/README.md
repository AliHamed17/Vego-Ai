# EXP-001 - M4B-1 Memory-Informed Parallel Comparison Experiment

## Metadata

- Experiment ID: EXP-001
- Title: M4B-1 memory-informed parallel comparison experiment
- Owner: Ali Hamed
- Date started: 2026-06-14
- Date completed: Initial mechanism/readiness run completed 2026-06-14
- Status: Initial evaluation run completed; generalization-safe expert-label evaluation pending
- Related research question: RQ4

## Purpose

Test whether reusable Human Judgment Memory can improve, clarify, or stabilize variability interpretation when M4A advisory evidence is used to produce a deterministic, experimental, parallel comparison result.

M4B-1 does not change Agent 4, does not call Agent 4, and does not overwrite Agent 4 output. It preserves the original classification and writes a separate comparison artifact.

See `docs/research/m4b-conditional-approval.md` for the mandatory implementation contract.

## Non-Goals

- Do not implement M4B-2.
- Do not call Agent 4 `resolve_with_answers`.
- Do not use LLMs, API keys, or embeddings.
- Do not modify Agent 4 prompts.
- Do not modify the visualizer.
- Do not overwrite `agentD_variability_classes.json`.
- Do not modify baseline `eval_output` files.

## Inputs

- Dataset: local generated run `VEGO-AI/runs/20260614-122150/human/`; controlled/ignored.
- Required records: original Agent 4 variability classifications, `memory_advice.json`, `memory_informed_comparison.json`, and Human Judgment Memory records.
- Source files: `VEGO-AI/framework/human_judgment_memory.py`, `VEGO-AI/framework/memory_advisor.py`, and `VEGO-AI/framework/memory_informed_classifier.py`.
- Config files: local configs used for run `20260614-122150`; controlled/ignored.
- Prompt/version notes: None for M4B-1 because the approved mode is deterministic and must not call an LLM.

## Method

- Condition: C4B from `docs/research/evaluation-plan.md`.
- Compare against C0 original VEGO-AI, C1-C3 human-review/memory records, and C4A advisory reports.
- Keep memory use controlled and explicit; do not turn M4B into default behavior without a separate decision.
- Preserve original Agent 4 output and produce a separate `memory_informed_comparison.json` artifact.
- Use `memory_informed_differs_from_original` to describe whether the parallel result differs from the original. Do not use ambiguous wording that could imply baseline Agent 4 changed.

## Deterministic Rule Table

| Advice case | Rule | Memory-informed result |
| --- | --- | --- |
| No memory | Keep original Agent 4 classification. | No change. |
| Weak advice | Keep original Agent 4 classification. | No change. |
| Moderate advice agrees with original | Keep original and add a support note. | No classification change. |
| Moderate advice disagrees with original | Keep original and require human review. | No automatic change. |
| Strong advice agrees with original | Keep original and record stronger support. | No classification change. |
| Strong advice disagrees with original | Propose the human-supported alternative as a parallel result only. | Parallel comparison differs from original. |
| Conflicting advice | Keep original and require human review. | No automatic change. |
| Ambiguous human decision | Keep original and require human review. | No automatic change. |
| Guideline update memory | Keep classification unless an explicit human class exists; flag guideline review. | Parallel guideline note only unless explicit class is present. |

## Required Output Fields

The future output must include:

- `mode = "experimental"`
- `ai_behavior_changed_in_baseline = false`
- `policy_version = "memory-informed-classifier-v1"`
- `original_agent4_classification`
- `memory_advice`
- `memory_informed_classification`
- `memory_informed_differs_from_original`
- `human_memory_used`
- `requires_human_review_after_memory`
- `evaluation_leakage_status`
- `decision_trace`

Allowed `evaluation_leakage_status` values:

- `none`
- `same_pattern_memory_used`
- `same_setting_memory_used`
- `cross_setting_memory_used`
- `unknown`

## Outputs

- Output folder: `reports/generated/exp001/` (ignored).
- Key source file: `memory_informed_comparison.json` in each local setting folder.
- Supporting files:
  - `reports/generated/exp001/exp001_evaluation_dataset.csv`
  - `reports/generated/exp001/exp001_evaluation_table.md`
  - `reports/generated/exp001/exp001_summary.json`
  - `reports/generated/exp001/exp001_summary.md`
- Generator: `scripts/build-exp001-evaluation.ps1`.

## Results

Initial run:

| Measure | Value |
| --- | ---: |
| M4B-1 comparison rows | 27 |
| Settings covered | 4 |
| Expert-labeled rows available from reusable memory | 3 |
| Generalization-safe expert-labeled rows | 0 |
| Memory-informed classifications differing from original | 0 |
| Human-review-after-memory flags | 2 |
| Conflicting memory flags | 0 |

Agreement, mechanism validation only:

| Subset | Expert Labels | Original Matches | Memory-Informed Matches | Original Rate | Memory-Informed Rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Includes same-pattern memory | 3 | 2 | 2 | 0.6667 | 0.6667 |
| Generalization-safe | 0 | 0 | 0 | Not evaluable | Not evaluable |

## Interpretation

The initial run supports mechanism/readiness evaluation: M4B-1 produced a complete non-destructive comparison table, preserved original Agent 4 output, tracked leakage, and flagged two cases for human review after memory.

It does not support an accuracy-improvement claim:

- no memory-informed classification differed from the original Agent 4 classification;
- expert labels are available only for three same-pattern Human Judgment Memory cases;
- there are zero generalization-safe expert-labeled rows.

## Limitations

- Requires audited input/output selection.
- Requires clear handling for conflicting human judgments.
- Same-pattern memory reuse is demonstration evidence, not clean generalization evidence.
- Clean evaluation should use leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout designs.

## Reproducibility

Command:

```powershell
.\scripts\build-exp001-evaluation.ps1
```

The experiment records code commit, local run root, deterministic policy version, supplied memory advice, supplied memory items, leakage status, outputs, and interpretation notes.

## Next Evaluation Workflow

- Collect or define held-out expert labels.
- Keep same-pattern memory in a separate mechanism-validation subset.
- Rerun the evaluation table generator.
- Populate thesis tables/figures from the generated CSV/JSON/Markdown.
- Do not implement M4B-2 until deterministic M4B-1 evidence is understood.
