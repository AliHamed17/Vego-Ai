# Provenance Manifest — 29 July 2026 Iris Supervisor Call

> **Status:** Complete local machine-transcription package; human bilingual review and full diarization pending.

## Source inventory and integrity

| Role | Local path | Bytes | Last modified | SHA-256 | Intended use |
| --- | --- | --- | --- | --- | --- |
| Metadata | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\recording.conf | 127 | 2026-07-29T09:58:46.394914+03:00 | 34EAFDDF04B95D996BD59C239C6C6F916F4E5E0479F067FB8F23045B55EEB8A0 | Zoom pairing/process metadata |
| Primary audio | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\audio1589041291.m4a | 31536858 | 2026-07-29T09:58:45.438393+03:00 | D4F98015CCBB7BAEBD76B8A7259D3A9FD57C0BAA6579EB538C19EA0FFE6B7D84 | ASR source |
| Primary video | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\video1589041291.mp4 | 288382283 | 2026-07-29T09:58:45.395192+03:00 | 11692B3777914CB4BCF8DC0CFAE909878E762149AE3CA2F031A16C4EC6473A77 | Visual participant/speaker review |
| Hebrew ASR JSONL | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.jsonl | 279463 | 2026-07-30T13:46:13.515365+03:00 | 952918CA15A36AC08E481C503D469E01BC00AA1A7554C97EF1D552EA2E2EC29B | Preserved timestamped machine source |
| Hebrew SRT | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.srt | 88204 | 2026-07-30T13:46:13.558362+03:00 | CAF1F6B85D119CA47E11619A2EFBA11D5B4B7C76A208F885BB7C1AEBE304CB9E | Subtitle draft |
| Hebrew text | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.txt | 82214 | 2026-07-30T13:46:13.562470+03:00 | 40EBD629FB1A851718F3A07C5E145757A9FB51ABC67012DD95519642EF8DE6A1 | Readable ASR draft |
| ASR metadata | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.metadata.json | 530 | 2026-07-30T13:46:13.568505+03:00 | 98EA57E87E6B0F30E521E2027C49E2AC874148705A3987FE86B15FBDD233B6DE | Engine/model settings |
| Bilingual machine JSONL | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he-en.machine.jsonl | 355737 | 2026-07-30T13:48:46.832673+03:00 | 9BF59566AF1177CDC633EB58DF7A193EC4E4889A8BBE9ACD8BBBDB661534BA59 | Aligned local English translation |
| Bilingual transcript | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-bilingual-transcript.he-en.md | 424648 | 2026-07-30T14:00:59.631919+03:00 | A0222A18A839970506A5B9AC656E5B6DDF57F3A7417CDCE416AF4050D34836EE | Reader-facing segment record |
| Call report | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-call-report.md | 11853 | 2026-07-30T14:00:59.631919+03:00 | D277B4056B91235578CF54975D720338AEABEEB1A71C7AF7014B5953D015F070 | Analytical summary |
| Requirements | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-requirements-register.md | 15742 | 2026-07-30T14:00:59.632918+03:00 | 9E8D10E81DE9D1FBF92B8DF8F9686DC56B9ED8E240EE3538CD5F9AEEE3A78154 | Evidence-linked requirements |
| Actions | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-action-register.md | 11716 | 2026-07-30T14:00:59.633913+03:00 | 5C5F2F11147A78912A2F73B0BC7AB556C4716EC144F34F19A73540C2FB8A9927 | Actions/open issues |

## Transformation chain

1. Zoom M4A/MP4 retained unchanged.
2. Hebrew ASR generated locally with `faster-whisper 1.2.1`, cached `large-v3-turbo`, CPU `int8`, language `he`, beam 5, VAD enabled.
3. ASR produced 1,195 contiguous segments from `00:00:01.060` to `00:46:25.010`; detected language Hebrew, probability `1.0` under the fixed-language run.
4. Each Hebrew segment was translated locally through Ollama `qwen2.5:7b`, temperature 0, with immutable segment IDs; no recording/transcript content was uploaded to an external service.
5. Analytical reports were built from the aligned JSONLs. Terminology was corrected in paraphrases without changing raw ASR or raw machine translation.

## Speaker evidence

- The Zoom video is a stable three-person gallery: Iris (upper-left), Ali (upper-right), Arnon (lower tile).
- The mixed AAC track has identical left/right channels and no per-speaker isolation.
- Visual review confirms Iris speaking at the opening; S-0001–S-0006 are high-confidence Iris. Later attribution uses female/male grammar, conversational turns, named-address cues, and is marked medium where used analytically.
- The transcript itself does not assign names beyond S-0001–S-0006.

## Known limitations

- Hebrew and English transcript text is machine-derived and can contain lexical errors or cross-segment drift.
- Important recurring errors include study/stage, data/diet, software engineering/modeling, variability, MIMIC, Claude, LLM, Clalit, and Haifa District. Analytical paraphrases correct these using Hebrew and context.
- Speaker labels are not automatic diarization. A named attribution must retain its confidence statement.
- Statements about university policy, hospitals, datasets, data volumes, access, privacy, or deadlines are meeting statements unless independently verified elsewhere.
- The English transcript is not suitable for direct quotation until bilingual review.

## Correction policy

Never change the raw media or raw JSONL in place. Record future corrections as reviewed fields or a separate correction log with segment ID, original text, corrected text, reviewer, date, and reason. Recompute hashes after any derived-artifact update.
