# July 29 Zoom Human-Review Merge

Status: **interface ready; Reviewer A `0/1,195` segments plus `0/1` full-media record, Reviewer B `0/1,195` segments plus `0/1` full-media record, adjudicated ledger not created**

The preliminary CSV/JSON remain immutable machine-only inputs. Human review is
captured separately in `2026-07-29-iris-zoom-reviewer-a.csv` and
`2026-07-29-iris-zoom-reviewer-b.csv`. Each return requires `S-0001` through
`S-1195` as `Segment` records plus one `MEDIA-TIMELINE` / `Full-media` record
whose notes identify the complete-video review evidence.

Run the merge-interface check without writing outputs:

```powershell
python scripts/build_iris_zoom_adjudicated_ledger.py --check
```

The command returns success for a valid pending interface only when the
adjudicated outputs are absent. A normal build remains blocked until both
reviewers are complete and distinct. Fields that differ between reviewers must
have a completed row in `2026-07-29-iris-zoom-adjudication.csv`; the adjudicator
must be a third person. Only then does the script emit the separate
`2026-07-29-iris-zoom-adjudicated-ledger.csv` and `.json` artifacts.

Template existence, a successful pending check, or copied machine text is not
human review. Never enter invented identities, dates, translations, speaker
labels, full-media evidence, or adjudication decisions.
