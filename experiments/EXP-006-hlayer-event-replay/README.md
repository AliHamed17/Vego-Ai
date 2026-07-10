# EXP-006 - H-Listen Event Replay

Status: initial run complete (2026-07-05). Claim scope: mechanism/observability evidence only - no accuracy, generalization, or clinical claims; EXP-005 remains the accuracy gate.

Question: how many E1-E14 event records can be reconstructed from a historical baseline run, at which stages, and how does their count compare with the old review-queue item count without claiming event-level linkage?

Method: offline, read-only reconstruction of the event stream from `VEGO-AI/eval_output/<setting>/` (templates, guideline iterations, Q&A questions, compliance vectors, classifications) plus `VEGO-AI/runs/20260614-122150/human/<setting>/` review queues. No VEGO-AI code is executed or modified.

Run: `python scripts/exp006_event_replay.py` (or `.\scripts\build-hlayer-experiments.ps1` for the whole suite). Outputs (ignored): `reports/generated/exp006/{events.csv, summary.json, summary.md}`.

Initial results (run 20260614-122150, 4 settings): 481 heterogeneous reconstructed lifecycle events; early-stage share 0.187; 235 uncertainty-marked records. `11 queue items / 481 heterogeneous reconstructed lifecycle events` (~2.3%) is a count ratio only; no event-level visibility inference or linkage exists. E3 answers are not persisted, so E9 recurring ambiguity remains an explicit gap.

Iteration 009 contract result: 481 captured records plus 20 explicit gap records validate as 501 `ObservationRecord` instances with capture state and lineage. This is offline contract evidence, not proof of complete live observability.

Interpretation notes: E6 fires on 163 of 165 compliance cases because "any uncovered/potential fragment" is a loose trigger definition - severity grading is needed before E6 can drive dosage (see EXP-007). Event counts are observability metrics, not quality metrics.
