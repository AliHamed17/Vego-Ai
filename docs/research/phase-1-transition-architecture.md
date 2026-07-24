# Phase 1 Transition Decision Tree

Status: **Proposal — not approved.**

Updated: 2026-07-20.

Purpose: describe what may be considered after the July 21 supervisor discussion without treating silence, the EXP-005 tooling, offline fixtures, or later author proposals as authorization.

## 1. Current Stop State

The transition is blocked because:

- M-01 through M-06 have no confirmed outcome.
- EXP-005 has 24 generalization-safe candidate rows and 0 supplied labels.
- EXP-012 is `NOT YET COMPUTABLE`.
- No allowed-touch implementation authorization exists.
- Education remains the MSc empirical domain.

No runtime, Agent 4, M4B-2, baseline-output, prompt/context, active-correction, trusted-memory, or protected-path change follows from this document.

## 2. Decision Tree

```text
M-01 confirmed?
  no  -> correct/qualify the July 1 record; keep every derived item provisional
  yes -> continue

M-02..M-05 explicitly recorded?
  no  -> offline design and fixture work only
  yes -> update only the affected provisional specifications

M-05 authorizes an allowed-touch proposal?
  no  -> no live implementation
  yes -> prepare an exact-file proposal; request a separate implementation approval

Separate implementation approval recorded?
  no  -> no protected-path changes
  yes -> dedicated branch + reviewed PR + shadow on/off equivalence tests

EXP-005 protocol approved and labels supplied?
  no  -> EXP-012 remains NOT YET COMPUTABLE; no policy refinement
  1-19 safe labels -> pilot-only analysis; no quantitative thesis claim
  >=20 safe labels -> freeze adjudicated gold labels, then run leakage-safe evaluation

Error analysis justifies a deterministic comparison variant?
  no  -> preserve current M4B-1
  yes -> preregister a development/holdout protocol before any variant design
```

## 3. Conditional Work Packages

### A. Decision-record maintenance

Allowed after the meeting:

- Record `Accepted`, `Accepted with changes`, `Rejected`, or `Deferred`.
- Record rationale, approver, owner, due date, constraints, and affected artifacts.
- Regenerate the package from the recorded outcomes.

This work changes documents only.

### B. Expert-label evidence phase

Allowed only after protocol approval:

1. Two independent reviewers label the blind rows.
2. Validate signatures, provenance, and leakage class.
3. Measure agreement.
4. Adjudicate disagreements and freeze a gold-label artifact.
5. Run EXP-003 and repaired EXP-012 only when their gates permit.
6. Perform error analysis before proposing any policy refinement.

Synthetic labels, same-pattern memory, and AI-generated labels are not independent expert evidence.

### C. Passive-listener proposal

Allowed only if M-05 explicitly authorizes preparation of an allowed-touch proposal:

- Name each file, event boundary, output, failure mode, and rollback.
- Keep the feature default-off, append-only, and fail-open.
- Require shadow-on/shadow-off equality for core artifact hashes.
- Keep triage downstream and preserve every baseline state transition.

The proposal itself is not permission to edit protected paths.

### D. Deterministic policy research

Allowed only after:

- at least 20 validated generalization-safe labels;
- adjudicated gold labels;
- a preregistered development/holdout split;
- completed error analysis;
- supervisor approval for the exact deterministic comparison.

Any candidate remains parallel and non-destructive. No baseline overwrite and no M4B-2.

## 4. Not Authorized

- Automatic deployment of a “winning” policy.
- Direct work in `VEGO-AI/framework/`, `VEGO-AI/schemas/`, `VEGO-AI/tests/`, `VEGO-AI/eval/`, or `VEGO-AI/inputs/` from this document.
- A new `human_integrator.py` module.
- Automatic trusted-memory writes.
- LLM-based reclassification or semantic verification.
- MediVARIA runtime scaffolding, clinical data handling, or clinical-effect claims.

## 5. Acceptance Gate

Phase 1 becomes an implementation phase only when the decision register and a separate authorization name the exact approved behavior and files. Until then it remains an offline design/evidence phase.
