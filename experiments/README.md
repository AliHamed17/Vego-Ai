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
- `EXP-019`–`EXP-029`: preregistered thesis, external-replication, effort,
  robustness, and model-evaluation roadmap.
- `EXP-030`–`EXP-036`: BigUI fidelity and human-value protocols plus offline
  architecture parity, topology, safety, and engineering experiments.

`EXP-019`–`EXP-029`, EXP-031, and EXP-032 remain specifications or gated
protocols unless an accepted manifest says otherwise. EXP-033–EXP-035 have
clone-safe offline fixture evidence only. EXP-036 publishes targets while local
machine measurements remain controlled. None changes Agent 4 or the baseline.
The program-wide status is generated into
`docs/research/bigui/experiment-catalog-snapshot-v1.json`.
