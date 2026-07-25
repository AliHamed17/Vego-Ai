<!--
last_updated: 2026-07-10
staleness_threshold_days: 7
-->

# Issues

Track project issues here. Keep active issues near the top.

## Open

| ID | Date | Source | Severity | Impact | Effort | Status | Summary | Next Step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ISS-002 | 2026-06-11 | Codex | Low | Low | Medium | Open | Prompt memory automation is script/instruction based, not a background service or native runtime hook. | Use the scripts consistently; consider native hooks later if the active tools support them. |
| ISS-005 | 2026-06-12 | Codex | Medium | Medium | High | Blocked | Live Confluence sync target is configured locally, but Atlassian Rovo reports cloud `724252a1-a5b7-45a5-b6ec-27a8292197ec` is not explicitly granted. | Grant Atlassian Rovo access, or enable the Codex Chrome Extension route, then update pages. |
| ISS-006 | 2026-06-12 | Codex | Medium | High | High | Open | M4B-1 memory-informed parallel comparison has evaluation tooling, but no completed generalization-safe expert labels. | Fill the EXP-005 blind label-review sheet with at least 20 safe expert labels. |
| ISS-007 | 2026-06-14 | Codex | Medium | High | Low | Open | M4B/C4B can suffer evaluation leakage if memory from the same pattern is reused for that pattern. | Keep same-pattern rows strictly for mechanism validation; label EXP-002 candidates. |
| ISS-011 | 2026-06-21 | Codex | Low | Low | Low | Open | EXP-005 label package regeneration can hit a Windows file lock if CSV is open in Excel during build. | Close the blind CSV before rerunning workbench or build scripts. |
| ISS-012 | 2026-06-22 | Codex | Medium | High | Low | Open | Strategic review found a false-accuracy-narrative risk: synthetic results could be misread as real accuracy. | Keep synthetic outputs labeled as policy-risk screening only; quote label status in reports. |
| ISS-013 | 2026-06-22 | Codex | Medium | High | Low | Open | Strategic review found that one-reviewer labels would be weak evidence for strong accuracy claims. | Use `exp005_adjudication_sheet.csv` for reviewer-2 or supervisor adjudication and reliability checks. |
| ISS-014 | 2026-07-10 | Codex | High | High | Human decision | Blocked | M-02 through M-05 have no recorded outcomes, so architecture, dosage, H-Verify, authority, timeout, and live-hook choices cannot become defaults. | Record explicit outcomes in the July 15 decision register; silence remains deferred. |

## Blocked

| ID | Date | Source | Reason | Summary | Needed |
| --- | --- | --- | --- | --- | --- |

## Resolved

| ID | Opened | Resolved | Source | Summary | Resolution |
| --- | --- | --- | --- | --- | --- |
| ISS-001 | 2026-06-11 | 2026-06-11 | Codex | Workspace was not a Git repository. | Added `.gitignore` and initialized Git. |
| ISS-003 | 2026-06-11 | 2026-06-11 | Codex | Git was initialized but no baseline commit existed. | Created and pushed safe baseline to GitHub. |
| ISS-004 | 2026-06-11 | 2026-07-11 | Codex | Data sensitivity, provenance, and IRB constraints are not audited yet. | Completed the ethics-irb checklist and updated artifact-audit metadata status. |
| ISS-008 | 2026-06-14 | 2026-06-14 | Codex | `research-health.ps1` flagged tracked build_results_dashboard.py as forbidden. | Added a narrow allowlist for this dashboard script. |
| ISS-009 | 2026-06-14 | 2026-06-14 | Codex | Visualizer could show stale or mismatched model/result pairs. | PR #7 added exact matching and auto-clearing. |
| ISS-010 | 2026-06-16 | 2026-06-16 | Codex | Bundled presentation tool runtime was unavailable for PPTX deck. | Generated Markdown/HTML deck and used ignored PPTX builder. |
| ISS-015 | 2026-07-10 | 2026-07-10 | Codex | EXP-012 was not connected to the validated EXP-005 export. | Repaired explicit eligibility/leakage/provenance filtering and passed the canonical EXP-003 cross-check; safe N=0 still blocks computation. |
| ISS-016 | 2026-07-10 | 2026-07-10 | Codex | Next-step handoff/status drift and unsafe provisional feedback flows: seven-experiment/iteration-010 misreporting, adjudication leakage, self-asserted synthesis eligibility, partial output promotion, input/output aliasing, and linked-file writes. | Reconciled authoritative manifests/registry/ledger; required a separately validated hash-bound trusted export; added rollback publication, collision/protected/link guards, adjudication separation, and deterministic-only demo checks; full validation passes. |
| ISS-017 | 2026-07-25 | 2026-07-25 | Codex review | Exact-head review found stale artifact/manifest publication, Python numeric/boolean parity equivalence, and archive-history blindness after extension changes. | Added staged pair replacement with rollback, canonical-JSON parity comparison, raw-tree historical archive enumeration, and regression coverage; the complete release gate passes. |
