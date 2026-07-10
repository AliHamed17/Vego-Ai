# July 1 Supervisor Meeting - Provenance Manifest

## Manifest status

- **Audit timestamp:** 2026-07-10 15:41:11 +03:00
- **Package integration recheck:** 2026-07-10 16:38:31 +03:00
- **Hash algorithm:** SHA-256
- **Hash command:** PowerShell `Get-FileHash -Algorithm SHA256`
- **Record state:** source inventory and transformation record; the derived notes remain unapproved until participant review
- **Privacy rule:** keep the full recording and full ASR local. Do not publish or stage them merely because their hashes appear here.
- **Immutability rule:** corrections must be stored in derived review documents. Do not rewrite the recording or raw ASR to make the meeting record agree with a later interpretation.

## Canonical source inventory

| Role | Local path | Bytes | Last-write time | SHA-256 | Use |
| --- | --- | ---: | --- | --- | --- |
| Canonical recording | `docs/video1832857678.mp4` | 65,472,232 | 2026-07-01 09:51:30.8321351 +03:00 | `23b16a5cc3c1a90402dd038f6b30dd85fd9e3df23e9deaa151eede3a94e8ab31` | Highest-authority local evidence for wording, voice, and sequence |
| ASR provenance wrapper and full Hebrew text | `docs/video1832857678.transcript.he.md` | 93,207 | 2026-07-03 23:20:09.8713993 +03:00 | `b34b0b0f28567449e443702377df61c2cae63f036cf2eef21784b0bf99a34b3c` | Documents generation method and provides searchable full text |
| Canonical timestamped Hebrew ASR | `docs/video1832857678.transcript.he.txt` | 88,406 | 2026-07-03 23:20:09.8744395 +03:00 | `5b01a08ae3a6209bb594d9fa0c74a91f970886b2054ae1820e87652ddc13f087` | Source for D1-D12 timestamps and selected appendix excerpts |
| Canonical Hebrew subtitles | `docs/video1832857678.transcript.he.srt` | 64,182 | 2026-07-03 23:20:09.8764236 +03:00 | `bac968598b7b1d7efef3d512776e4aed7d360674c316b12ba984c17b3666428e` | Segment-level playback alignment |

The recording's Windows media metadata reports a duration of `00:35:12`. File last-write time is not treated as a verified meeting end time. No calendar invitation or Zoom metadata export was inspected, so the exact start/end interval remains unresolved.

## Duplicate and legacy artifacts

| Local path | Bytes | SHA-256 | Status |
| --- | ---: | --- | --- |
| `presentations/video1832857678.mp4` | 65,472,232 | `23b16a5cc3c1a90402dd038f6b30dd85fd9e3df23e9deaa151eede3a94e8ab31` | Byte-identical duplicate of the canonical recording; not a second independent source |
| `presentations/video1832857678_transcript.txt` | 36,518 | `3716f2d878fcbedbe12618d4676172c9322bfbcf36e83aee13c5bb524ee9989e` | Earlier/legacy transcript; not used for the canonical record |
| `presentations/video1832857678_transcript.srt` | 60,005 | `99ca37722b7594153d78bcb5be7dc9a4d1a1ce6377d1230b3e6bb74a5f98f7de` | Earlier/legacy subtitles; not used for D1-D12 timestamps |

The adjacent `presentations/transcribe_hebrew.py` currently names the OpenAI Whisper `base` model, but the legacy output files do not embed their own complete generation manifest. Their exact generation configuration is therefore not asserted here.

## Source hierarchy

Use the highest available level when evidence conflicts:

1. **Recording:** `docs/video1832857678.mp4` for audible wording, speaker voice, and conversational sequence.
2. **Timestamped canonical ASR:** `.srt` for playback alignment and `.txt` for searchable segments. These are machine outputs and may contain recognition or segmentation errors.
3. **ASR Markdown wrapper:** `.md` for generation metadata and convenient full-text reading.
4. **Selected evidence appendix:** short, unchanged ASR excerpts plus unverified English paraphrases.
5. **Canonical meeting record:** English synthesis and D1-D12 traceability, pending participant confirmation.
6. **July 4-10 working documents and offline results:** responses to the meeting, never evidence of what Iris or Arnon said or approved on July 1.
7. **Follow-up decision records:** authoritative only for decisions explicitly captured and confirmed after July 1; they do not alter the historical recording.

## Transformation chain

```text
local Zoom MP4
  -> local faster-whisper large-v3-turbo ASR (Hebrew, CPU int8)
  -> full text + timestamped TXT/SRT + provenance Markdown
  -> selected Hebrew ASR excerpts (unchanged, unreviewed)
  -> English paraphrases and D1-D12 synthesis (unverified)
  -> participant correction/confirmation at follow-up (pending)
```

