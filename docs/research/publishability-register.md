# Publishability Register

Track whether a project artifact can be shared in GitHub, Confluence, papers, thesis appendices, or external supplements.

## Status Values

- `Allowed`: safe to publish in the named venue.
- `Controlled`: do not publish until reviewed.
- `Metadata only`: record path/category/status, not contents.
- `Generated internal`: regenerate locally; do not publish by default.
- `Unknown`: missing provenance or permission.

## Register

| Artifact Group | GitHub | Confluence | Paper/Thesis | External Supplement | Reason | Required Approval |
| --- | --- | --- | --- | --- | --- | --- |
| Source code in `VEGO-AI/framework/` and `VEGO-AI/eval/` | Allowed | Summary only | Describe methods | Maybe | Already safely published to private GitHub. | Owner review before public release. |
| Project docs and architecture | Allowed | Allowed | Reuse/adapt | Maybe | Contains project process, not controlled data. | Normal review. |
| Agent memory logs | Allowed in private repo | Summary only | No | No | Useful operational history, but noisy and may include process details. | Review before external sharing. |
| Root PDF / IRB-related material | Controlled | Metadata only | Controlled | No | May contain protocol, review, or unpublished paper content. | IRB/protocol and author approval. |
| Source archives and executables | Controlled | Metadata only | No | No | Large/binary and unaudited. | Owner and data audit approval. |
| Case models and visualizer bundled models | Controlled | Metadata only | Controlled examples only | Controlled | May include student/participant/institutional data. | IRB/provenance approval. |
| Analysis and eval outputs | Controlled | Metadata only | Controlled summaries | Controlled | May encode model or expert-label content. | IRB/provenance approval. |
| Generated Confluence outbox | Generated internal | Not tracked | No | No | Draft mirror generated from safe docs. | Configure live target before use. |

## Current Decision

No deferred artifacts move from `Controlled` to `Allowed` until `docs/research/ethics-irb.md` and this register are explicitly updated.
