# Provenance Register

Record where datasets, outputs, and evidence artifacts came from. Keep this register metadata-only until the data/IRB audit is complete.

| ID | Artifact Group | Source | Date Received/Created | Owner/Permission | Storage Location | Transformations | Linked Experiment | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PROV-001 | Original source package | Delivered archive `VEGO-AI-20260611T112722Z-3-001.zip` | 2026-06-11 | Unknown | Repository root, ignored | Extracted to `VEGO-AI/` | `EXP-000` | Metadata recorded; content audit pending. |
| PROV-002 | Preserved runnable code | Extracted from delivered archive | 2026-06-11 | Unknown | `VEGO-AI/framework/`, `VEGO-AI/eval/` | Safe source subset committed to GitHub | `EXP-000` | Tracked safe code baseline exists. |
| PROV-003 | Lightweight input texts | Extracted from delivered archive | 2026-06-11 | Unknown | `VEGO-AI/inputs/` | Committed lightweight text inputs | `EXP-000` | Tracked; publishability still pending review. |
| PROV-004 | Case models | Extracted from delivered archive | 2026-06-11 | Unknown | `VEGO-AI/models/` | None recorded | `EXP-000` | Ignored; audit pending. |
| PROV-005 | Expert analysis and eval outputs | Extracted from delivered archive | 2026-06-11 | Unknown | `VEGO-AI/analysis/`, `VEGO-AI/eval_output/` | None recorded | `EXP-000` | Ignored; audit pending. |
| PROV-006 | Human feedback workflow examples | Created during Milestone 2 work | 2026-06-11 | Project generated | `VEGO-AI/inputs/human_feedback.example.jsonl` | Manual examples for schema/test coverage | Human-AI co-reasoning docs | Tracked safe example; continue checking for real expert data. |

## Required Fields For Future Entries

- Source and owner.
- Date received or created.
- Permission and sharing constraints.
- Storage location.
- Transformation history.
- Linked experiment or paper claim.
- Sensitivity and publishability status.
