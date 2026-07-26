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

Release identity uses source-tree, per-source, package-tree, and artifact hashes
in the release and thesis manifests. Historical source/package build commits
remain audit context, but validation does not depend on feature-branch ancestry;
therefore a squash merge and a clean clone of `main` preserve valid provenance.
The post-merge SHA belongs in GitHub PR and tag metadata, not in a
self-invalidating tracked manifest.

Presentation artifacts that embed hardening state are deliberately excluded
from `ReleaseManifest-v3` to prevent a circular hash dependency. The
repository-generated BigUI and deployable AI Studio package are hashed by
`DeploymentSnapshot-v1`; the thesis presentation artifacts are hashed by the
thesis review package manifest.
