# Continuation Plan - 2026-07-24 (Post Evidence-Ready Thesis Package)

Last updated: 2026-07-24 by Fable (Claude). Status: ACTIVE. Successor to `docs/research/h-layer/enhancement-plan-2026-07-12.md` (Phase 2/3 items absorbed here) and companion to the evidence ladder and EXP-019-027 protocols.

## 0. Where We Stand

The evidence-ready package covers the B0-B5 evidence ladder, EXP-019-027
registered protocols (independent reviewers, adjudication, 16-development /
8-sealed-holdout, external replication, human effort, and robustness),
preregistration, claim-to-chapter traceability, a review-ready DOCX with a
local-only rendered PDF, and the offline baseline-progress explainer. Exact
test and page counts belong to the final dated verification record. EXP-005
remains 0/24 independent labels; the policy still changes 0/27
classifications; no accuracy claim is made.

The defining fact of this phase: **the critical path is now human, not code.** Every accuracy-bearing step waits on Iris/Arnon approvals and two reviewers labeling 24 rows. The plan below therefore has one human-gated spine and three parallel non-gated tracks, so agent/user work never idles while approvals are pending - and never front-runs them.

## 1. Phase 0 - Secure The Work (this week, highest urgency)

| # | Action | Owner | Why now |
| --- | --- | --- | --- |
| 0.1 | Audit, explicitly stage, commit, and push the intended thesis-package paths to the existing publication branch | Ali or authorized agent | Preserve the package without sweeping in private, ignored, protected, or unrelated paths |
| 0.2 | Rerun `.\scripts\verify-hlayer-all.ps1 -WithOverview` immediately before committing; record the run in the commit message | agent | Commit provably-green state |
| 0.3 | Update existing draft PR #8; do not open a competing PR | Ali or authorized agent | PR #8 is the sole review and publication record |
| 0.4 | Send the supervisor pre-reads: thesis PDF + baseline-progress HTML + the one-page decision sheet (labeling protocol, reviewer roles, holdout boundary, claim gates - the M-decision register format) | Ali | Approvals are the gate to everything in Phase 1 |

## 2. Phase 1 - The Human-Gated Spine (label campaign -> evidence ladder climb)

Sequence (each step gated on the previous):

1. **Approvals** (Iris + Arnon): labeling protocol, reviewer roles, 16-dev/8-sealed-holdout boundary, claim gates. Capture outcomes in the decision register; regenerate the decision snapshot.
2. **Label campaign**: two independent reviewers label the 24 generalization-safe rows on the blind sheets; adjudication for disagreements; kappa computed; `gold_labels` frozen per protocol.
3. **Controlled evidence refresh**: validate the human-filled export, rerun the
   approved downstream evaluation, and inspect every refreshed output.
   EXP-012 remains stopped at zero labels; 1-19 safe labels are pilot-only and
   20-24 are quantitative with explicit limitations. B3 does not open
   automatically: it still requires development error analysis and supervisor
   approval.
4. **Error analysis** (EXP-003 tooling) on labeled rows -> only if errors exist that memory could plausibly correct, design **M4B-1.1 on the 16 dev rows only**, then a **single-shot sealed-holdout test** per the registered protocol. Supervisor approval before any policy lands in code.
5. **Robustness/effort experiments** (registered EXP-02x set) in protocol order.

