# VEGO Workbench Launcher

The VEGO workbench launcher opens the local research workspace from one command. It is intended for demos, supervisor meetings, daily review, and EXP-005 label collection.

Run from the repository root:

```powershell
.\scripts\open-vego-workbench.ps1
```

Default behavior:

- regenerates the results dashboard;
- regenerates the EXP-005 label-review package;
- opens the results dashboard;
- opens the EXP-005 "label these first" summary;
- opens the EXP-005 blind label sheet;
- opens the EXP-005 adjudication sheet and evidence verdict when present;
- opens the EXP-005 local report when present;
- opens the full results and accuracy report when present.

After real labels are entered, use `-SkipGenerate` for review so the saved CSV is not regenerated accidentally:

```powershell
.\scripts\open-vego-workbench.ps1 -SkipGenerate
```

Useful options:

```powershell
.\scripts\open-vego-workbench.ps1 -Gui
.\scripts\open-vego-workbench.ps1 -All
.\scripts\open-vego-workbench.ps1 -Health
.\scripts\open-vego-workbench.ps1 -Wiki
.\scripts\open-vego-workbench.ps1 -SkipGenerate
.\scripts\open-vego-workbench.ps1 -NoOpen
```

For a supervised one-cycle "continue to next step" workflow, use:

```powershell
.\scripts\run-codex-next-step.ps1 -RefreshWiki -RunHealth -NoOpen
```

For a structured project review only, use:

```powershell
.\scripts\run-project-review.ps1
```

Details: `docs/operations/codex-next-step-loop.md` and `docs/operations/project-review-architecture.md`.

Export the topology/flow report to HTML and PDF:

```powershell
.\scripts\export-topology-report.ps1
.\scripts\export-topology-report.ps1 -Open
```

Export the overlay version that places the human-judgment flow on top of the VEGO-AI paper architecture:

```powershell
.\scripts\export-baseline-overlay-report.ps1
.\scripts\export-baseline-overlay-report.ps1 -Open
```

Option meaning:

| Option | Purpose |
| --- | --- |
| `-Gui` | Also open the VEGO Tkinter visualizer. |
| `-All` | Build dashboard, build EXP-005 package, refresh wiki outbox, open core files, open GUI, and run health checks. |
| `-Health` | Run project, research, and dashboard health checks after opening core files. |
| `-Wiki` | Refresh Confluence outbox, dashboard snapshot, and manual sync pack. |
| `-SkipGenerate` | Open existing outputs without regenerating dashboard or EXP-005 files. |
| `-NoOpen` | Generate/check outputs without opening windows. |

If you are inside the visualizer folder, use:

```powershell
..\..\scripts\open-vego-workbench.ps1 -Gui
```

Boundary:

- does not modify Agent 4;
- does not implement M4B-2;
- does not call LLM/API services;
- does not overwrite `VEGO-AI/eval_output`;
- does not publish controlled artifacts.