The canonical ASR Markdown header states that transcription used a matching extracted audio stream named `audio1832857678.m4a`. That separate `.m4a` was **not present** in the inspected repository locations on 2026-07-10, so no independent audio hash is recorded. The MP4 remains the preserved audiovisual source.

## Attribution method and confidence

- The ASR files do not contain speaker diarization.
- Speaker attribution is inferred from direct address (for example, inviting Arnon to respond), first-person statements, question/answer sequence, and the content of adjacent turns.
- `High` confidence does not mean verified identity; it means the conversational evidence strongly supports the inference.
- Short acknowledgements and overlapping turns remain `Medium` unless checked against the recording.
- No English sentence in the meeting record is presented as a verbatim translation.

## Derived artifact policy

| Artifact | SHA-256 at manifest audit | Role | Approval state |
| --- | --- | --- | --- |
| `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` | `8cd61697e8c76347efad8c9bb8f8480c402907cf68eebca9aa72a6c748ee91e2` | Canonical English meeting record and D1-D12 matrix | Machine-derived; participant confirmation pending |
| `docs/research/meetings/2026-07-01-supervisor-evidence-appendix.md` | `b9ba694d2deda707f4589b16966c73752d8ec29177f2a9fc540a41a3164cabc6` | Selected Hebrew machine-ASR evidence and unverified English paraphrases | Human review pending |
| `docs/research/meetings/2026-07-15-supervisor-decision-register.md` | `91efec50b81d1496f81358c9cd12089bb84f06fe7f44d23d6eba280957ec0547` | Single decision-register interface for M-01 through M-06 | Working; outcomes not yet recorded |
| `docs/research/meetings/2026-07-15-supervisor-action-register.md` | `a0ceaddcd344e209996a44567a2ad87265659c4f02f112ddc09be0d54a9b5ae3` | July 1 attributed actions and conditional follow-up actions | Working; M-01 confirmation pending |
| `docs/research/meetings/2026-07-15-supervisor-follow-up-annex.md` | `b358c2773a6e594a5fa8c3fdce3464f3fd63a9848b7665037fa2682995c45b17` | Chronology separation and later offline-evidence limits | Working provenance annex |
| `docs/research/meetings/2026-07-15-supervisor-executive-pre-read.md` | `49f243ce1b02d93d1caf557435676c8263c88c68f0a35ac721d91b1a348ccb15` | Authoritative Markdown source for the two-page pre-read | Working; recommendations are later work |
| `docs/research/meetings/2026-07-15-post-meeting-capture-template.md` | `076aa3e1ee943744eac39f5f791dad736331640100c397ece959484c10231cbd` | Outcome/action capture interface | Blank template; no approval implied |
| PPTX and PDF decision package outputs | See `2026-07-15-decision-package-manifest.md` | Rendered decision-support derivatives and shareable copies | Working; must preserve the three chronologies and this manifest's claim boundaries |

Derived documents may be revised when participants correct them. Source recording and ASR hashes must not be recomputed after silent source edits; any intentionally regenerated ASR must receive a new version entry, new hashes, generation configuration, and a change rationale.

## Explicit chronology exclusions

The following items did not originate as approved July 1 decisions and must be labeled as later work wherever used:

- Observer + Integrator / Option B decomposition.
- A four-source H-Verify source set.
- A maximum of two H-Verify question rounds.
- MediVARIA and any clinical study or application details.
- EXP-006 through EXP-012 outputs and any July 4-10 prototype behavior.
- Any claim about improved accuracy, generalization, or clinical performance.

## Known gaps requiring human or external verification

1. Exact Hebrew wording for every decision-critical passage.
2. Speaker attribution for short responses and any overlapping speech.
3. Participant confirmation of D1-D12 and the transcript-derived action items.
4. Prof. Arnon's surname as it should appear in the shareable package.
5. Exact scheduled meeting start/end time; media duration is known, calendar metadata is not.
6. Whether Arnon's July 15 invitation was subsequently sent and accepted.
7. Exact course presentation/submission dates discussed around `00:24:40-00:25:13`.
8. Administrative direct-track rules; the meeting explicitly deferred these to Sigal and the Graduate Studies Authority.

## Integrity recheck

Before distributing the decision package, recompute the four canonical hashes above and compare them byte-for-byte with this table. A mismatch is a stop condition: identify whether the file was moved, regenerated, or edited, then version the provenance record before relying on it.
