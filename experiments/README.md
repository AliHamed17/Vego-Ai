# Experiments

Every experiment gets:

- one registry entry in `experiments/registry.md`,
- one folder named `EXP-YYYYMMDD-short-slug`,
- an experiment card copied from `docs/templates/experiment-card.md`,
- configs or config references,
- commands,
- output path,
- result interpretation,
- limitations.

Use:

```powershell
.\scripts\new-experiment.ps1 -Slug "short-name" -Title "Readable title"
```

## Evidence phases

- `EXP-000`–`EXP-005`: baseline integrity, mechanism readiness, annotation, and the real-label gate.
- `EXP-006`–`EXP-018`: offline H-layer replay, synthetic-rule, and conformance evidence.
- `EXP-019`–`EXP-027`: preregistered thesis accuracy-evidence roadmap.

`EXP-019`–`EXP-027` are specifications and gates, not completed results. None
changes Agent 4 or the baseline. Their canonical status is in
`docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json`.
