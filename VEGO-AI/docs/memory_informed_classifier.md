# Memory-Informed Classifier (Milestone 4B-1, deterministic)

M4B-1 is the first **experimental, behavior-informing** step: for each Agent 4
variability pattern it produces a **parallel** memory-informed classification next
to the original, using only a transparent **deterministic** policy over Memory
Advice (M4A) + Human Judgment Memory (M3).

> **Hard boundary.** M4B-1 **never modifies the baseline.**
> - Reads `agentD_variability_classes.json`, `memory_advice.json`, `human_judgment_memory.jsonl` (all read-only).
> - Writes a **separate** `memory_informed_comparison.json`.
> - Every record: `mode="experimental"`, `ai_behavior_changed_in_baseline=false`.
> - The original Agent 4 classification is copied **verbatim** and never changed.
> - **No LLM, no API key, no embeddings, no Agent 4 call, no `resolve_with_answers`, no visualizer change.**
> - The memory-informed result differs from the original in **one** case only
>   (strong disagreement) — and even then it is a *parallel proposal* flagged for human review.
> M4B-2 (the optional LLM `resolve_with_answers` mode) is **deferred / not implemented**.

## Deterministic policy table

| Advice case | Memory-informed result | differs? | requires_human_review_after_memory |
|---|---|---|---|
| no memory | keep original | no | no |
| weak | keep original | no | no |
| moderate, agrees with original | keep original (+support) | no | no |
| moderate, disagrees | keep original | no | **yes** |
| strong, agrees | keep original (+stronger support) | no | no |
| **strong, disagrees** | **propose memory-supported alternative (parallel)** | **yes** | **yes** |
| conflicting advice | keep original | no | **yes** |
| ambiguous human decision | keep original | no | **yes** |
| guideline-update memory (no explicit human class) | keep original (+flag guideline review) | no | **yes** |

"Agree/disagree" compares the memory's `human_classification` (from the relevant
matches) against the original Agent 4 `classification`. Conflicting memory (advice
strength `conflicting`, or matches that disagree among themselves) is **never**
auto-resolved — it routes to human review.

## Output record (per pattern)

```json
{
  "comparison_id": "MINF-ucd_ch-P5",
  "setting_id": "ucd_ch", "pattern_id": "P5",
  "mode": "experimental",
  "policy_version": "memory-informed-classifier-v1",
  "ai_behavior_changed_in_baseline": false,
  "original_agent4_classification": { "classification": "Substantial Variability", "confidence": "High", "requires_human_review": false, "flag_for_guidelines_update": true },
  "memory_advice": { "advice_strength": "strong", "advice_summary": "...", "memory_match_ids": ["HJM-ucd_ch-P5"], "has_conflicting_memory": false },
  "memory_informed_classification": { "classification": "Substantial Variability", "confidence": "High", "source": "original_agent4" },
  "memory_informed_differs_from_original": false,
  "classification_changed_meaning": "The parallel memory-informed classification differs from the original Agent 4 classification; the baseline Agent 4 output was NOT modified.",
  "requires_human_review_after_memory": false,
  "human_memory_used": ["HJM-ucd_ch-P5"],
  "evaluation_leakage_status": "same_pattern_memory_used",
  "rule_applied": "strong_agreement_keep_original",
  "decision_trace": ["advice_strength=strong","original_classification=Substantial Variability","human_memory_classification=Substantial Variability","rule=strong_agreement_keep_original","evaluation_leakage_status=same_pattern_memory_used","baseline_output_not_modified"]
}
```

## Evaluation-leakage status (research guard)

`evaluation_leakage_status` ∈ `none | same_pattern_memory_used | same_setting_memory_used |
cross_setting_memory_used | unknown`, computed from the provenance of the memory actually
used vs the pattern being evaluated. This flags when a result reused the *exact* human
judgment created for the same case (a demo, not a generalization test). For clean
evaluation, prefer leave-one-pattern-out / cross-setting / cross-domain / expert-only holdout.

## Public API

`load_json`, `load_memory`, `build_comparison_items(variability_classes, memory_advice,
memory, setting_id) -> list`, `generate_report(items, setting_id, provenance) -> dict`,
`write_report(report, path) -> int`.

## Reproduce (no API key)

From `VEGO-AI/framework/` (after M1→M2→M3→M4A so `memory_advice.json` exists):

```bash
python memory_informed_classifier.py \
    --classes ../eval_output/ucd_ch/agentD_variability_classes.json \
    --advice  ../human_review_output/ucd_ch/memory_advice.json \
    --memory  ../human_review_output/ucd_ch/human_judgment_memory.jsonl \
    --out     ../human_review_output/ucd_ch/memory_informed_comparison.json
```

Run the tests:

```bash
python tests/test_memory_informed_classifier.py     # or: pytest tests/
```

## Deferred (M4B-2)

Optional Agent 4 `resolve_with_answers` (LLM) mode — real AI behavior change; needs an
`OPENAI_API_KEY`, a token/cost budget, and strict experiment mode. **Not implemented.**
