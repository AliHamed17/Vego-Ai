# Memory Advisory Layer (Milestone 4A)

M4A is the **advisory** bridge between stored human judgment (M3) and future
AI-assisted assessment. For each Agent 4 variability pattern, it retrieves
relevant prior human judgments from Human Judgment Memory and presents them as
evidence.

> **Hard boundary.** M4A **never changes an AI classification.** Every advice item
> has `advice_mode="advisory_only"` and `ai_classification_changed=false`. The
> original Agent 4 classification is copied in (for later M4B comparison) but never
> modified. There is **no Agent 4 call, no reclassification, no guideline change,
> no embeddings, and no LLM/API call** here. Changing AI behavior is M4B.

## Flow

```
agentD_deviation_patterns.json  +  agentD_variability_classes.json   (Agent 4)
                              +  human_judgment_memory.jsonl          (M3)
                                          │  (reuses M3 search_memory)
                                          ▼
                                  memory_advice.json   (advisory only)
```

## Files

- `framework/memory_advisor.py` — build advice + CLI.
- `schemas/memory_advice.schema.json` — Draft-07 contract for the report.
- `tests/test_memory_advisor.py` — incl. the "never changes AI" proof.

No existing files are modified.

## How relevance & strength are decided (deterministic, explainable)

Per pattern the advisor builds a query from structured facets — `domain`,
`diagram_type`, `related_guideline_id` (from the pattern or parsed from the
classification evidence), and deterministic `keywords` (quoted phrases + notable
capitalized words from the pattern description) — and calls M3 `search_memory`.

A memory match is **relevant** only if it shares the **guideline** or a
**keyword** (domain+diagram alone is too broad). `advice_strength` over the
relevant matches:

| strength | meaning |
|---|---|
| `none` | no relevant memory |
| `weak` | a relevant match with score ≤ 2 (guideline- or keyword-qualified) |
| `moderate` | a relevant match with score 3 |
| `strong` | a relevant match with score ≥ 4 (domain + diagram + guideline + keyword) |
| `conflicting` | relevant memory disagrees → **needs adjudication** (never auto-resolved) |

`advice_summary` is generated **deterministically** from memory fields (no LLM).
Conflicts are surfaced via `has_conflicting_memory` + `conflict_note` and each
conflicted match keeps its `match_warning`.

## Advice item shape

```json
{
  "advice_id": "MADV-ucd_ch-P5",
  "setting_id": "ucd_ch",
  "pattern_id": "P5",
  "advice_mode": "advisory_only",
  "ai_classification_changed": false,
  "original_ai_classification": { "classification": "Substantial Variability", "confidence": "Medium", "requires_human_review": true, "flag_for_guidelines_update": false },
  "query": { "domain": "cheers", "diagram_type": "UCD", "related_guideline_id": "G12", "keywords": ["Marketing"] },
  "advice_strength": "strong",
  "advice_summary": "Relevant human judgment (needs_guideline_update) classified a similar fragment as Substantial Variability for guideline G12. Advisory only.",
  "memory_matches": [
    { "memory_id": "HJM-ucd_ch-P5", "memory_signature": "…", "match_score": 4,
      "match_reasons": ["same domain","same diagram type","same related guideline G12","keyword match: Marketing"],
      "match_warning": null,
      "human_decision": { "decision_type": "needs_guideline_update", "classification": "Substantial Variability", "rationale": "…" },
      "reuse_scope": { "domain": "cheers", "diagram_type": "UCD" } }
  ],
  "has_conflicting_memory": false,
  "conflict_note": null,
  "recommended_use": "Use as advisory evidence only. Do not change classification until M4B.",
  "provenance": { "source_memory_file": "…/human_judgment_memory.jsonl", "source_agent4_files": { "deviation_patterns": "…", "variability_classes": "…" } }
}
```

The output file wraps these as `{ schema_version, setting_id, advice_mode,
generated_at, provenance, advice: [ … ] }`.

## Reproduce (no API key)

From `VEGO-AI/framework/` (after running M1→M2→M3 so the memory file exists):

```bash
python memory_advisor.py \
    --patterns ../eval_output/ucd_ch/agentD_deviation_patterns.json \
    --classes  ../eval_output/ucd_ch/agentD_variability_classes.json \
    --memory   ../human_review_output/ucd_ch/human_judgment_memory.jsonl \
    --out      ../human_review_output/ucd_ch/memory_advice.json
```

Expected on `ucd_ch` (with the 3 example judgments P4/P5/P6 in memory): advice for
all 8 patterns; **P5 → strong** (cites `HJM-ucd_ch-P5`, guideline G12 + keyword
Marketing), P4/P6 lower strength, the rest `none`. **No** item has
`ai_classification_changed=true`.

Run the tests:

```bash
python tests/test_memory_advisor.py     # or: pytest tests/
```

## Next (blocked)

**M4B — controlled reclassification** will feed this advisory evidence into Agent
4's `resolve_with_answers` and compare original vs memory-informed classification.
That changes AI behavior and is **blocked** until Codex isolation / PR review is
truly under control.
