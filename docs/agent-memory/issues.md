# Issues

Track project issues here. Keep active issues near the top.

## Open

| ID | Date | Source | Severity | Status | Summary | Next Step |
| --- | --- | --- | --- | --- | --- | --- |
| ISS-002 | 2026-06-11 | Codex | Low | Open | Prompt memory automation is script/instruction based, not a background service or native runtime hook. | Use the scripts consistently; consider native hooks later if the active tools support them. |
| ISS-004 | 2026-06-11 | Codex | Medium | Open | Data sensitivity, provenance, and IRB constraints are not audited yet. | Complete `docs/research/data-management-plan.md` and `docs/research/ethics-irb.md` checklists. |
| ISS-005 | 2026-06-12 | Codex | Medium | Blocked | Live Confluence sync target is configured locally, but Atlassian Rovo reports cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted; rechecked 2026-06-14 14:50 +03:00. Chrome UI fallback was checked 2026-06-13 13:50 +03:00, but the extension-backed browser channel was unavailable after retry. | Grant Atlassian Rovo access, or enable the Codex Chrome Extension route, then read page `294914`, update the home page, create/update the four child pages, and store child page IDs in ignored local config. |
| ISS-006 | 2026-06-12 | Codex | Medium | Open | M4B-1 memory-informed parallel comparison now has EXP-003/EXP-004/EXP-005 evaluation tooling, but no completed generalization-safe expert-label evaluation yet. | Fill the EXP-005 blind label-review sheet with at least 20 safe expert labels, rerun `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream`, and do not claim accuracy improvement until evidence exists. |
| ISS-007 | 2026-06-14 | Codex | Medium | Open | M4B/C4B can suffer evaluation leakage if memory from the same pattern is reused for that pattern; EXP-001 has 3 same-pattern expert-labeled rows and 0 generalization-safe expert-labeled rows, while EXP-002 identifies 24 generalization-safe candidate rows for labeling. | Keep same-pattern rows as mechanism validation only; label EXP-002 generalization-safe candidates before making generalization claims. |
| ISS-011 | 2026-06-21 | Codex | Low | Open | EXP-005 label package regeneration can hit a Windows file lock if `exp005_label_review_blind.csv` is open in Excel while the workbench or build script tries to rewrite it. | Close the blind CSV before rerunning `.\scripts\open-vego-workbench.ps1` or `.\scripts\build-exp005-label-review.ps1`; reopen it after generation completes. |
| ISS-012 | 2026-06-22 | Codex | Medium | Open | Strategic review found a false-accuracy-narrative risk: synthetic EXP-004 results or same-pattern labels could be misread as real accuracy improvement. | Keep EXP-004 labeled as synthetic policy-risk screening, keep same-pattern rows as mechanism validation only, and quote the EXP-005 gate status in every accuracy report. |
| ISS-013 | 2026-06-22 | Codex | Medium | Open | Strategic review found that one-reviewer labels would be weak evidence for strong accuracy/generalization claims. | Use generated `exp005_adjudication_sheet.csv` for reviewer-2 or supervisor adjudication and review the reliability summary before treating results as strong quantitative evidence. |

## Blocked

| ID | Date | Source | Reason | Summary | Needed |
| --- | --- | --- | --- | --- | --- |

## Resolved

| ID | Opened | Resolved | Source | Summary | Resolution |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | 2026-06-11 | 2026-06-11 | Codex | Workspace was not a Git repository, so true file-level revert support was not available. | Added `.gitignore` and initialized Git; baseline commit remains tracked as `ISS-003`. |
| ISS-003 | 2026-06-11 | 2026-06-11 | Codex | Git was initialized but no baseline commit existed, so revert support was incomplete. | Created and pushed safe baseline to private GitHub repo `AliHamed17/Vego-Ai` on `main`. |
| ISS-008 | 2026-06-14 | 2026-06-14 | Codex | `scripts/research-health.ps1` flagged tracked `VEGO-AI/analysis/build_results_dashboard.py` as a forbidden analysis artifact, causing project/research health to fail after the dashboard merge. | Added a narrow allowlist for `VEGO-AI/analysis/build_results_dashboard.py` while keeping generated spreadsheets and controlled analysis artifacts forbidden; `project-health`, `research-health`, and `dashboard-health` pass. |
| ISS-009 | 2026-06-14 | 2026-06-14 | Codex | The visualizer could silently show stale or mismatched model/result pairs because aggregate selection used loose substring matching and did not clear the previous model when no match existed. | PR #7 added exact `<case_id>_` matching, stale-model clearing, a persistent pairing banner, filters/details, read-only research panels, and helper regression tests; real-display GUI validation passed, PR #7 merged as `78b261e`, and tag `research-state-visualizer-ux-clean` was pushed. |
| ISS-010 | 2026-06-16 | 2026-06-16 | Codex | The bundled presentation artifact-tool runtime was unavailable when exporting the supervisor PPTX deck. | Generated the Markdown and HTML decks, then used the local ignored fallback PPTX builder to produce a 20-slide PowerPoint deck and recorded the limitation in `artifacts/supervisor_demo_2026-06-17/README.md`. |
