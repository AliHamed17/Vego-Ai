# H-Layer Passive Shadow Listener - Provisional Allowed-Touch Proposal

Status: **PROPOSED, NOT APPROVED.** The project remains offline-only until M-05 is explicitly recorded and a separate implementation authorization approves this exact boundary. This document does not authorize code changes.

## Candidate Boundary

Only the following additions or touch points may be proposed for a first passive shadow-listener change:

1. `VEGO-AI/framework/orchestrator.py` at phase boundaries for append-only artifact/event observations.
2. `VEGO-AI/framework/qa_registry.py` for E2 request-ID allocation and E3 answer recording.
3. One new shadow-writer module: `VEGO-AI/framework/h_layer_shadow_writer.py`, responsible only for fail-open append operations.
4. One versioned schema, `VEGO-AI/schemas/observation_record.schema.json`, and one focused test file, `VEGO-AI/tests/test_h_layer_shadow_writer.py`.

The proposed configuration is additive, default-off, and fail-open:

```json
{
  "h_layer_shadow": {
    "enabled": false,
    "schema_version": "1.0",
    "output_subdir": "h_layer_shadow",
    "fail_open": true
  }
}
```

When separately authorized and enabled, the writer may append `events.jsonl` beside run outputs. Writer failure may produce a warning only; it must not fail the baseline pipeline.

## Explicit Exclusions

- No edits to Agent 1-4 modules or Agent 4 policy/behavior.
- No changes to existing output, evaluation, feedback, memory, or classification schemas.
- No prompt mutation, state-transition change, artifact rewrite, evaluation change, active routing, correction application, pipeline re-trigger, or automatic memory reuse.
- No semantic/LLM verification.
- No change to timeout behavior; missing review preserves baseline behavior and parks the item.

## Required Authorization and Acceptance Evidence

Before implementation, the decision register must contain an explicit M-05 outcome and a second approval naming the allowed files. A dedicated branch/PR must then demonstrate that shadow-on and shadow-off fixture runs have identical baseline artifact hashes, event records validate, failure is fail-open, and protected paths outside the approved list are unchanged.

The machine-readable authorization record must be created from `allowed-touch-authorization.template.json`. The template's placeholder outcomes are not approval and must fail any implementation gate.
