# Issues

Track project issues here. Keep active issues near the top.

## Open

| ID | Date | Source | Severity | Status | Summary | Next Step |
| --- | --- | --- | --- | --- | --- | --- |
| ISS-002 | 2026-06-11 | Codex | Low | Open | Prompt memory automation is script/instruction based, not a background service or native runtime hook. | Use the scripts consistently; consider native hooks later if the active tools support them. |
| ISS-004 | 2026-06-11 | Codex | Medium | Open | Data sensitivity, provenance, and IRB constraints are not audited yet. | Complete `docs/research/data-management-plan.md` and `docs/research/ethics-irb.md` checklists. |
| ISS-005 | 2026-06-12 | Codex | Medium | Blocked | Live Confluence sync target is configured locally, but Atlassian Rovo does not list cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` among accessible clouds; rechecked 2026-06-14 12:51 +03:00. Chrome UI fallback was checked 2026-06-13 13:50 +03:00, but the extension-backed browser channel was unavailable after retry. | Grant Atlassian Rovo access, or enable the Codex Chrome Extension route, then read page `294914`, update the home page, create/update the four child pages, and store child page IDs in ignored local config. |
| ISS-006 | 2026-06-12 | Codex | Medium | Open | M4B-1 memory-informed parallel comparison is implemented/merged but not yet evaluated as a controlled C4B experiment. | Run EXP-001/C4B and do not claim reusable memory improves AI variability interpretation until evidence exists. |
| ISS-007 | 2026-06-14 | Codex | Medium | Open | M4B/C4B can suffer evaluation leakage if memory from the same pattern is reused for that pattern. | Require `evaluation_leakage_status` and prefer leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout evaluation before making generalization claims. |
| ISS-008 | 2026-06-14 | Codex | Low | Open | `scripts/research-health.ps1` flags tracked `VEGO-AI/analysis/build_results_dashboard.py` as a forbidden analysis artifact, so project/research health currently fail after the dashboard merge. | Add a narrow allowlist for `VEGO-AI/analysis/build_results_dashboard.py` while keeping generated spreadsheets and controlled analysis artifacts forbidden. |

## Blocked

| ID | Date | Source | Reason | Summary | Needed |
| --- | --- | --- | --- | --- | --- |

## Resolved

| ID | Opened | Resolved | Source | Summary | Resolution |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | 2026-06-11 | 2026-06-11 | Codex | Workspace was not a Git repository, so true file-level revert support was not available. | Added `.gitignore` and initialized Git; baseline commit remains tracked as `ISS-003`. |
| ISS-003 | 2026-06-11 | 2026-06-11 | Codex | Git was initialized but no baseline commit existed, so revert support was incomplete. | Created and pushed safe baseline to private GitHub repo `AliHamed17/Vego-Ai` on `main`. |
