# Ethics And IRB

## Current Status

The repository records a student/modeling protocol identifier but does not
contain enough evidence to verify its approval date, expiry, or full scope.
Nothing in this file proves that a student/modeling determination covers
MIMIC, Clalit, patient data, clinical derivatives, or a medical transfer study.

The open PDF filename references IRB, so future work should verify the approved protocol, consent constraints, anonymization rules, and publication permissions before sharing data or examples.

Until this checklist is completed, deferred artifacts remain `Controlled / do not publish` in `artifact-audit.md` and `publishability-register.md`.

## Medical Extension Status

Status: **BLOCKED / NOT AUTHORIZED**.

Before any patient-row access or clinical processing, the program requires a
written dataset- and use-case-specific determination covering:

- named-user authorization and the stated research purpose;
- ethics/IRB or exemption status;
- privacy roles, retention, deletion, export, publication, and incident rules;
- derived data and model-output handling;
- approved restricted environment and audit logging;
- clinician, custodian, privacy/ethics, and VDI responsibilities;
- an approved cohort/process/outcome protocol with leakage and missingness
  controls.

The operational proof checklist is
`docs/research/governance/medical-readiness-scorecard.md`. All six gates are
open/blocked as of 2026-07-30. MIMIC access normally requires dataset-specific
credentialing/training and a DUA; Clalit requirements must come from the named
partner and data/privacy authorities. No ordinary Drive share substitutes for
those approvals.

## Checklist

- IRB protocol identifier: `IRB2-Iris`
- Approval date: `Unknown (not in repository)`
- Expiration/renewal date: `Unknown (not in repository)`
- Data categories covered: `Student domain models (UML use case and class diagrams) from modeling course; expert labeling/evaluation sheets.`
- Participant/student data included: `Yes (anonymous student models from university course).`
- Anonymization method: `No names, IDs, or identifiers in data/git. Stored with random candidate hashes.`
- Sharing restrictions: `Controlled / do not publish (only metadata, synthesized examples, and anonymized statistics may be shared/published; raw student models and expert worksheets are ignored by Git).`
- Publication restrictions: `Publication restricted to aggregated metrics, illustrative anonymized examples, and theoretical/framework findings in MODELS 2026/thesis; no raw personal data.`
- Contact person: `Iris Reinhartz-Berger`

## Rule

If a file may contain participant, student, expert, or institutional data, treat it as controlled until proven safe.

If a file may contain patient-level, clinical, or restricted-data-derived
content, keep it in the approved VDI and treat it as non-exportable until the
data custodian and ethics/privacy authority approve the exact artifact. Do not
send it to an online LLM or third-party API.
