# July 29 Zoom Reviewer Operations

Status: **operational plan; Reviewer A and Reviewer B remain unstarted; no adjudicated truth exists**

## Outcome and staffing

Two authorized Hebrew-English reviewers independently review all `1,195`
segments and the complete `46:26.283` audiovisual timeline. Reviewer A is Ali;
Reviewer B must be independent and must not see A's return before submitting.
A third bilingual person adjudicates every exact disagreement. A ledger
operator may validate files and hashes but must never create or alter human
review content.

Expected effort is `22–40 person-hours`: `8–12` hours for each reviewer,
`4–12` hours for adjudication, and `2–4` hours for merge/provenance QA. Exact
HE/EN comparison makes stylistic rewrites expensive, so reviewers should copy
acceptable machine text and change only genuine errors.

## Calibration and batching

1. Independently review this fixed 30-row calibration set: `S-0001–S-0006`,
   `S-0053–S-0058`, `S-0162–S-0167`, `S-0891–S-0896`, and
   `S-1087–S-1092`.
2. Compare the calibration only to align the codebook and formatting rules;
   do not copy substantive judgments between reviewers.
3. Review the four priority ranges before the remainder:
   `S-0053–S-0126`, `S-0150–S-0185`, `S-0891–S-0972`, and
   `S-1058–S-1152` (`287` segments total).
4. Complete the remaining `908` segments in ascending batches of roughly 100.
   Preserve one unique row per segment; gaps are allowed while work is partial.
5. Add `MEDIA-TIMELINE` last with `Record_Type=Full-media`. Its notes must cite
   the media hash/path, complete start-to-end review, date, and the exact
   machine uncovered-interval register. The register currently contains `934`
   intervals: one `1.060`-second lead, `932` internal intervals totaling
   `450.450` seconds, and one `1.273`-second tail. Every interval must be
   classified by each reviewer as reviewed silence, non-speech, overlap,
   crosstalk/VAD exclusion, or a blocking transcription gap; the machine
   ledger does not choose among those meanings.

For deterministic merge, each reviewer's `MEDIA-TIMELINE` `Review_Notes` must
include these semicolon-separated markers using the current values from the
preliminary coverage JSON:

```text
Complete_Start_to_End_Review=Yes; Media_SHA256=11692B3777914CB4BCF8DC0CFAE909878E762149AE3CA2F031A16C4EC6473A77; Gap_Register_SHA256=<current gap-register SHA-256>; Uncovered_Intervals_Reviewed=934/934; Gap_Classifications=Complete
```

The markers bind a claimed review scope; they do not independently prove that
the human review happened.

Use only these speaker labels: `Iris`, `Arnon`, `Ali`, `Multiple`,
`Unresolved`, or `Non-speech`. Confidence is `High`, `Medium`, `Low`, or
`Unknown`. Keep control IDs in R/A/Q numeric order and external facts in EF
numeric order, separated by semicolon-space. External-fact tagging is not
independent verification.

## Read-only batch validation

Validate the tracked or returned partial files without writing anything:

```powershell
python scripts/validate_iris_zoom_review_batches.py
python scripts/validate_iris_zoom_review_batches.py --reviewer-a <A.csv> --reviewer-b <B.csv>
python scripts/validate_iris_zoom_review_batches.py --reviewer-a <A.csv> --reviewer-b <B.csv> --require-complete
```

Exit `0` means structurally valid partial/complete inputs. Exit `1` means an
invalid header, ID, order, duplicate, value, date, or reviewer identity. With
`--require-complete`, exit `2` means structurally valid but incomplete. No exit
code from this command establishes truth or adjudication.

## Independence, adjudication, and completion evidence

- Store A and B separately and hash each received file before comparison.
- Verify the people behind the recorded reviewer IDs; distinct strings alone
  are not proof of independence.
- Any difference in HE, EN, speaker, confidence, basis, content class, control
  IDs, or external-fact IDs requires a third-person adjudication row.
- Ambiguous attribution stays `Unresolved`; direct quotations remain barred
  until the complete merge passes.
- Completion requires two `1,195/1,195 + MEDIA-TIMELINE` returns, `934/934`
  uncovered intervals independently classified by both reviewers, every
  disagreement adjudicated, normal merge exit `0`, deterministic merge check
  exit `0`, EXP-05/06 readiness PASS, and EXP-07 provenance binding.

## August 5 versus August 12

The August 5 supervisor package may proceed while review is incomplete only
with the machine-derived caveat, paraphrases, no direct quotations, no certain
later-turn Iris attribution, and the visible `0/1,195` or current partial
count. Priority review improves preparation but does not make a partial ledger
canonical.

August 12 is the operational target for the complete dual-review,
adjudication, deterministic merge, and provenance refresh. If staffing or
disagreements prevent completion, the gate remains blocked and the proposal
continues under the same evidence boundary. Human-review completion still does
not establish supervisor acceptance, external-fact truth, or final 100%
requirements closure.
