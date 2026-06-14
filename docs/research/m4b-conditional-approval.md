# M4B-1 Conditional Approval And Implementation Contract

## Review Verdict

M4B-1 is conditionally approved as a deterministic, experimental, parallel comparison layer.

The approval applies only after these design clarifications are treated as mandatory requirements. It does not approve M4B-2, Agent 4 prompt changes, LLM/API behavior, embeddings, visualizer changes, or any overwrite of baseline VEGO-AI outputs.

## Research Boundary

M4B-1 tests whether reusable Human Judgment Memory can inform a separate comparison result. It must never mutate the original Agent 4 output.

Required boundary fields:

```json
{
  "mode": "experimental",
  "ai_behavior_changed_in_baseline": false,
  "policy_version": "memory-informed-classifier-v1"
}
```

Use `memory_informed_differs_from_original` instead of the ambiguous field name `classification_changed`.

If legacy wording must appear in a report, it must be defined as: the parallel memory-informed classification differs from the original Agent 4 classification. The baseline Agent 4 output was not modified.

## Deterministic Policy Table

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

## Output Contract

M4B-1 writes only `memory_informed_comparison.json`.

Each comparison item must include:

- `original_agent4_classification`
- `memory_advice`
- `memory_informed_classification`
- `memory_informed_differs_from_original`
- `ai_behavior_changed_in_baseline`
- `human_memory_used`
- `requires_human_review_after_memory`
- `evaluation_leakage_status`
- `decision_trace`
- `policy_version`
- `mode`

`decision_trace` must explain the deterministic rule that fired. Example:

```json
[
  "advice_strength=strong",
  "human_memory_classification=Substantial Variability",
  "original_classification=Occasional Variability",
  "rule=strong_disagreement_propose_memory_supported_alternative",
  "baseline_output_not_modified"
]
```

## Evaluation Leakage Guard

M4B-1 must label whether the memory used creates evaluation leakage.

Allowed `evaluation_leakage_status` values:

- `none`
- `same_pattern_memory_used`
- `same_setting_memory_used`
- `cross_setting_memory_used`
- `unknown`

If a memory item created from the same pattern is used to reclassify that pattern, the result is useful as a demonstration but not as clean generalization evidence.

Clean evaluation should use at least one of:

- leave-one-pattern-out
- cross-setting
- cross-domain
- cross-diagram
- expert-only holdout

## Schema Requirements

The future `VEGO-AI/schemas/memory_informed_comparison.schema.json` must enforce:

- `mode` equals `experimental`
- `ai_behavior_changed_in_baseline` equals `false`
- required original classification, memory advice, memory-informed classification, human memory used, decision trace, policy version, leakage status, and human-review flag

## Acceptance Criteria

M4B-1 is accepted only if all criteria hold:

1. It writes `memory_informed_comparison.json` only.
2. It never overwrites `agentD_variability_classes.json`.
3. It never modifies baseline `eval_output` files.
4. It has no LLM calls.
5. It has no OpenAI/API calls.
6. It has no embeddings.
7. It has no Agent 4 prompt changes.
8. It has no visualizer changes.
9. It preserves `original_agent4_classification` verbatim.
10. It sets `ai_behavior_changed_in_baseline=false`.
11. It includes `policy_version` and `decision_trace`.
12. It marks evaluation leakage when memory comes from the same pattern.
13. It handles conflicting memory by requiring human review.
14. All M1-M4A tests still pass.
15. New M4B-1 tests pass.

## Approved Future Implementation Scope

Claude may implement M4B-1 only after reading this contract and only on a feature branch:

- Branch: `feature/memory-informed-comparison`
- PR target: `main`
- No direct-to-main commit for milestone implementation files

Approved future implementation files:

- `VEGO-AI/framework/memory_informed_classifier.py`
- `VEGO-AI/schemas/memory_informed_comparison.schema.json`
- `VEGO-AI/tests/test_memory_informed_classifier.py`
- `VEGO-AI/docs/memory_informed_classifier.md`

Do not implement or modify:

- M4B-2
- Agent 4 `resolve_with_answers`
- LLM/API calls
- embeddings
- visualizer behavior
- baseline evaluation outputs
- original Agent 4 output files

## Codex Isolation Rule

Codex must not commit directly to `main` for M4B implementation files under:

- `VEGO-AI/framework/`
- `VEGO-AI/schemas/`
- `VEGO-AI/tests/`
- `VEGO-AI/eval/`
- `VEGO-AI/inputs/`
- `VEGO-AI/docs/memory_*`
- `VEGO-AI/docs/*advisor*`

Codex may update root-level research, memory, experiment-planning, dashboard, and Confluence outbox documentation when asked, but must audit staged paths before committing.
