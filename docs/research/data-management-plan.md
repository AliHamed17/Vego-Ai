# Data Management Plan

The program-level authority for the July 29 doctoral work is
`docs/research/governance/phd-data-boundary.md`. The rules below remain the
repository-local implementation of that boundary.

## Program Data Boundary

| Zone | Allowed contents | Prohibited contents | Authority |
| --- | --- | --- | --- |
| Repository | Proposal text, metadata, schemas, manifests, code, aggregate software/modeling evidence, and approved non-sensitive derived records. | Patient rows, clinical extracts, direct identifiers, restricted derivatives, credentials, and unapproved partner material. | Git review plus claim, provenance, and publishability registers. |
| Ali-owned working Drive | Proposal drafts, literature workbook, weekly pre-reads, decisions, non-sensitive aggregate evidence, and links to controlled sources. | MIMIC/Clalit rows, patient-level extracts, restricted clinical derivatives, credentials, and raw expert/participant data. | Ali review before sharing; folder access and export controls. |
| Restricted VDI | Authorized MIMIC/Clalit rows, patient-level extracts, approved clinical derivatives, approved local models, and audit logs. | Online/commercial LLM calls, third-party APIs, unapproved exports, ordinary Drive copies, and Git commits. | Named-user authorization, ethics/privacy decision, custodian approval, environment controls, and protocol approval. |

The supplied MIMIC Drive remains a viewer/source resource. Link to it; do not
copy it into the working Drive. A Drive share is not proof that a named user is
authorized under the selected dataset agreement.

## Repository-Local Software/Modeling Data Zones

| Zone | Folder | Contents | Git Rule |
| --- | --- | --- | --- |
| Raw | `data/raw/` | Original data exactly as received. | Ignored by default. |
| External | `data/external/` | Third-party/reference data. | Ignored by default. |
| Interim | `data/interim/` | Temporary transformed data. | Ignored by default. |
| Processed | `data/processed/` | Cleaned/derived data for analysis. | Ignored by default. |
| Package data | `VEGO-AI/inputs/`, `VEGO-AI/models/` | Data bundled with current source package. | Review before committing. |
| Outputs | `outputs/`, `VEGO-AI/eval_output/` | Generated results. | Ignored by default unless curated. |

## Provenance Record

For each dataset, record:

- source,
- date received,
- owner/permissions,
- transformation steps,
- sensitivity level,
- intended use,
- storage location,
- whether it can be published.

Every derived medical artifact must additionally record the exact input
manifest and hashes, code/environment lock, parameters, owner, execution date,
restricted storage location, approvals, and export-review decision. Use
`docs/research/governance/medical-derived-artifact-provenance-template.md`.

Use `provenance-register.md` for source/ownership records and `publishability-register.md` for venue-specific sharing decisions.

## Sensitivity

Treat student models, expert labels, IRB-related material, MIMIC/Clalit data,
and any patient-level or potentially re-identifiable derivative as controlled
research data unless a documented authority explicitly determines otherwise.

Use `artifact-audit.md` as the metadata-only register for ignored/deferred artifacts. Do not copy controlled contents into Git, Confluence, or paper/thesis appendices until publishability is explicitly approved.

Never store:

- API keys,
- participant identifiers,
- private emails,
- raw sensitive data without access control,
- unpublished third-party material without permission.

Restricted medical data or derivatives must never enter this repository, the
ordinary working Drive, an online/commercial LLM, telemetry-enabled tooling, or
a third-party API. Metadata/schema inspection does not authorize row-level
processing.
