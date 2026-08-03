# PhD Medical Data Boundary

**Effective baseline:** 2026-07-30
**Status:** **ACTIVE CONTROL; MEDICAL EXECUTION BLOCKED**
**Applies to:** MIMIC, Clalit, and any other patient, clinical, health-system, or credentialed medical data considered by the PhD project.

## 1. Purpose and authority

This boundary prevents unapproved disclosure, uncontrolled copying, license violations, and evidence overclaiming. It applies even when source data is described as deidentified.

The controlling order is:

1. applicable law and institutional policy;
2. ethics/IRB and data-owner decisions;
3. the applicable data-use agreement or license;
4. this project boundary;
5. a study-specific approved protocol.

The strictest applicable rule wins. This document cannot grant access or weaken an external obligation. Unknown requirements are treated as blocked until the relevant authority decides them in writing.

## 2. Data classes

| Class | Description | Examples | Default handling |
| --- | --- | --- | --- |
| P0 — Public | Deliberately public, non-sensitive information | Published papers, public schema documentation, official URLs | Repository or shared Drive |
| P1 — Internal non-medical | Project operations without patient data | Plans, blank templates, task registers | Repository or access-controlled shared Drive |
| P2 — Controlled derived | Non-row-level medical metadata or aggregates that still require review | File names/sizes, approved counts, model metrics, aggregate plots | Restricted VDI until downstream D3 approval; then the explicitly approved destination |
| P3 — Restricted medical | Patient-level, event-level, record-level, credentialed, or re-identification-sensitive data | MIMIC CSV rows, clinical notes, timestamps, encounter IDs, row-level Clalit data, embeddings derived from notes | Restricted VDI only |
| S — Secrets | Authentication or security material | Passwords, tokens, API keys, private access URLs | Approved secret manager only |

Small samples, screenshots, copied cells, prompt excerpts, embeddings, and model traces inherit the source data class. Deidentification does not automatically convert P3 into P1 or permit redistribution.

## 3. Zone rules

### Zone R — Repository

**Purpose:** versioned research design, code, public references, governance templates, metadata-only audits, and approved non-sensitive documentation.

Permitted:

- P0 and P1 materials;
- code that contains no medical rows, secrets, or embedded access paths;
- metadata such as table names and file sizes;
- an aggregate artifact only when downstream D3 explicitly names the repository as an approved destination.

Prohibited:

- patient, encounter, event, note, or row-level data;
- raw MIMIC or Clalit files;
- identifiers, dates, copied cells, screenshots, or representative patient examples;
- embeddings, prompts, completions, logs, caches, or test fixtures derived from P3;
- credentials, secrets, or signed download URLs.

### Zone D — Shared Google Drive

**Purpose:** supervisor collaboration on proposals, literature review, approved meeting artifacts, blank templates, and non-sensitive project administration.

Permitted:

- P0 and P1 materials;
- approved P2 summaries after downstream D3;
- links to official public documentation.

Prohibited:

- all P3 data, including credentialed MIMIC CSVs and row-level Clalit data;
- patient-level exports, clinical notes, event timelines, screenshots, copied cells, or identifiers;
- unrestricted sharing links for controlled artifacts;
- use as a staging area between a source system and the VDI.

The 2026-07-30 metadata audit observed apparent raw MIMIC CSV files in this zone. Their authority and disposition are unresolved. They must not be opened, copied, moved, deleted, or shared by this work; the data steward must execute any remediation through an approved process.

### Zone V — Restricted VDI

**Purpose:** the only project zone that may hold or process P3 after all six entry gates G1–G6 pass.

Required controls:

- named, individually authorized users;
- purpose-bound access with least privilege;
- approved storage, encryption, logging, patching, backup, retention, and deletion controls;
- network and clipboard/drive-redirection controls defined by institutional security;
- approved local software and dependency sources;
- no unapproved synchronization to OneDrive, Google Drive, Git, chat, email, or personal devices;
- local/offline model execution only when specifically approved;
- export quarantine for every derived artifact.

### Zone X — External and online services

