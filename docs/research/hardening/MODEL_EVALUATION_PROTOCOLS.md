# Model Reproducibility and Evaluation Protocols

Iteration 15 keeps `gpt-4o` as the VEGO-AI runtime default and adds model
provenance interfaces only. It does not execute a candidate model or change the
historical Agent 4 output.

## Historical limitation

The original runs requested the `gpt-4o` alias. The exact served dated snapshot
was not retained. `BaselineLockManifest-v2` therefore freezes the committed
Agent 4 artifacts and records this limitation rather than claiming that a new
alias call can reconstruct the historical run.

## EXP-028

EXP-028 records model execution metadata with
`ModelExecutionManifest-v1`. Its purpose is to separate prompt/input/config
drift from SDK, endpoint, returned-model, fingerprint, retry, and output drift.
It is descriptive and requires explicit API-run authorization.

## EXP-029

EXP-029 is blocked until independent labels, agreement, adjudication, a frozen
policy/prompt/partition, supervisor approval, a sealed holdout, and a cost
ceiling exist. One dated candidate snapshot may then be compared as a separate
condition. The experiment cannot promote a model automatically.

## Shared invariants

- Agents 1–4, Agent 4 policy, and B0 remain unchanged.
- Prompts and parameters are identical across a frozen comparison.
- Each execution has a complete manifest and isolated output root.
- Pull-request CI makes no OpenAI API call.
- `metadata_only` remains the logging default.
- Positive, null, mixed, and harmful outcomes are all valid.
- No model result can bypass the independent-label or human-decision gates.
