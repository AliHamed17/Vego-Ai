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

