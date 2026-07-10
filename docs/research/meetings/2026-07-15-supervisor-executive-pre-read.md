# VEGO-AI Supervisor Follow-up - Executive Pre-read

**Meeting:** 2026-07-15 | **Audience:** Iris and Arnon | **Format:** 20-minute presentation + 20-minute decision discussion

**Status:** Two-page working pre-read. Recommendations below were developed after July 1 and are not attributed to either supervisor.

## Page 1 of 2 - Confirm the record and settle the H-layer shape

### Desired outcome

Confirm or correct the July 1 record, then leave the meeting with explicit outcomes for M-02 through M-05. M-06 is strategic and may be handled if time permits. Each outcome will be read back with rationale, approver, owner, and due date.

### Keep the evidence streams separate

| July 1 record | July 4-10 working layer | July 15 decisions |
| --- | --- | --- |
| Machine-derived Hebrew transcript, timestamped D1-D12 paraphrases, and attributed actions | Draft architecture, S1-S7/E1-E15 formalization, provisional specs, retired historical prototype scaffold, and offline mechanism evidence | Accepted / Accepted with changes / Rejected / Deferred, with named approver |

The current notes are not human-verified. Stockholm and Belgium are candidate future sites, March 2027 was illustrative, and Option B, the four-source H-Verify set, the two-round bound, and MediVARIA are later proposals.

### Decisions M-01 to M-03

| ID | Decision | Recommendation | Choice to record |
| --- | --- | --- | --- |
| **M-01** | July 1 record | Review D1-D12 and attributed actions row by row; correct the notes without altering raw ASR | Accept, correct, qualify, or defer each disputed row/action |
| **M-02** | H-layer decomposition | Two agents: Observer = H1/S1-S3; Integrator = H2+H3/S4-S7; keep H1/H2/H3 visible | Option B, Option A (three agents), or Option C (one agent/seven modules) |
| **M-03** | Observation and dosage | Passively observe E1-E14; route guideline churn, significant uncertainty, recurring ambiguity, and source conflicts; pilot `threshold_sev2`; prefer adaptive per-setting caps | Approve trigger set and pilot; choose adaptive or uniform caps |

### What the offline replay can honestly say

This Markdown source now reflects accepted offline iteration 009. Regenerate the shareable PDF before treating its figures as current.

- EXP-006 count comparison: `11 queue items / 481 heterogeneous reconstructed lifecycle events` (about 2.3%). This is a count ratio only; no event-level visibility inference or linkage exists.
- EXP-006 validates 481 captured plus 20 explicit gap records = 501 ObservationRecords; this is offline contract evidence, not complete live coverage.
- `threshold_sev2`: event load 0.799, transaction load 0.796, weighted coverage 0.981, high-severity coverage 1.0. The aggregate coverage >=0.8/load <=0.5 target remains unmet.
- Uniform K30/K35 capture is 0.75/0.85. These are Pareto points, not approved caps or defaults.

<div style="page-break-after: always;"></div>

## Page 2 of 2 - Set verification, authority, and thesis boundaries

### Decisions M-04 to M-06

| ID | Decision | Recommendation | Choice to record |
| --- | --- | --- | --- |
| **M-04** | H-Verify and convergence | Check Language Template, Reference Guidelines, domain description, and prior judgments; deterministic checks before semantic checks; at most two question rounds, then human adjudication | Confirm source set, order, and round bound |
| **M-05** | Human authority and implementation | Every phase-one correction needs explicit approval; timeout preserves baseline and parks the item; no automatic H3 advice; trained staff may review defined low-risk items while supervisors adjudicate; live hooks require a separately approved allowed-touch list | Confirm approval/timeout rules, reviewer roles, and authorization process |
| **M-06** | MSc and strategic direction | Finalize the MSc question after M-02-M-05; keep empirical work in education; treat domain-parameterized specs and MediVARIA as proposed PhD/future work | Decide RQ timing and confirm the education/future-work boundary |

### How to read the later evidence

- EXP-009 and EXP-010 are assumption-driven synthetic rule tests. Their seeded cases help inspect a protocol; they do not validate detection of real expert mistakes or real dialogue behavior.
- All July 10 detailed specifications remain provisional. The July 10 prototype scaffold is retired historical scaffolding and is not runnable evidence; current evidence comes from EXP-006..018 and the hardened offline harness.
- EXP-005 remains the parked real-label gate. With zero supplied real labels, accuracy improvement cannot be evaluated yet and no generalization-safe quantitative evaluation is available.
- EXP-012's same-pattern `N=3` pilot is excluded from this meeting narrative; it is not evidence and not an improvement claim.
- MediVARIA is a July 4 planning draft. It has no approved clinical scope, partner, data, ethics route, implementation, or performance evidence.

### Meeting close

Before ending, read back M-01 through M-06 and assign every accepted action. A blank or ambiguous outcome is recorded as `Deferred`, never inferred as approval. Within 24 hours, issue corrected minutes for confirmation, update the registers, revise only the provisional documents affected by accepted decisions, and regenerate the shareable package with new hashes.

**Decision source:** `2026-07-15-supervisor-decision-register.md`  
**Action source:** `2026-07-15-supervisor-action-register.md`  
**Provenance detail:** `2026-07-15-supervisor-follow-up-annex.md`
