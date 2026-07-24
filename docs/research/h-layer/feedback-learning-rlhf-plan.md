# H-Layer Feedback Learning and Alignment: Gated Research Plan

Status: **PROVISIONAL WORKING DRAFT — OFFLINE ONLY.** M-02 through M-05 are unrecorded. This plan does not authorize prompt mutation, automatic memory reuse, model training, runtime integration, or any accuracy, generalization, or clinical-performance claim.

This document separates three possible research vectors from the behavior that currently exists. The current repository has offline replay and conformance evidence, a provisional interactive demo, and proposal-only correction fixtures. It does **not** have approved live S1-S3 listener hooks, an approved trusted-memory service, an Agent B prompt integration, or an evidence-bearing learning pipeline.

## 1. Current Boundary

The only permitted near-term flow is:

```text
review/demo feedback
  -> eligibility and provenance checks
  -> conflict isolation
  -> structured synthesis request
  -> provisional candidate rules
  -> human review / S6 proposal gate
  -> parked (not applied)
```

Only feedback that is S5-verified or explicitly supervisor-adjudicated, carries an allowlisted trusted-human/trusted-export origin, is explicitly `trusted_memory_eligible = true`, marked reusable, scoped, provenance-linked, and conflict-free may enter an offline synthesis request. A separately produced `trusted-feedback-export-validator-v1` manifest must bind the exact input-file hash and allowed record IDs; record-local fields alone are never sufficient. Self-declared demo, synthetic, adjudication-candidate, timeout, rejection, escalation awaiting adjudication, missing-provenance, and ambiguous-scope records stay excluded. Raw rationale text is untrusted data and must never be treated as prompt instructions.

The required companion shape is documented in `trusted-feedback-export-manifest.template.json`. The template is not approval and must never be copied unchanged into a run. The validator/approval workflow that produces a real manifest remains a human-governed prerequisite.

Generated candidate rules must carry `PROVISIONAL_NOT_APPLIED`, their source record IDs and hashes, an applicability scope, conflicts, and `runtime_eligible = false`. They cannot be appended to Agent B or any other runtime context without an M-05 outcome, an approved allowed-touch list, separate implementation authorization, and a reviewed implementation plan.

## 2. Research Vectors

### Vector 1 — Meta-instruction synthesis candidate (ICL)

Purpose: test whether verified feedback can be organized into reviewable, scope-bounded candidate rules without changing model weights or runtime prompts.

Offline phase:

1. Read feedback records from a selected local input.
2. Validate status, reuse scope, provenance, and conflict state.
3. Group eligible records by setting, pattern key, and reuse scope.
4. Produce structured S7 synthesis requirements with the raw rationales serialized as data.
5. Optionally accept a separately generated model response in a future approved run.
6. Validate every candidate against the source group and emit a proposal-only package.
7. Route accepted candidates through S6 as correction proposals; do not inject them into Agent B.

The first implementation intentionally performs no LLM/API call. It proves input eligibility, deterministic grouping, prompt-data isolation, provenance, and the no-application gate. A model/provider, final prompt text, and evaluation protocol require separate approval.

### Vector 2 — Supervised fine-tuning candidate (future work)

Purpose: study whether adjudicated feedback could support an instruction-tuning dataset. No training is authorized.

A future protocol would need independently reviewed training tuples, a frozen reference baseline, leakage controls, held-out evaluation, catastrophic-forgetting checks, compute and privacy approval, and a rollback path. EXP-005 labels must never be inferred or repurposed automatically.

### Vector 3 — Preference optimization candidate (future work)

Purpose: study whether adjudicated preference pairs could support a preference-learning experiment. No preference optimization is authorized.

A future protocol would need explicit winning/losing responses, reviewer agreement, a stable reference policy, preregistered metrics, evidence gates, and supervisor approval. Escalated overrides and unresolved disagreements are not preference labels.

## 3. Candidate Measurements and Gates

These are protocol questions, not achieved results or approved targets:

| ID | Candidate question | Minimum gate before measurement |
| --- | --- | --- |
| M-G1 | Do candidate rules transfer to held-out, leakage-safe patterns? | Approved protocol plus sufficient real, adjudicated labels; report `NOT YET COMPUTABLE` while the gate is closed. |
| M-G2 | How many verified feedback records are needed before a stable candidate rule recurs? | Repeated independent records with scope and provenance; do not equate prompt condensation with learning. |
| M-G3 | Does any future adapted policy preserve frozen baseline behavior outside the approved scope? | Separate training authorization, frozen benchmark, preregistration, and rollback test. |
| M-G4 | Are candidate rules traceable to eligible feedback and kept out of runtime contexts? | 100% source IDs/hashes, deterministic grouping, conflict isolation, and `runtime_eligible = false` in the offline phase. |

No numerical performance target is accepted by this plan. Values may be proposed later in a preregistered experiment and must remain clearly separate from observed results.

## 4. Phased Research Roadmap

### Phase 1 — Current MSc/offline evidence phase

- Maintain contract-driven offline replay and conformance tests.
- Keep EXP-005 at the human-label gate; do not invent labels.
- Use the supervisor demo only as an isolated interaction-design artifact.
- Generate eligibility reports and provisional synthesis requests; apply nothing.

### Phase 2 — Post-decision design phase

- Record M-02 through M-05.
- Approve the trusted-feedback contract, reviewer roles, allowed-touch list, and implementation boundary.
- Review Vector 1 candidate rules manually and decide whether a controlled prompt-context experiment is warranted.
- Preregister any learning or transfer evaluation before using results in the thesis.

### Phase 3 — Separately authorized training research

- Consider SFT or preference optimization only after sufficient adjudicated data, privacy review, a frozen baseline, and explicit compute/training authorization.
- Keep all results isolated from the MSc empirical claims unless their evidence gate is satisfied.

### Phase 4 — Strategic future work

- Domain-parameterized specifications and MediVARIA remain proposed PhD/future-work directions only.
- This plan authorizes no clinical data, deployment, validation, or clinical-performance statement.

## 5. Stop Conditions

Stop and emit a blocked/proposal-only result when any of the following holds:

- no verified or supervisor-adjudicated reusable feedback exists;
- feedback lacks reviewer/provenance/scope fields;
- decisions conflict within the same setting, pattern, and scope;
- the decision snapshot remains offline-only for an action that would affect runtime context;
- an LLM/provider or final prompt is required but has not been separately approved;
- a requested output would imply accuracy, generalization, or clinical performance beyond the evidence gate.
