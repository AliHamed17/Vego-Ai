# IRIS-EXP-05 — Media-to-transcript coverage

## Status

- Structural state: **PASS on 2026-08-01 for ledger/schema/source projection**
- Full protocol state: **pending raw-media and human timeline review**
- Human review state: **not complete**
- Production impact: none

## Question

Do the immutable July 29 media sources, machine transcript, preliminary
disposition ledger, and control registers account for the complete call without
missing segments, unexplained time ranges, duplicate identifiers, or orphan
substantive clauses?

## Inputs

- `docs/research/meetings/2026-07-29-iris-supervisor-provenance-manifest.md`
- `docs/research/meetings/2026-07-29-iris-supervisor-asr.he.jsonl`
- `docs/research/meetings/2026-07-29-iris-supervisor-asr.he.srt`
- `docs/research/meetings/2026-07-29-iris-supervisor-bilingual-transcript.he-en.md`
- `docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.csv`
- `docs/research/meetings/2026-07-29-iris-zoom-preliminary-disposition.json`
- `docs/research/meetings/2026-07-29-iris-supervisor-call-report.md`
- The July 29 requirements and action/question source registers.

The preliminary disposition files are machine-derived review inputs. They are
not human-adjudicated evidence.

## Procedure

1. Recompute hashes, sizes, and durations for `recording.conf`, the M4A audio,
   and the MP4 video; compare them with the provenance manifest without
   modifying the source files.
2. Require the exact ordered identifier set `S-0001` through `S-1195` in the
   Hebrew transcript, bilingual transcript, CSV ledger, and JSON ledger.
3. Compare start/end timestamps across all four representations and reject
   duplicate, reversed, out-of-order, missing, or conflicting segment spans.
4. Calculate the union of segment spans over the `46:26.283` source duration.
   Record every interval not covered by speech as reviewed silence, non-speech,
   overlap, or a blocking transcription gap; no interval is silently ignored.
5. Require every segment to have one preliminary content class and a review
   state. Require every control-bearing segment to map to at least one stable
   R/A/Q or subsequently approved control ID.
6. Review all segments classified as rationale, context, external fact, or
   risk/dependency for substantive clauses hidden by a broad range mapping.
7. Produce per-segment and timeline findings. Do not edit the media, machine
   transcript, source registers, or human-review fields.

## Outputs

- Segment identity and timestamp conformance report.
- Complete timeline coverage and unexplained-gap register.
- Orphan substantive-clause and unmapped-control findings.
- Recomputed source-hash comparison.
- A structural verdict separated from the human-review verdict.

## Metrics

| Metric | Gate | Definition | Target |
| --- | --- | --- | --- |
| Machine-source projection | Structure | Current machine-source/register hashes and rows agree with the deterministic ledger | `100%` |
| Segment identity coverage | Structure | Exact ordered IDs present in every segment representation | `1195/1195` |
| Cross-representation timestamp agreement | Structure | Segment timestamps agree across transcript and ledger inputs | `1195/1195` |
| Duplicate or missing IDs | Structure | Duplicate, skipped, or extra segment identifiers | `0` |
| Preliminary schema/class coverage | Structure | Segments with the full schema and one preliminary content class | `1195/1195` |
| Raw-source integrity | Readiness | Recomputed media/config hashes equal the manifest | `3/3` |
| Timeline disposition | Readiness | Media time is covered by a segment or an explicit human-reviewed gap class | `46:26.283 / 46:26.283` |
| Unexplained timeline gaps | Readiness | Unclassified uncovered intervals | `0` |
| Orphan substantive clauses | Closure | Substantive clauses with neither a control nor an explicit non-control rationale | `0` |

## Acceptance

Structural acceptance requires the structure metrics to meet their targets and
establishes complete machine-level ledger accounting only. Readiness additionally
requires raw-source and full-timeline review. Call-extraction closure remains
blocked until IRIS-EXP-06 completes independent bilingual and speaker review and
every substantive clause receives an adjudicated disposition.

## Dependencies

- Immutable, locally available source media.
- The complete 1,195-segment machine transcript.
- The preliminary disposition CSV and JSON.
- Stable source-register IDs and a controlled rule for adding newly discovered
  IDs without renumbering existing controls.

## Claim boundary

A passing structural result does not establish transcript accuracy, speaker
identity, translation quality, supervisor intent, or substantive requirement
completion. It supplies coverage evidence for human review only.
