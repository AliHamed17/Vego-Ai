# IRIS-EXP-02 — Supervisor presentation and decision rehearsal

## Status

- Document/preflight state: **PASS on 2026-07-30**
- Live rehearsal state: **pending; not run**
- Human participants required: presenter, Iris-role reviewer, Arnon-role
  reviewer, and decision recorder
- Production impact: none

An automated document check cannot substitute for the live rehearsal or for
Iris and Arnon's real decisions.

Automated phase:

```powershell
python scripts/validate_iris_requirements_closure.py --experiment IRIS-EXP-02
```

## Question

Can the supervisor video-call presentation orient Iris and Arnon quickly,
represent what was requested in the July 29 call without overstatement, obtain
answerable decisions, and finish with an unambiguous read-back of owners,
evidence, and next work?

## Inputs

- `docs/research/meetings/2026-08-05-supervisor-pre-read.md`
- `docs/research/meetings/2026-08-05-supervisor-presentation-checklist.md`
- `docs/research/phd-proposal/iris-requirements-closure-audit.md`
- `docs/research/phd-proposal/2026-08-05-rq-decision-pack.md`
- `docs/research/phd-proposal/proposal-v0.1.md`
- `docs/research/phd-proposal/master-traceability-register.md`
- `docs/research/phd-proposal/claim-register.md`
- `docs/research/phd-proposal/decision-change-log.md`
- `docs/templates/weekly-supervisor-pre-read.md`
- `docs/templates/supervisor-decision-change-log.md`
- The candidate presentation, presenter notes, and appendix when available.

## Procedure

### A. Document and video-call preflight

1. Confirm the meeting time, timezone, attendees, video-call link, screen-share
   permission, and a locally accessible fallback copy.
2. Verify that the main presentation contains one umbrella RQ, exactly three
   subquestions, the three-study mapping, Plan A/Plan B, the evidence boundary,
   current blockers, and explicit decisions requested.
3. Verify that every July 29 requirement is presented directly or reachable in
   a clearly labelled traceability appendix; do not overload the main
   presentation with the full register.
4. Verify that no restricted medical data, unreviewed direct transcript quote,
   private credential, or unsupported performance/partner/deadline claim is
   visible.
5. Confirm that each decision prompt offers `Accepted`, `Accepted with
   changes`, `Rejected`, or `Deferred` and has a recorder field.

### B. Live human rehearsal

1. Run the decision-focused presentation segment inside a simulated video call
   while sharing the same artifact planned for the real meeting.
2. Have the Iris-role and Arnon-role reviewers interrupt with at least one
   wording correction, one evidence challenge, and one deferred decision.
3. Require the presenter to distinguish implemented artifacts from completed
   research outcomes and to state the `0/24` EXP-005 and `0/6` medical-gate
   boundaries.
4. Record every simulated outcome, correction, owner, due date, acceptance
   check, and affected artifact without editing the raw July 29 evidence.
5. Read back the decisions and exactly one proposed next weekly commitment.
6. Debrief all missed prompts, unclear wording, inaccessible links, timing
   overruns, or changes that were not propagated.

The rehearsal record must be labelled simulated and must never be copied into
the real decision log as supervisor approval.

## Outputs

- Completed presentation/preflight checklist.
- Human rehearsal observation sheet and timing notes.
- List of unclear or over-strength statements and their proposed corrections.
- Simulated decision read-back.
- Presentation revision list, separated into mandatory blockers and optional
  improvements.

## Metrics

| Metric | Definition | Target |
| --- | --- | --- |
| July 29 requirement reachability | Requirements shown or linked in the traceability appendix | `19/19` |
| Action reachability | Actions linked from presentation/pre-read controls | `15/15` |
| Open-question routing | Questions tied to a decision owner or explicit later gate | `10/10` |
| Research architecture fidelity | One umbrella RQ, three SQs, three mapped studies | Exact match |
| Required decision-prompt coverage | All decisions requested by the pre-read are answerable and recordable | `10/10` |
| Evidence-boundary prompts | EXP-005, medical, literature, transcript, partner, and deadline limitations visible | `6/6` |
| Broken or inaccessible presentation links | Link failures during the preflight/rehearsal | `0` |
| Unsupported/direct-quote findings | Unsupported positive claims or unreviewed direct transcript quotations | `0` |
| Decision read-back completeness | Outcome, exact wording, owner, due/gate, evidence, and confirmation state captured | `100%` |
| Single-task closure | Exactly one next weekly commitment with definition of done | `1` |

Timing is recorded descriptively during the first rehearsal. It is not given a
passing threshold until the supervisors' preferred presentation length is
confirmed.

## Acceptance

The document/preflight phase passes only when all non-timing targets pass. The
experiment as a whole remains pending until humans complete the live rehearsal,
all mandatory findings are resolved, and a second preflight passes. A real
supervisor outcome is never inferred from the rehearsal.

## Dependencies

- A frozen candidate presentation and appendix.
- A working video-call/screen-share environment and fallback copy.
- At least three human rehearsal participants in addition to the presenter, or
  a documented reason for combining reviewer and recorder roles.
- Current claim register, traceability register, and decision template.
- Human bilingual review for any planned exact quotation or speaker
  attribution.

## Claim boundary

Passing this protocol supports presentation readiness and decision-capture
usability only. It does not mean Iris or Arnon attended, accepted the wording,
approved Plan A/Plan B, closed an open question, or found the scientific case
adequate.
