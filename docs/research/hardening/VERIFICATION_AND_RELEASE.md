# Verification and Release Runbook

## Entry points

| Command | Scope | Default behavior |
| --- | --- | --- |
| `scripts/verify-source.ps1 -Check` | Clone-safe dependencies, contracts, tests, security, documents, browsers | Read-only with temporary audit files |
| `scripts/verify-controlled.ps1 -Check` | Ignored local baseline/evidence, 27-row parity, EXP gates | Read-only; conformance rerun uses temporary storage |
| `scripts/verify-controlled.ps1 -Refresh` | Same gates plus refreshed ignored diagnostics | Explicitly write-capable |
| `scripts/verify-release.ps1 -Check` | Source + controlled + clean-tree publication gate | Requires clean tracked worktree |

## Mandatory release evidence

- Python 3.10–3.13 CI matrix.
- Complete VEGO-AI, research-script, and offline H-layer test groups.
- Zero required deselections and zero schema-validation skips.
- Baseline Agent 4 byte and semantic lock.
- Legacy/unified parity across 27 comparison rows.
- Zero M4B-1 classification changes.
- EXP-005 at 0/24 and EXP-012 not computable.
- Dependency, secret/history, static-analysis, privacy, binary, and archive gates.
- Deterministic thesis artifacts and offline browser checks.
- Independent human approval and green aggregate `merge-gate`.

## Merge rule

The PR remains open if any gate fails, if GitHub cannot enforce the required
rule, or if no separate collaborator has approved it. Administrators are not a
bypass. The intended final operation is a squash merge followed by tag
`research-state-unified-hardening-v1`.

Release identity uses source/package/artifact hashes in
`ReleaseManifest-v3`. The post-merge SHA belongs in GitHub PR and tag metadata,
not in a self-invalidating tracked manifest.
