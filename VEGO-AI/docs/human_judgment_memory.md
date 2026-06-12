# Human Judgment Memory (Milestone 3)

Milestone 3 turns one-off human feedback (M2) into **reusable human judgment**. It
ingests a *resolved* Human Review Queue, keeps only the judgments a human marked
reusable, stores them, and retrieves relevant prior judgments by **simple,
explainable** matching.

> **Scope guard.** M3 does **not** change any AI decision. It does not wire into
> Agent 4, does not use embeddings, and does not touch the visualizer. It only
> **builds** and **searches** memory. Consuming memory to change an AI decision is
> a later milestone (M4).

This is the milestone that realizes the core thesis idea: human judgment as a
**structured, reusable knowledge asset**, not a one-time correction.

## Flow

```
human_review_queue_resolved.jsonl  (M2)
        │  ingest_judgments  (resolved + reusable + rationale only)
        ▼
human_judgment_memory.jsonl
        │  search_memory(domain, diagram_type, related_guideline_id, keywords)
        ▼
ranked matches, each with explainable match_reasons
```

## Files

- `schemas/human_judgment.schema.json` — Draft-07 memory-item contract.
- `framework/human_judgment_memory.py` — ingest / store / search / conflicts + CLI.
- `tests/test_human_judgment_memory.py`.

## Ingestion guardrails

A resolved review item becomes a memory item **only if all** hold:

| Check | Skip reason if it fails |
|---|---|
| `status == "resolved"` (not `signature_mismatch`) | `signature_mismatch` / `not_resolved` |
| `human_feedback` present | `no_feedback` |
| `human_feedback.reusable == true` | `skipped_non_reusable` |
| non-empty `human_decision.rationale` | `missing_rationale` |

Skipped items are **reported with reasons**, never raised as errors. `reuse_scope`
is carried through, or safely defaulted (`applies_to_future_models=false`) if absent.

## Memory item

Each item has a human-readable `memory_id` (`HJM-<setting>-<pattern_id>`) and a
deterministic `memory_signature` (sha256/16-hex over the stable `signature_fields`:
`source_review_signature`, `source_feedback_id`, `decision_type`,
`human_classification`, `related_guideline_id`, `reuse_scope`,
`guideline_update.action`). Full **provenance** is preserved:

```json
{
  "memory_id": "HJM-ucd_ch-P5",
  "memory_signature": "….16hex",
  "status": "active",
  "conflict_status": "none",
  "source_review_id": "HRQ-ucd_ch-P5",
  "source_review_signature": "858650979a1195fb",
  "source_feedback_id": "HF-ucd_ch-P5-001",
  "domain": "cheers",
  "diagram_type": "UCD",
  "related_guideline_id": "G12",
  "target_fragment": "Marketing employees' ability to update wine information.",
  "decision_type": "needs_guideline_update",
  "human_classification": "Substantial Variability",
  "rationale": "Marketing dept update is an explicit domain responsibility.",
  "reuse_scope": { "domain": "cheers", "diagram_type": "UCD", "applies_to_future_models": true, "limitations": "" },
  "guideline_update": { "action": "add_alternative", "proposed_text": "…", "requires_second_expert": false },
  "provenance": {
    "source_system": "VEGO-AI", "source_setting": "ucd_ch", "source_pattern_id": "P5",
    "source_commit": "…",
    "source_schema_versions": { "review_item_schema": "1.2.0", "feedback_schema": "1.0.0", "judgment_schema": "1.0.0" }
  }
}
```

## Conflict handling

If two judgments apply to the same `(domain, diagram_type, related_guideline_id,
target_fragment)` but **disagree** on `human_classification`, they are **not**
silently merged: each is flagged `conflict_status="needs_adjudication"` with the
other's id in `conflicting_memory_ids`. Retrieval still returns them, but each
carries `match_warning="conflicting_human_judgments"`. Expert disagreement is
surfaced, not hidden.

## Retrieval (explainable; no embeddings)

`search_memory(memory, *, domain, diagram_type, related_guideline_id, keywords,
include_conflicts=False)` scores each item by transparent facet matches:

- `same domain`, `same diagram type`, `same related guideline Gj`
- `keyword match: <kw>` (substring of `target_fragment` / `rationale`)

Every result includes a `match_reasons` list and a `match_score`. Results are
ranked by score. Conflicted matches carry `match_warning`; with
`include_conflicts=True` the result also lists `conflicting_memory_ids`.

## Public API

`load_resolved_queue`, `ingest_judgments(resolved_items) -> (memory_items, report)`,
`build_memory_item`, `write_memory(memory_items, path) -> int`, `load_memory`,
`search_memory(...)`, `detect_conflicts(memory_items) -> list[dict]`.

## Reproduce (no API key)

```bash
# (chain M1 → M2 → M3 on ucd_ch)
python framework/human_review_queue.py --from-eval-output ../eval_output/ucd_ch
python framework/human_feedback_manager.py \
    --queue    ../human_review_output/ucd_ch/human_review_queue.jsonl \
    --feedback ../inputs/human_feedback.example.jsonl \
    --out      ../human_review_output/ucd_ch/human_review_queue_resolved.jsonl

# ingest reusable judgments
python framework/human_judgment_memory.py \
    --resolved ../human_review_output/ucd_ch/human_review_queue_resolved.jsonl \
    --out      ../human_review_output/ucd_ch/human_judgment_memory.jsonl

# query
python framework/human_judgment_memory.py \
    --memory ../human_review_output/ucd_ch/human_judgment_memory.jsonl \
    --query-domain cheers --query-diagram UCD --query-guideline G12 \
    --keywords "Marketing Department"
```

Expected on `ucd_ch`: the 3 reusable example feedbacks (P4, P5, P6) → **3 memory
items**; the query above returns the **P5** (marketing-department) judgment.

Run the tests:

```bash
python tests/test_human_judgment_memory.py     # or: pytest tests/
```

## What this enables next (M4+)

Memory is built and searchable but **inert**. A later milestone will let Agent 4's
`resolve_with_answers` consult relevant prior judgments, and will gate guideline
refinement on human approval — only then does human judgment change an AI decision.
