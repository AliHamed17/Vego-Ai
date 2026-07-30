# Medical Research Governance Control Pack

**Control date:** 2026-07-30
**Current readiness:** **BLOCKED — 0 of 6 pre-row-level entry gates passed**
**Purpose:** keep the PhD medical track evidence-bounded while access, governance, scientific-design, and reproducibility requirements are completed.

This directory is a control pack, not an access authorization. It does not approve use of MIMIC, Clalit data, patient-level data, cloud services, or medical claims.

## Non-negotiable boundary

- No patient-level rows, clinical notes, record identifiers, or row-derived excerpts may enter the repository, the shared Google Drive, prompts, chat attachments, or an online LLM/API.
- Raw or row-level medical data may be handled only inside an institutionally approved restricted VDI by a named, individually authorized researcher and only for the approved purpose.
- A local/offline LLM may be considered inside the restricted VDI only after all six entry gates pass and Gate 5 explicitly approves an offline/no-telemetry toolchain. No online LLM/API is allowed for medical data under this project baseline.
- Only disclosure-reviewed, non-identifying aggregate or synthetic artifacts may leave the restricted VDI, and only after downstream disclosure/export control D3 passes and a completed provenance record is approved.
- Existing files are not evidence of lawful access, scientific validity, reproducibility, or supervisor approval.

PhysioNet identifies MIMIC-III v1.4 as a credentialed-access resource, requires human-research training and a signed data-use agreement, and forbids sharing access with other people. PhysioNet's current LLM guidance prohibits third-party sharing and recommends local deployment; this project adopts the stricter rule of no medical data in online services.

## Immediate control issue

The 2026-07-30 metadata-only audit observed 25 MIMIC CSV files in the shared Drive. Their apparent contents were not opened. Patient-level MIMIC files are not permitted in the shared-Drive zone under this control pack.

Do not download, move, rename, share, or delete those files as an ad hoc cleanup action. The data owner and institutional data steward must determine the authorized source, named licensee, permitted location, retention requirement, and controlled remediation. Until that decision is recorded, all six entry gates remain blocked.

## Documents

| Document | Purpose |
| --- | --- |
| [PhD data boundary](phd-data-boundary.md) | Defines the repository, shared-Drive, restricted-VDI, and external-service zones and the permitted movement between them. |
| [Medical readiness scorecard](medical-readiness-scorecard.md) | Defines the six mandatory pre-row-level gates—Use-case, People, Authorization, Ethics/privacy, Environment, and Protocol—plus downstream integrity, pilot, and export controls. |
| [MIMIC metadata audit](mimic-metadata-audit-2026-07-30.md) | Records the metadata verified on 2026-07-30 without reading patient rows. |
| [Clalit research request template](clalit-research-request-template.md) | Captures the clinical use case, minimum data need, governance, evaluation, ownership, and approval decision. |
| [Derived-artifact provenance template](medical-derived-artifact-provenance-template.md) | Creates an auditable chain from approved source and code to an export-reviewed aggregate artifact. |

## Required operating sequence

1. Read and acknowledge the data boundary.
2. Pass **Gate 1 — Use-case**: approve the clinical workflow, problem owner, unit, inputs, outputs, and measurable success/failure criteria.
3. Pass **Gate 2 — People**: name the clinician/domain expert, data custodian, privacy/ethics owner, VDI administrator, supervisor, and methods reviewer.
4. Pass **Gate 3 — Authorization**: verify that every researcher is individually permitted to use the selected data for the exact stated project.
5. Pass **Gate 4 — Ethics/privacy**: obtain the written MIMIC/Clalit determination covering derivatives, retention, publication, and incidents.
6. Pass **Gate 5 — Environment**: approve the VDI, storage, compute, audit logging, egress controls, and offline/no-telemetry tools.
7. Pass **Gate 6 — Protocol**: approve cohort, inclusion/exclusion, outcome, case/activity/timestamp rules, missingness, leakage, statistics, and stop criteria.
8. Only after all six entry gates pass, execute **D1 — Data integrity and provenance**: reconcile release, checksums, schema, row counts, source, and existing artifacts inside the approved VDI.
9. Only after D1 passes, execute **D2 — Bounded pilot and scientific validation** with clinical and methods review.
10. Only after D2 passes, execute **D3 — Disclosure, export, and evidence acceptance** for each exact artifact and claim.

The six entry gates are sequential and cumulative. No medical row may be inspected while any entry gate is blocked. Data integrity, a bounded pilot, and disclosure/export are mandatory downstream controls; they do not replace an entry gate.

The gate numbering and sequence in the [medical readiness scorecard](medical-readiness-scorecard.md) are authoritative. A reference elsewhere to only a subset of gates must never be read as authorization: all six entry gates and every applicable downstream control are required.

## Status vocabulary

- **BLOCKED (open):** required evidence or approval is missing; work may only close the stated evidence gap.
- **READY FOR REVIEW:** required evidence is attached and awaits the named approver.
- **PASSED:** every required item is verified, current, and signed by the named approver.
- **REVOKED:** a prior approval expired, changed, or was invalidated; later entry gates and downstream controls return to blocked.

## Official references

- [MIMIC-III Clinical Database v1.4](https://physionet.org/content/mimiciii/1.4/)
- [PhysioNet credentialing and reuse FAQ](https://physionet.org/about/faqs/)
- [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/)
- [PhysioNet guidance: Use of MIMIC Data with Large Language Models and Online Services](https://physionet.org/news/post/llm-responsible-use/)