This includes online LLMs, commercial APIs, browser upload forms, cloud notebooks, hosted code assistants, paste sites, email, messaging, and any service whose retention, training, review, logging, caching, or subprocessor behavior is not institutionally controlled.

P2 and P3 medical content is prohibited. This includes a single row, a "deidentified example," an embedding, a screenshot, a schema plus values, or a prompt/completion derived from restricted data.

PhysioNet's guidance requires zero data retention for third-party LLM services, warns that service behavior may be unclear, and recommends locally deployed models. This project uses a stricter baseline: no MIMIC, Clalit, or other medical content may be sent to an online LLM/API.

## 4. Allowed data flow

```text
Public documentation / approved request
                |
                v
     Repository or shared Drive
                |
     metadata/configuration only
                |
                v
        Restricted VDI intake
                |
       P3 processing in VDI
                |
                v
      Export quarantine in VDI
                |
  D1 provenance -> D2 validation -> D3 disclosure
                |
                v
Approved aggregate/synthetic artifact
to the explicitly named destination
```

There is no direct P3 path to the repository, shared Drive, or Zone X. Each source must be acquired directly into the VDI by an authorized user through the approved source mechanism.

## 5. Derived-artifact rule

A derived artifact remains P3 until all of the following are true:

- its source, code, environment, parameters, and parent artifacts are recorded;
- it contains no patient-level values, notes, identifiers, rare-case excerpts, or reversible encodings;
- its aggregation, suppression, and disclosure checks are recorded;
- a clinical/methods reviewer confirms the interpretation;
- the data steward or privacy reviewer approves export;
- the supervisor approves the exact evidence claim and destination;
- downstream D3 is marked passed for that exact artifact, destination, audience, and claim.

File extension does not determine sensitivity. Models, embeddings, notebooks, logs, charts, screenshots, and prose can all remain restricted.

## 6. LLM and automation boundary

- No medical rows or derived excerpts in an online LLM, API, hosted notebook, or cloud code assistant.
- No automatic browser upload or synchronization from the VDI.
- A local/offline model requires an approved model identifier/version, weights provenance, runtime, logging behavior, storage location, and an evidence record that it has no external network dependency.
- Local model prompts and outputs remain in Zone V and inherit the highest input classification.
- Synthetic test data must be independently generated and documented; copying or perturbing a real row does not make it synthetic.
- Model output is not a clinical conclusion. Clinical and methods review remain mandatory.

## 7. Roles and decisions

| Role | Required responsibility |
| --- | --- |
| Lead researcher | Maintains purpose limitation, evidence records, provenance, and stop-work decisions |
| Supervisor/PI | Approves research scope, claim boundary, methods, and publication use |
| Clinical owner/expert | Confirms clinical meaning, cohort, outcome, risks, and interpretation |
| Data steward/privacy or ethics authority | Decides access, permitted environment, retention, disclosure, and export |
| IT/security owner | Approves the VDI, tools, network controls, logging, and incident path |
| Independent methods reviewer | Reviews study design, bias, leakage, evaluation, and reproducibility |

One person may hold more than one role only when institutional policy permits it. An unassigned role is `Unknown` and blocks the relevant gate.

## 8. Incident and exception handling

If medical data appears outside Zone V, or an unauthorized person/service may have received it:

1. stop processing and prevent further transfer;
2. do not forward, duplicate, or perform unsupervised deletion;
3. preserve only the minimum operational evidence required by the institutional incident process;
4. notify the data steward/security contact and supervisor through the approved channel;
5. record the affected source, destination, time, and containment decision without copying patient content;
6. revoke downstream gate approvals until the authority closes the incident.

There is no project-level exception for putting P3 data in the repository, shared Drive, or an online LLM. Any broader exception must be written by the data owner, data steward/privacy or ethics authority, IT/security owner, and supervisor, and must remain compatible with the governing license.

## 9. Official references

- [MIMIC-III Clinical Database v1.4](https://physionet.org/content/mimiciii/1.4/)
- [PhysioNet credentialing and reuse FAQ](https://physionet.org/about/faqs/)
- [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/)
- [Use of MIMIC Data with Large Language Models and Online Services](https://physionet.org/news/post/llm-responsible-use/)
