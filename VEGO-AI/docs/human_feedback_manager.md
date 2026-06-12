# Human Feedback Manager (Milestone 2)

Milestone 2 **captures, validates, and attaches** structured human feedback to the
Human Review Queue produced in Milestone 1. It produces a *resolved* queue.

> **Scope guard.** This milestone does **not** change any AI decision. It does not
> re-run Agent 4, does not store reusable judgment (Human Judgment Memory), and
> does not modify the visualizer. It only records the expert's judgment and
> attaches it to the corresponding review item. Using that judgment to change AI
> behavior is a later milestone.

## Flow

```
human_review_queue.jsonl  (M1)        human_feedback.jsonl  (expert decisions)
                      \                /
                       load + validate (schema + business rules)
                                |
                   attach by review_id, verify review_signature
                                |
                   human_review_queue_resolved.jsonl
```

## Files

- `schemas/human_feedback.schema.json` — Draft-07 contract for one feedback object.
- `framework/human_feedback_manager.py` — load / validate / attach / write + CLI.
- `inputs/human_feedback.example.jsonl` — three worked examples (approve, valid
  alternative, needs guideline update).
- `schemas/human_review_item.schema.json` — extended so a *resolved* item
  (with `human_feedback`, `feedback_id`, and `status` of `resolved` /
  `signature_mismatch`) still validates.

## Feedback object (schema)

Required: `feedback_id`, `review_id`, `review_signature`, `expert_id`,
`timestamp`, `human_decision`. `human_decision` requires `decision_type` and
`confidence`; `rationale` and `corrected_classification` are optional in the
schema but `rationale` is enforced by the manager (below).

`decision_type` ∈ `approve_ai_decision`, `reject_ai_decision`,
`correct_classification`, `valid_alternative`, `modeling_error`,
`domain_specific`, `pedagogical_issue`, `ambiguous`, `needs_guideline_update`.

Optional: `reusable`, `reuse_scope` (`domain`, `diagram_type`,
`applies_to_future_models`, `limitations`), `guideline_update`
(`action` ∈ `none|add_alternative|edit_description|restrict_scope|reject_guideline|new_guideline`,
`proposed_text`, `requires_second_expert`), `notes`.

```json
{
  "feedback_id": "HF-ucd_ch-P6-001",
  "review_id": "HRQ-ucd_ch-P6",
  "review_signature": "7c0a6700854332a8",
  "expert_id": "expert_02",
  "timestamp": "2026-06-11T12:05:00Z",
  "human_decision": {
    "decision_type": "valid_alternative",
    "corrected_classification": "Substantial Variability",
    "confidence": "High",
    "rationale": "Modeling 'Customer' as an actor who places orders is a legitimate alternative, not an error."
  },
  "reusable": true,
  "reuse_scope": { "domain": "cheers", "diagram_type": "UCD", "applies_to_future_models": true, "limitations": "Only when the customer is clearly the order initiator." }
}
```

## Matching & enforcement rules

1. **Match by `review_id`.** Feedback whose `review_id` is not in the queue is
   reported as **unmatched** (never silently dropped).
2. **Verify `review_signature`.** If the feedback's signature differs from the
   item's, the item is marked `status="signature_mismatch"` with a
   `resolution_note`, and the feedback is **not applied** (drift protection).
3. **Validate decision types** against the controlled `decision_type` enum.
4. **Require rationale for meaningful changes.** Any `decision_type` other than
   `approve_ai_decision` must carry a non-empty `rationale` (manager-enforced).
5. **Keep unresolved and resolved separate.** The original queue is never
   overwritten; a new `human_review_queue_resolved.jsonl` is written. Resolved
   items gain `status="resolved"`, `feedback_id`, and an embedded `human_feedback`.
   Items with no feedback stay `status="pending"`.

## Public API (`human_feedback_manager.py`)

- `load_review_queue(path) -> list[dict]`
- `load_feedback(path) -> list[dict]`
- `validate_feedback(feedback, schema_path=DEFAULT_FEEDBACK_SCHEMA) -> list[str]`
- `attach_feedback(review_items, feedback_items) -> list[dict]`
- `report_feedback(review_items, feedback_items) -> dict`
- `write_resolved_queue(items, path) -> int`

## Reproduce (no API key required)

```bash
# 1) (re)generate the M1 queue if needed
python framework/human_review_queue.py --from-eval-output ../eval_output/ucd_ch

# 2) attach the example feedback
python framework/human_feedback_manager.py \
    --queue    ../human_review_output/ucd_ch/human_review_queue.jsonl \
    --feedback ../inputs/human_feedback.example.jsonl \
    --out      ../human_review_output/ucd_ch/human_review_queue_resolved.jsonl
```

Expected on `ucd_ch`: 3 feedback items attach to P4 / P5 / P6 (all valid, signatures
match) → 3 `resolved`, 1 `pending` (P7), 0 mismatches, 0 unmatched.

Run the tests:

```bash
python tests/test_human_feedback_manager.py     # or: pytest tests/
```

## Statuses

| status | meaning |
|---|---|
| `pending` | no feedback attached |
| `resolved` | feedback validated, signature matched, attached |
| `signature_mismatch` | feedback found by id but signature differed — not applied |
| `dismissed` | reserved (manual triage) |

## What this enables next

`reuse_scope` and `guideline_update` are captured now but **not acted on**. Milestone
3 (Human Judgment Memory) will persist reusable decisions and recall them; a later
milestone will feed confirmed judgments into Agent 4's `resolve_with_answers` and
gate guideline refinement on human approval.