Agent support work that is allowed NOW without front-running (prepare, don't execute):
- Labeling logistics kit: reviewer instruction one-pager, expected time-per-row estimate, session checklist, file-lock warnings (ISS-011).
- A dry-run of the full post-label pipeline on a clearly-marked SYNTHETIC filled sheet (existing pattern) to guarantee zero friction on labeling day - outputs quarantined as synthetic, never promoted.
- Thesis Chapter-7 injection dry-run: verify the quantitative placeholders regenerate from EXP outputs mechanically, so real numbers flow into the draft the same day labels land.

## 3. Phase 2 - Parallel Non-Gated Tracks (proceed while waiting)

**Track A - Academic deadlines (hard dates, highest parallel priority):**
| When | What |
| --- | --- |
| Mid-August (~3 weeks) | Pnina-course literature-survey PRESENTATION - build slides from the taxonomy branches + gap statement; this cannot slip |
| End-Sep/Oct | Written survey submission (doubles as thesis Ch. 2 input) |
| Sept-Oct | Framework+survey paper assembly (redirect-plan P4) |
| Ongoing | Sigal / Graduate Studies direct-track admin question (still open since 2026-07-01) |

**Track B - Deferred enhancements (from the 2026-07-12 plan) - IMPLEMENTED 2026-07-24:**
- E6 DONE (pytest lane): `EvidenceGuardIntegrationTests` marked `slow` (registered marker in `pyproject.toml`); fast dev lane `pytest scripts/tests -m "not slow"` runs in ~6s vs ~69s full. The shared parse-cache half of E6 stays deferred (touches hardened runner semantics; needs an equivalence proof).
- E7 DONE: `build-confluence-wiki.ps1` now emits `vego-ai-hlayer-program-overview.md` sourced from the generated overview (missing-tolerant, sanitized by the existing Protect-WikiContent pass).
- E8 DONE: `build_hlayer_program_overview.py` also writes `program_overview.html` - a self-contained offline small-multiples chart (one panel per metric, single validated hue, light+dark, hover tooltips, data-table view, schema-gap line breaks); render-verified via headless browser screenshot. Covered by an added pytest case (5 total for the overview).
- Standing rules unchanged: suite reruns only via `run-hlayer-iteration.ps1`; `verify-hlayer-all.ps1` before every finish.
- Fix landed en route (2026-07-24): the stale `policy-candidate-record` test record was completed for the hardened schema (concurrent agent) and the thesis evidence snapshot was regenerated with the current builder. The two REMAINING test failures are the DESIGNED COMMIT-GATE: `thesis-evidence-snapshot` and `thesis-review-package` schemas pin `canonicalSourcesDirty`/`sourceTreeDirty` to `false`, so they stay red until Phase 0.1 (commit) executes - by design, not defect.

**Track C - MediVARIA / PhD trajectory (low intensity):**
- MV-P2 groundwork that needs no partner/data: ethics-requirements catalog skeleton, guideline-corpus selection criteria note.
- Idea-log upkeep; PhD-proposal outline once thesis review cycles start.

## 4. Phase 3 - Thesis Finalization Trajectory

1. Supervisor review cycle on the 87-page draft (expect 2-3 rounds) -> tracked change-log per round.
2. After labels: Chapter 7 quantitative sections are filled from validated
   outputs; validity threats are updated with observed agreement and any
   holdout outcome. B2 may support quantitative reporting with limitations at
   20-24 safe labels; B4 remains an eight-row one-time pilot and never becomes
   a formal improvement claim.
3. Haifa submission mechanics: formatting requirements, abstract (and Hebrew abstract if required), declaration pages, submission checklist - start this early, it always takes longer than expected.
4. Target unchanged: ~March 2027 fast-path submission; PhD proposal a semester later with the thesis as preliminary results.

## 5. Risks

| Risk | Mitigation |
| --- | --- |
| Unpublished-work loss | Complete the explicit commit, PR, CI, and merge sequence without broad staging |
| Supervisor availability in August (semester break) | Send pre-reads + decision sheet now; ask for an approval meeting before mid-August; the survey presentation is independent of approvals |
| Label quality / low kappa | Adjudication protocol already registered; treat 1-19 labels as pilot band honestly |
| Holdout discipline | Sealed 8 rows: single-shot, preregistered; any second look invalidates B4 - the protocols already say this, keep them loud |
| Scope creep back into feature work | Feature development is DONE for this phase by design; new code only for Track B items or post-approval protocol execution |
| Survey deadline crowd-out | Track A outranks Tracks B/C in any conflict |

## 6. Definition Of Done For This Plan

- Intended work is committed, pushed, reviewed through PR #8, and merged only after all required checks are green.
- Approvals recorded; 24 rows labeled by two reviewers; kappa + adjudication done; gold labels frozen.
- EXP-012 reports a real generalization-safe baseline in its correct band; ladder position updated; thesis Ch. 7 carries real numbers with claims matching the band.
- Survey presented (mid-Aug) and submitted (Sep/Oct); paper draft assembled.
- No governance gate violated at any point (verify-hlayer-all green at every checkpoint).
