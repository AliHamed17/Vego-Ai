# Issues

Track project issues here. Keep active issues near the top.

## Open

| ID | Date | Source | Severity | Status | Summary | Next Step |
| --- | --- | --- | --- | --- | --- | --- |
| ISS-002 | 2026-06-11 | Codex | Low | Open | Prompt memory automation is script/instruction based, not a background service or native runtime hook. | Use the scripts consistently; consider native hooks later if the active tools support them. |
| ISS-004 | 2026-06-11 | Codex | Medium | Open | Data sensitivity, provenance, and IRB constraints are not audited yet. | Complete `docs/research/data-management-plan.md` and `docs/research/ethics-irb.md` checklists. |

## Blocked

| ID | Date | Source | Reason | Summary | Needed |
| --- | --- | --- | --- | --- | --- |

## Resolved

| ID | Opened | Resolved | Source | Summary | Resolution |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | 2026-06-11 | 2026-06-11 | Codex | Workspace was not a Git repository, so true file-level revert support was not available. | Added `.gitignore` and initialized Git; baseline commit remains tracked as `ISS-003`. |
| ISS-003 | 2026-06-11 | 2026-06-11 | Codex | Git was initialized but no baseline commit existed, so revert support was incomplete. | Created and pushed safe baseline to private GitHub repo `AliHamed17/Vego-Ai` on `main`. |
