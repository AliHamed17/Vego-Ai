# Unified Runtime and Security Hardening

Status: **release candidate; independent human approval required before merge**.

This package records Iteration 15 work on the additive M1–M4B-1 human-judgment
layer. It does not change Agents 1–4, Agent 4 classifications, the official
baseline outputs, or the empirical evidence gate.

## What this release adds

- A versioned canonical H-layer contract package under `src/vego_hlayer`.
- Explicit `legacy`, `unified`, and fail-closed `parity` runtime modes.
- Deterministic adapters that preserve all historical artifact names.
- Portable baseline, security, SBOM, model-execution, architecture-run, and
  release manifest contracts.
- Protocol-only EXP-028/029 model reproducibility and frozen-comparison gates;
  `gpt-4o` remains the default.
- Frozen Python and browser toolchains, an environment doctor, full CI test
  inventory, and an aggregate `merge-gate`.
- Metadata-only interaction logging by default, bounded local retention,
  credential rejection, secret/privacy scanning, archive validation, and a
  strict new-code security ratchet.
- Three explicit verification entry points:
  `verify-source.ps1`, `verify-controlled.ps1`, and `verify-release.ps1`.

## Evidence boundary

The controlled parity gate covers 11 review items, 3 legacy mechanism-memory
records, and all 27 M4B-1 comparison rows. It records zero classification
changes. This is mechanism parity and baseline-protection evidence, not
accuracy evidence.

EXP-005 remains at 0/24 independent generalization-safe labels. EXP-012 remains
`NOT YET COMPUTABLE`. Accuracy, generalization, benchmark superiority, reduced
human effort, and clinical performance are not established.

## Human gates

The PR must remain open until:

1. GitHub protection rules can require the aggregate `merge-gate`.
2. A separate named collaborator reviews and approves the PR.
3. All conversations are resolved and all checks are green.
4. A final clean-tree release verification succeeds.

No automation in this package bypasses those gates.
