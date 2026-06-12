# Human Review Queue (Milestone 1)

The Human Review Queue is the first step of the Human–AI Co-Reasoning extension of
VEGO-AI. It turns VEGO-AI from *AI-only* assessment into *AI + selective human
review*: when Agent 4 (Variability Explorer) produces a variability classification
that warrants human judgment, the system records a **structured review item**
instead of silently continuing.

This milestone is **observe-only**: it does not change any AI behavior, does not
ask anything of a human yet, and does not modify guidelines. It only detects,
structures, and persists the cases where a human should weigh in.

## Where it sits in the pipeline

```
Agent 4 (skill 4-1 identify_deviation_patterns) ─┐
Agent 4 (skill 4-2 classify_variability) ────────┴─▶ Selective Intervention Policy ─▶ Human Review Queue (JSONL)
```

- `framework/selective_intervention_policy.py` — decides *whether* a single Agent 4
  classification needs human review (`should_request_human_review`).
- `framework/human_review_queue.py` — joins each flagged classification with its
  deviation pattern and writes schema-valid items (`build_review_items`,
  `write_queue`), plus a no-API-key CLI.
- `schemas/human_review_item.schema.json` — the contract for each item.

Each review item corresponds to one recurring **variability pattern** (`P1`, `P2`,
…) across many models — **not** to a single case model, because Agent 4 reasons at
the population level.

## Triggers (Selective Intervention Policy)

A review item is created when **any** trigger fires:

| Trigger code | Condition | Why a human is needed |
|---|---|---|
| `agent_requested_human_review` | `requires_human_review == true` | Agent 4 explicitly deferred. |
| `undetermined_classification` | `classification == "Undetermined"` | The AI could not decide. |
| `low_confidence` | `confidence == "Low"` | Unreliable verdict. |
| `medium_confidence` | `confidence == "Medium"` (broad policy only) | Borderline verdict. |
| `guideline_update_proposed` | `flag_for_guidelines_update == true` | The human owns the rubric. |

### Strict vs. broad policy

- **Broad** (`include_medium=True`, default): includes Medium-confidence cases.
- **Strict** (`--no-include-medium`): only Low / Undetermined / guideline-update /
  explicit-human-review cases.

Reporting both is part of the planned evaluation ("how much human effort under
different intervention policies?"). On the committed `eval_output/`:

| Setting | Broad | Strict |
|---|---|---|
| ucd_ch | 4 | 2 |
| cd_ch | 2 | 2 |
| ucd_pw | 5 | 5 |
| cd_pw | 0 | 0 |
| **total** | **11** | **9** |

(cd_ch is 2 under both policies because its Medium-confidence pattern also carries
`guideline_update_proposed`, which survives the strict policy.)

> Note: in the committed data `requires_human_review` is always `false` and there
> are no `Undetermined` patterns (Agent 4's `resolve_with_answers` was never run),
> so confidence and guideline-update triggers are what populate the queue.

## Stable identity (review_id vs review_signature)

`review_id` (`HRQ-<setting>-<pattern_id>`) is human-readable but depends on Agent
4's pattern ordering — if Agent 4 is re-run and emits patterns in a different
order, `P4` could later describe a different pattern. Because Milestone 2 attaches
human feedback by id, each item also carries a **`review_signature`**: an
order-independent sha256 prefix over the stable `signature_fields`
(`source_setting`, `pattern_description`, `related_guideline_id`, `affected_cases`
[sorted + de-duplicated], `classification`). Feedback joins can match on
`review_id` for convenience and verify `review_signature` to detect drift.
`source_pattern_id` records the originating Agent 4 `pattern_id`.

## Output item (schema v1.2.0)

```json
{
  "review_id": "HRQ-ucd_ch-P4",
  "review_signature": "a83f91c2d5e07b14",
  "signature_fields": ["source_setting", "pattern_description", "related_guideline_id", "affected_cases", "classification"],
  "schema_version": "1.2.0",
  "source_pattern_id": "P4",
  "created_at": "2026-06-11T12:23:44Z",
  "provenance": {
    "source_system": "VEGO-AI",
    "policy_version": "human-review-policy-v1",
    "source_commit": "bc9b54e",
    "source_setting": "ucd_ch",
    "policy_config": { "include_medium": true }
  },
  "setting_id": "ucd_ch",
  "domain": "cheers",
  "diagram_type": "UCD",
  "pipeline_stage": "agent4_classify_variability",
  "pattern_id": "P4",
  "pattern_kind": "fragment",
  "target_fragment": "The inclusion of system interactions with 'Gefen System' ...",
  "related_guideline_id": "G16",
  "related_guideline_resolution": {
    "method": "parsed_from_evidence",
    "confidence": "medium",
    "candidate_guidelines": ["G16"]
  },
  "affected_cases": ["68092", "68162", "68075"],
  "pattern_strength": { "value": 0.225, "display": "22.5%" },
  "ai_decision": {
    "classification": "Substantial Variability",
    "confidence": "High",
    "justification": "...",
    "evidence": "G16 -- \"At the start of each month...\"",
    "flag_for_guidelines_update": true,
    "requires_human_review": false
  },
  "trigger_reasons": ["guideline_update_proposed"],
  "status": "pending",
  "feedback_id": null
}
```

`related_guideline_id` resolution is transparent: `method` is `from_pattern` (the
deviation pattern carried a `guideline_id`), `parsed_from_evidence` (extracted a
`Gj` token from the classification evidence — fragment patterns have no guideline
id of their own), or `none`. `feedback_id`/`status` are the join hooks for
Milestone 2.

## Reproduce (no API key required)

From `framework/`:

```bash
# All four settings, broad policy, written to ../human_review_output/<setting>/
python human_review_queue.py --all-settings ../eval_output

# One setting, strict policy
python human_review_queue.py --from-eval-output ../eval_output/ucd_ch --no-include-medium

# Write next to the source agentD files instead of the separate output folder
python human_review_queue.py --all-settings ../eval_output --in-place
```

Run the tests (no third-party dependency required):

```bash
python tests/test_human_review_queue.py     # or: pytest tests/
```

## Output location

By default the CLI writes to a **separate** folder, `human_review_output/<setting>/
human_review_queue.jsonl`, so the official baseline `eval_output/` stays pristine.
When wired into a live run, the pipeline hooks
(`orchestrator.run_setting`, `evaluator.phase_d`) write the queue into that run's
own `output_dir`.

## Properties

- **Non-breaking**: pipeline hooks are wrapped in `try/except` that logs a warning
  (never silent, never fatal). The change only appends a new file.
- **Idempotent**: `write_queue` rebuilds the file deterministically and dedups by
  `review_id`; re-running does not accumulate or duplicate items.
- **Versioned**: every item carries `schema_version`, `policy_version`, and
  `source_commit` for cross-experiment comparison.

## Follow-On Milestones

Milestone 2 is documented in `human_feedback_manager.md`: human feedback input,
schema validation, signature checking, and resolved queue writing.

Still deferred: Human Judgment Memory and reuse into Agents 2/4 via
`resolve_with_answers` (M3), gating the auto guideline-refinement loop behind
human approval, and visualizer feedback widgets. All of these join on `review_id`.
