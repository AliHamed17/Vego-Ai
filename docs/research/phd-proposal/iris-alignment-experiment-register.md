# Iris Alignment Experiment Register

Status: **active non-production assurance program; results must be recorded
without implying supervisor approval**

This register is separate from the canonical BigUI experiment registry, which
remains intentionally bounded to `EXP-000`–`EXP-040`. The `IRIS-EXP` series
tests requirements closure, source/call coverage, supervisor-package readiness,
claim discipline, change control, explicit acceptance, and final certification.
It does not change VEGO-AI production behavior or extend the empirical accuracy
evidence base.

The proposal-only `SCI-EXP-01`–`SCI-EXP-06` labels are mapped to existing
canonical experiments in the
[`scientific-experiment-crosswalk.md`](scientific-experiment-crosswalk.md).
They are not additional registry IDs and have no independent result state.

## Execution

Run one automated protocol:

```powershell
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-01
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-03
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-04
```

Run the complete automated set:

```powershell
python scripts/validate_iris_requirements_closure.py --all --mode structure
```

Run the deeper gates only when the required human/external evidence is expected
to exist:

```powershell
python scripts/validate_iris_requirements_closure.py --all --mode readiness
python scripts/validate_iris_requirements_closure.py --all --mode closure
```

`readiness` and `closure` must return non-zero while their human, delivery,
acceptance, or submission evidence is missing. Add `--refresh` only when the
ignored `latest.md` and `latest.json` diagnostics should be regenerated.

`IRIS-EXP-02` has a deterministic document/preflight phase, but its live
video-call rehearsal requires humans. An automated check must not mark the full
protocol complete.

`IRIS-EXP-05`–`IRIS-EXP-10` add the enhanced Zoom-to-submission assurance
gates. Their protocols deliberately separate structural checks from human
bilingual review, real supervisor acceptance, delivery/access evidence, and
authorized submission. A structural run may report missing human evidence; it
must not create or infer that evidence.

## Register

