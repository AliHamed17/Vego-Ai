# EXP-028 — Model Execution Reproducibility and Drift

Status: **Proposal — not approved. Protocol only; no execution result.**

## Research question

Can a future authorized VEGO-AI model execution be described precisely enough
to distinguish input, prompt, configuration, SDK, endpoint, and served-model
drift without changing the frozen Agent 4 baseline?

## Motivation

The historical baseline requested the `gpt-4o` alias, but the exact dated
snapshot served for those calls was not retained. The committed Agent 4 output
is therefore the reproducible baseline. This protocol improves future
provenance; it does not reconstruct the historical served snapshot.

## Inputs

- Frozen prompt and configuration hashes.
- Immutable input-artifact hashes.
- Requested model and endpoint.
- Approved cost and retention boundary.
- Explicit authorization for an API execution.

## Procedure

1. Validate the frozen prompt, configuration, and input hashes.
2. Execute the approved request without changing prompts or parameters.
3. Capture `ModelExecutionManifest-v1`:
   requested and returned model identifiers, endpoint, SDK version,
   prompt/input/config hashes, parameters, token usage, retries, errors,
   timestamp, and system fingerprint when returned.
4. Store metadata only by default. Full request/response content remains
   explicit, local-only, redacted opt-in.
5. Compare manifests descriptively for model identifier, fingerprint, latency,
   token, retry, and output-hash drift.
6. Preserve every result as a separate condition. Never overwrite B0.

## Acceptance

- Manifest validates and contains no prompt or response text in
  `metadata_only` mode.
- No plaintext credential is written.
- Prompt, parameter, and input hashes equal the frozen protocol.
- Agent 4 baseline files remain byte-identical.
- Differences are reported as provenance drift, not performance improvement.

## Stop conditions

- Authorization, cost limit, or data-retention decision is missing.
- A frozen input/prompt/config hash differs.
- The returned metadata cannot be linked to the run.
- Any output path would touch `eval_output` or another protected baseline.

## Claim boundary

EXP-028 may establish that execution provenance is complete for a recorded run.
It cannot establish accuracy, superiority, generalization, or model
replaceability.
