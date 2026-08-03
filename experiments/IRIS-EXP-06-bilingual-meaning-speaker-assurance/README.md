# IRIS-EXP-06 — Bilingual meaning and speaker assurance

## Status

- Structural state: **PASS on 2026-08-01**
- Human execution state: **not run**
- Required roles: Reviewer A, independent Hebrew-English Reviewer B, and a
  bilingual adjudicator
- Production impact: none

## Question

Does a complete independent bilingual review preserve the meaning of every
July 29 segment, resolve control-bearing speaker attribution, and prevent an
uncertain supervisor-side statement from being reported as an instruction from
Iris or Arnon?

## Inputs

- Immutable July 29 M4A audio and MP4 video listed in the provenance manifest.
- `docs/research/meetings/2026-07-29-iris-supervisor-bilingual-transcript.he-en.md`
- `docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.csv`
- `docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.json`
- The current call report and July 29 source registers.
- A reviewer-conflict and adjudication record created during execution.

## Procedure

1. Freeze and hash the machine-derived inputs before human review.
2. Reviewer A watches/listens to the complete call and independently records
   reviewed Hebrew, reviewed English, speaker, confidence, basis, content
   class, control links, and uncertainty for every segment.
3. Reviewer B repeats the complete review without seeing Reviewer A's final
   judgments or the proposed adjudication.
4. Compare the two returns field by field. Preserve both returns and record
   every translation, meaning, content-class, obligation, and speaker
   disagreement.
5. The bilingual adjudicator resolves every disagreement using the source
   media. The adjudicator cannot replace a missing independent return.
6. Obtain Iris/Arnon confirmation before assigning their names to disputed
   control-bearing statements or direct quotations. If confirmation is absent,
   retain `supervisor-side` or `unknown` and prohibit named attribution.
7. Require exact quotations to have adjudicated Hebrew, English, speaker, and
   timestamps. Keep all other supervisor material as reviewed paraphrase.
8. Add newly discovered requirements, actions, decisions, questions, risks, or
   external claims using new stable IDs. Never renumber the existing controls
   or rewrite the raw ASR.

## Outputs

- Two immutable independent reviewer returns with hashes.
- Disagreement and adjudication log.
- Human-reviewed Hebrew/English fields and speaker basis per segment.
- Newly discovered-control report and updated denominator proposal.
- Named-quotation eligibility list.

## Metrics

| Metric | Gate | Definition | Target |
| --- | --- | --- | --- |
| Human-review schema coverage | Structure | Ledger rows with bilingual, speaker-basis, reviewer, disagreement, adjudication, and status fields | `1195/1195` |
| False review completion | Structure | Machine-only rows presented as human-reviewed | `0` |
| Unfounded machine-only naming | Structure | Named segments beyond the documented opening attribution before human review | `0` |
| Reviewer A coverage | Readiness | Segments independently reviewed | `1195/1195` |
| Reviewer B coverage | Readiness | Segments independently reviewed | `1195/1195` |
| Adjudication coverage | Readiness | Recorded disagreements with a final disposition | `100%` |
| Control-bearing meaning resolution | Closure | Substantive control spans with adjudicated meaning | `100%` |
| Unsupported named attribution | Closure | Control-bearing statements assigned to Iris/Arnon without sufficient basis or confirmation | `0` |
| Eligible direct quotations | Closure | Quotes with reviewed Hebrew, English, speaker, and timestamps | `100%` of quotes used; otherwise `0` quotes |
| Orphan discovered controls | Closure | New substantive controls lacking a stable ID and owner | `0` |
| Raw-evidence rewrites | Closure | Changes to source media or machine ASR presented as raw | `0` |

## Acceptance

The structural pass establishes schema availability and conservative machine
status only. Full acceptance requires two complete independent returns,
resolution of every disagreement, and no unsupported named attribution. A segment may remain
`supervisor-side` or `unknown` only when both the uncertainty and the prohibition
on named attribution are explicit; such a segment cannot support the phrase
"Iris required". Any newly discovered control expands the closure denominator
and must pass the downstream implementation and acceptance gates.

## Dependencies

- IRIS-EXP-05 structural coverage.
- Two genuinely independent bilingual reviews.
- A bilingual adjudicator who did not produce both reviewer returns.
- Iris/Arnon confirmation for disputed named attribution when it is required.

## Claim boundary

Passing this protocol supports the reviewed meaning and permitted attribution
of the examined call. It does not mean the supervisors approved the proposal,
accepted a control, completed an action, or validated an external factual
claim.
