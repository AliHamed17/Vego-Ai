# MediVARIA Domain-Mapping Questions

Status: **Proposal — not approved; future work only.**

Updated: 2026-07-20.

Purpose: preserve a possible PhD research direction without implying domain transfer, schema authorization, clinical validation, patient-data access, alert reduction, or clinical benefit.

## 1. Current Boundary

- The MSc empirical domain is education.
- No real or synthetic clinical runtime is implemented here.
- No patient data, clinical partner, approved clinical protocol, ethics approval, or clinical ground truth is present.
- The existing E1-E15 catalog and H-layer contracts were developed for the education-domain research program.
- Similar terminology across domains does not demonstrate that the contracts transfer.
- Nothing in this document authorizes changes under `VEGO-AI/`.

## 2. Future Research Questions

1. Which education-domain event concepts, if any, have defensible analogues in a clinical decision-support workflow?
2. Which concepts fail to transfer because clinical responsibility, temporal context, uncertainty, or safety requirements differ?
3. What governance, ethics, privacy, security, and accountability controls would be required before collecting any clinical data?
4. Who may review, adjudicate, approve, supersede, or revoke a reusable judgment in a clinical setting?
5. How should patient context, guideline version, institution, care setting, and validity period constrain reuse?
6. What evidence would be necessary before testing alert workload, decision quality, or patient-relevant outcomes?

## 3. Candidate Analogy Table

The rows below are questions for a future feasibility study, not a schema mapping or validated equivalence.

| Education concept | Candidate future clinical analogue | Required validation before use |
| --- | --- | --- |
| Guideline authored or revised | Clinical guideline or local protocol version changes | Clinical informatics review; provenance and version-control study |
| Case context established | Encounter context | Data-minimization, consent/ethics, and temporal-context design |
| Deviation assessed | Decision-support rule identifies a possible mismatch | Clinical safety and responsibility analysis |
| Human feedback received | Clinician records a reason or requests review | Workflow study; reviewer burden and bias analysis |
| Verification/adjudication | Authorized clinical reviewer evaluates the evidence | Role, escalation, audit, and liability design |
| Judgment memory candidate | Scoped, time-bounded precedent candidate | Prospective safety protocol; conflict, expiry, and revocation rules |

## 4. Questions for a Future Data Contract

A future domain contract would need to decide, at minimum:

- whether pseudonymous identifiers are needed at all;
- how encounter and temporal context are minimized;
- how guideline and evidence versions are bound;
- how institution and jurisdiction limit reuse;
- how contraindications, exceptions, and missing evidence are represented;
- how a judgment expires, is superseded, or is revoked;
- how human authority and audit access are enforced;
- how leakage and cross-site transfer are measured.

No `domain_context` field or clinical schema extension is approved by this draft.

## 5. Evidence Needed Before Any Pilot

1. Supervisor approval to keep the topic in future work.
2. A clinical partner and named domain experts.
3. Ethics/privacy/legal review appropriate to the proposed data and setting.
4. A separate research protocol with claim boundaries and stop rules.
5. Synthetic design fixtures reviewed as fixtures only.
6. Prospective validation before any operational or clinical-performance claim.

## 6. Claims Not Supported

This project does not currently show:

- domain transferability;
- reduction of alert workload;
- suppression of clinically appropriate alerts;
- improved decision quality;
- improved patient outcomes;
- safe automatic reuse of clinical judgments.

MediVARIA remains a proposed PhD/future-work direction and is excluded from the MSc empirical results.
