# July 15 H-Layer Supervisor Demo Runbook

Status: **PROVISIONAL OFFLINE DEMO.** This runbook demonstrates interaction design and deterministic safety checks. It does not create trusted memory, apply a correction, modify a VEGO-AI prompt, validate a policy, or support an accuracy/generalization claim.

Audience: Iris and Arnon  
Timebox: 20-minute walkthrough + 20-minute decision discussion  
Output: isolated demo records only; adjudication candidates remain pending

## Preflight

Run from `C:\Users\ahamed\vego-ai` before the meeting:

```powershell
git status --short --branch
python scripts/check_evidence_consistency.py
python scripts/validate_hlayer_offline.py
python scripts/validate_hlayer_program.py
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --test-conflict
```

Create a session-specific directory outside tracked source paths:

```powershell
$demoDir = Join-Path $env:TEMP "vego-hlayer-supervisor-demo-20260715"
New-Item -ItemType Directory -Force -Path $demoDir | Out-Null
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --mock-session --output-dir $demoDir
```

The mock session must leave ordinary feedback and adjudication files in the repository unchanged. Inspect the temporary output and confirm every record has a demo/synthetic origin, an explicit state, provenance, and `trusted_memory_eligible = false`.

## Walkthrough

### 0:00–2:00 — Boundary and objective

- State that the framework is offline-only and the decisions M-02 through M-05 are open.
- State that the replay suite has six experiments and iteration 012 is a neutral reliability snapshot.
- State that EXP-005 has zero supplied labels and EXP-012 is not computable.
- Ask the supervisors to evaluate the interaction flow, authority model, and evidence presentation—not quality performance.

### 2:00–5:00 — Observation and workload

Run:

```powershell
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run
```

Explain that the counts are replay-derived mechanism data. Bundling is an observed modest reduction; no workload default or forecast is approved.

### 5:00–13:00 — Isolated interactive review

Run:

```powershell
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --interactive --output-dir $demoDir
```

Use `cd_ch`. Select one template item and one guideline/decision item. For each item:

1. Read the displayed source event IDs and evidence details.
2. Enter a valid `Approve` or `Reject` decision and a nonblank rationale.
3. For the template example, first enter an unmatched brace to trigger the deterministic syntax check, then revise it.
4. For the policy-conflict example, choose not to revise and request escalation.
5. Show that the escalated record is written only as `needs_adjudication`, never as ordinary feedback/trusted memory.

Do not describe the low-certainty guideline heuristic as a domain truth. It is a provisional demo signal unless an explicit core/invariant source field exists.

### 13:00–17:00 — Read the captured records

Open the session output and show:

- stable record identifier;
- setting, subject, decision, rationale, and selected evidence;
- source/run provenance;
- verification state;
- origin (`SUPERVISOR_DEMO` or `SYNTHETIC_NOT_HUMAN`);
- `trusted_memory_eligible = false`;
- adjudication candidate separated from ordinary feedback.

Explain that a future trusted-memory record needs S5 verification or recorded supervisor adjudication, confirmed scope/reusability, and the M-05 implementation gate.

### 17:00–20:00 — Decision bridge

End with the decision read-back:

- M-02: agent decomposition;
- M-03: observation/routing/dosage and cap policy;
- M-04: approved deterministic source set and round bound;
- M-05: authority, timeout behavior, reviewer roles, and whether an allowed-touch implementation process may begin.

Do not end with a generic thank-you slide or claim. End with owners, dates, deferred items, and the exact record that will be updated.

## Discussion Capture (20 minutes)

For each decision, record exactly one outcome: `Accepted`, `Accepted with changes`, `Rejected`, or `Deferred`. Capture rationale, constraint, approver, owner, due date, and affected artifacts. Blank or ambiguous means `Deferred`.

Within 24 hours, update the decision/action registers and corrected minutes. Regenerate outputs only after the recorded outcomes are reviewed. No deliverable becomes `Approved` merely because it was demonstrated.

## Abort Conditions

Stop the demo and preserve baseline behavior if:

- a validator fails;
- the output directory points inside `VEGO-AI/` or a protected source path;
- a record lacks decision, rationale, state, origin, or provenance;
- an escalated override appears in ordinary feedback memory;
- any step attempts an LLM/API call, prompt injection, correction application, or pipeline retrigger;
- the presentation starts implying accuracy, transfer, or clinical performance.
