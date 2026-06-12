# Data Management Plan

## Data Zones

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

Use `provenance-register.md` for source/ownership records and `publishability-register.md` for venue-specific sharing decisions.

## Sensitivity

Treat student models, expert labels, and IRB-related material as controlled research data unless confirmed otherwise.

Use `artifact-audit.md` as the metadata-only register for ignored/deferred artifacts. Do not copy controlled contents into Git, Confluence, or paper/thesis appendices until publishability is explicitly approved.

Never store:

- API keys,
- participant identifiers,
- private emails,
- raw sensitive data without access control,
- unpublished third-party material without permission.
