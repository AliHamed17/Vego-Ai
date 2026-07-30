# Iris Alignment Experiment Register

Status: **active non-production assurance program; results must be recorded
without implying supervisor approval**

This register is separate from the canonical BigUI experiment registry, which
remains intentionally bounded to `EXP-000`–`EXP-040`. The `IRIS-EXP` series
tests requirements closure, supervisor-package readiness, claim discipline,
and weekly change control. It does not change VEGO-AI production behavior or
extend the empirical accuracy evidence base.

## Execution

Run one automated protocol:

```powershell
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-01
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-03
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-04
```

Run the complete automated set:

```powershell
python scripts/validate_iris_requirements_closure.py --all
```

`IRIS-EXP-02` has a deterministic document/preflight phase, but its live
video-call rehearsal requires humans. An automated check must not mark the full
protocol complete.

## Register

| ID | Title | Status | Primary control question | Protocol | Expected evidence | Claim boundary |
| --- | --- | --- | --- | --- | --- | --- |
| IRIS-EXP-01 | Requirements traceability conformance | **PASS** on 2026-07-30: 44/44 controls and locators; audited readiness distribution preserved | Are all 19 requirements, 15 actions, and 10 open questions complete as controls and honest about unresolved work? | [`../../../experiments/IRIS-EXP-01-requirements-traceability-conformance/README.md`](../../../experiments/IRIS-EXP-01-requirements-traceability-conformance/README.md) | Per-ID findings and aggregate structural verdict | Structural coverage is not substantive completion, human transcript confirmation, or supervisor approval. |
| IRIS-EXP-02 | Supervisor presentation and decision rehearsal | **Automated preflight PASS** on 2026-07-30; live human rehearsal **NOT RUN** | Can the video-call presentation orient reviewers, expose evidence boundaries, obtain decisions, and produce an exact read-back? | [`../../../experiments/IRIS-EXP-02-supervisor-presentation-decision-rehearsal/README.md`](../../../experiments/IRIS-EXP-02-supervisor-presentation-decision-rehearsal/README.md) | Preflight, human observations, simulated read-back, and revision list | Rehearsal readiness is not a real decision or approval by Iris or Arnon. |
| IRIS-EXP-03 | Claim-language and evidence-boundary audit | **PASS** on 2026-07-30: canonical wording and high-risk boundary checks pass | Does every material supervisor-facing statement stay within its registered evidence state and wording strength? | [`../../../experiments/IRIS-EXP-03-claim-language-evidence-boundary-audit/README.md`](../../../experiments/IRIS-EXP-03-claim-language-evidence-boundary-audit/README.md) | Claim mapping and release-blocking findings | Language consistency does not independently validate evidence truth or quality. |
| IRIS-EXP-04 | Weekly commitment closure and change propagation | **Structural preflight PASS** on 2026-07-30; first real weekly cycle **NOT RUN** | Does each cycle dispose of the prior task, propagate confirmed changes, and define exactly one next task? | [`../../../experiments/IRIS-EXP-04-weekly-commitment-closure-change-propagation/README.md`](../../../experiments/IRIS-EXP-04-weekly-commitment-closure-change-propagation/README.md) | Commitment disposition and decision-propagation matrix | Process conformance is not scientific validation or inferred supervisor acceptance. |

The ignored machine-readable run record is
`reports/generated/iris_requirements_closure/latest.json`; the paired readable
record is `latest.md`.

## Status rules

- `Runnable automated protocol` means the read-only validator can execute the
  defined structural checks.
- `Document/preflight ready` means required artifacts can be inspected; it does
  not mean a live rehearsal occurred.
- `Pending`, `NOT YET EVALUABLE`, and `FAIL` remain visible and are never
  converted to `PASS` because the planned artifact exists.
- Automated findings may identify missing human evidence but may not create,
  infer, or approve that evidence.
- Raw meeting media, ASR, bilingual transcript, and source registers remain
  unchanged.

## Program acceptance boundary

The four protocols may establish that the internal closure process is complete,
traceable, presentation-ready, evidence-bounded, and consistently propagated.
They cannot support the statement that **all of Iris's substantive
requirements have been completed and approved** while open decisions,
literature execution, EXP-005 labels, medical gates, external permissions,
institutional confirmation, bilingual review, or supervisor decisions remain
unresolved.
