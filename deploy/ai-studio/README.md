# VEGO-AI BigUI deployment adapter

This directory packages the repository-generated BigUI as a read-only Node service for the existing AI Studio / Google-hosted deployment.

The repository remains authoritative. The adapter serves:

- `/` — the self-contained BigUI.
- `/archive/workspace-v1` — a qualified historical description of the previous deployment.
- `/api/health`.
- `/api/v1/program`.
- `/api/v1/experiments`.
- `/api/v1/experiments/:id`.
- `/api/v1/experiments/:id/runs`.
- `/api/v1/paper-baseline`.
- `/api/v1/comparisons/eligibility`.
- `/api/v1/deployment`.

Build an immutable candidate package:

```powershell
uv run python scripts/build_ai_studio_package.py --refresh
```

Validate it without retaining a generated package:

```powershell
uv run python scripts/build_ai_studio_package.py --check
```

After the package is built from merged `main`, supply the exact 40-character revision using `--main-revision`. Production deployment requires authenticated access to the existing AI Studio project. The tracked candidate snapshot does not claim that deployment occurred.