| ID | Title | Status | Primary control question | Protocol | Expected evidence | Claim boundary |
| --- | --- | --- | --- | --- | --- | --- |
| IRIS-EXP-01 | Requirements traceability conformance | **PASS** on 2026-07-30: 44/44 controls and locators; audited readiness distribution preserved | Are all 19 requirements, 15 actions, and 10 open questions complete as controls and honest about unresolved work? | [`../../../experiments/IRIS-EXP-01-requirements-traceability-conformance/README.md`](../../../experiments/IRIS-EXP-01-requirements-traceability-conformance/README.md) | Per-ID findings and aggregate structural verdict | Structural coverage is not substantive completion, human transcript confirmation, or supervisor approval. |
| IRIS-EXP-02 | Supervisor presentation and decision rehearsal | **Automated/local package preflight PASS** on 2026-08-01; live timed and adversarial human rehearsals **NOT RUN** | Can the video-call presentation orient reviewers, expose evidence boundaries, obtain decisions, and produce an exact read-back? | [`../../../experiments/IRIS-EXP-02-supervisor-presentation-decision-rehearsal/README.md`](../../../experiments/IRIS-EXP-02-supervisor-presentation-decision-rehearsal/README.md) | Preflight, human observations, simulated read-back, and revision list | Rehearsal readiness is not a real decision or approval by Iris or Arnon. |
| IRIS-EXP-03 | Claim-language and evidence-boundary audit | **PASS** on 2026-07-30: canonical wording and high-risk boundary checks pass | Does every material supervisor-facing statement stay within its registered evidence state and wording strength? | [`../../../experiments/IRIS-EXP-03-claim-language-evidence-boundary-audit/README.md`](../../../experiments/IRIS-EXP-03-claim-language-evidence-boundary-audit/README.md) | Claim mapping and release-blocking findings | Language consistency does not independently validate evidence truth or quality. |
| IRIS-EXP-04 | Weekly commitment closure and change propagation | **Structural preflight PASS** on 2026-07-30; first real weekly cycle **NOT RUN** | Does each cycle dispose of the prior task, propagate confirmed changes, and define exactly one next task? | [`../../../experiments/IRIS-EXP-04-weekly-commitment-closure-change-propagation/README.md`](../../../experiments/IRIS-EXP-04-weekly-commitment-closure-change-propagation/README.md) | Commitment disposition and decision-propagation matrix | Process conformance is not scientific validation or inferred supervisor acceptance. |
| IRIS-EXP-05 | Media-to-transcript coverage | **Structural PASS on 2026-08-01; full-media human review pending** | Do immutable media, transcripts, and the disposition ledger account for all 1,195 segments and the complete 46:26.283 timeline? | [`../../../experiments/IRIS-EXP-05-media-transcript-coverage/README.md`](../../../experiments/IRIS-EXP-05-media-transcript-coverage/README.md) | Source-hash, segment identity, timeline-gap, class-coverage, and orphan-clause findings | Machine-level coverage does not establish transcription accuracy, speaker identity, or supervisor intent. |
| IRIS-EXP-06 | Bilingual meaning and speaker assurance | **Structural PASS on 2026-08-01; two independent reviews and adjudication NOT RUN** | Does human review resolve meaning and control-bearing attribution without turning uncertain supervisor-side speech into an Iris/Arnon instruction? | [`../../../experiments/IRIS-EXP-06-bilingual-meaning-speaker-assurance/README.md`](../../../experiments/IRIS-EXP-06-bilingual-meaning-speaker-assurance/README.md) | Independent reviewer returns, disagreement/adjudication log, reviewed bilingual fields, and quote-eligibility list | Reviewed meaning is not substantive approval, external-fact verification, or task completion. |
| IRIS-EXP-07 | Canonical status and provenance consistency | **Structural PASS on 2026-08-01 for the preliminary ledger; broader human truth remains pending** | Do historical snapshots, canonical current state, derived views, hashes, external facts, and revision metadata agree? | [`../../../experiments/IRIS-EXP-07-canonical-status-provenance-consistency/README.md`](../../../experiments/IRIS-EXP-07-canonical-status-provenance-consistency/README.md) | Hash/revision report, cross-view status matrix, and stale/superseded wording findings | Record consistency does not prove scientific quality or create human acceptance. |
| IRIS-EXP-08 | Presentation and delivery assurance | **Structural/local artifact PASS on 2026-08-01; human rehearsal, Ali approval, delivery, and access evidence pending; NOT SHARED** | Is the exact PPTX/PDF package complete, readable, rehearsed, approved by Ali, safely delivered, and accessible to both supervisors? | [`../../../experiments/IRIS-EXP-08-presentation-delivery-assurance/README.md`](../../../experiments/IRIS-EXP-08-presentation-delivery-assurance/README.md) | Frozen package manifest, control reachability, visual QA, rehearsal, approval, and recipient-access records | Package and delivery readiness are not meeting attendance or supervisor approval. |
| IRIS-EXP-09 | Supervisor acceptance and propagation | **Structural PASS on 2026-08-01; real supervisor outcomes pending** | Does the real meeting explicitly disposition every decision/control and propagate confirmed changes within 24 hours? | [`../../../experiments/IRIS-EXP-09-supervisor-acceptance-propagation/README.md`](../../../experiments/IRIS-EXP-09-supervisor-acceptance-propagation/README.md) | Decision outcomes, per-control disposition, written confirmation, read-back, and propagation report | A passing process audit does not mean every control was accepted; final row states remain authoritative. |
| IRIS-EXP-10 | Final closure certificate | **Structural PASS on 2026-08-01; NOT ELIGIBLE and certificate NOT ISSUED** | Can one frozen evidence set prove complete extraction, implementation, allowed final states, authoritative process verification, approval, and submission? | [`../../../experiments/IRIS-EXP-10-final-closure-certificate/README.md`](../../../experiments/IRIS-EXP-10-final-closure-certificate/README.md) | Issued certificate or explicit NOT ISSUED report, frozen manifest, per-control appendix, sign-offs, and receipt | A certificate is bounded to its evidence/revision and cannot authorize medical work or prove more than the cited evidence. |

The ignored machine-readable run record is
`reports/generated/iris_requirements_closure/latest.json`; the paired readable
record is `latest.md`.

## Status rules

- `Runnable automated protocol` means the read-only validator can execute the
  defined structural checks.
- `Document/preflight ready` means required artifacts can be inspected; it does
  not mean a live rehearsal occurred.
- `Protocol authored` means the design, metrics, dependencies, and claim
  boundary are controlled; it does not mean the protocol has run.
- `Pending`, `NOT YET EVALUABLE`, and `FAIL` remain visible and are never
  converted to `PASS` because the planned artifact exists.
- Automated findings may identify missing human evidence but may not create,
  infer, or approve that evidence.
- Raw meeting media, ASR, bilingual transcript, and source registers remain
  unchanged.

## Program acceptance boundary

The ten protocols together define the route from structural traceability to a
versioned closure certificate. They cannot support the statement that **all of
Iris's substantive requirements have been completed and approved** while open
decisions, literature execution, EXP-005 labels, medical gates, external
permissions, institutional confirmation, bilingual review, supervisor
decisions, proposal approval, or submission evidence remain unresolved.
