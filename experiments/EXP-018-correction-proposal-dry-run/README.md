# EXP-018 - Correction-Proposal Dry Run

Status: Offline proposal-only implementation complete; no source correction is authorized or applied.

Question: Can S6-style logic produce a reproducible, reviewable diff on a disposable copy while the repository fixture remains byte-identical?

Run:

```powershell
python scripts/exp018_correction_proposal_dry_run.py
```

Generated, ignored outputs: `reports/generated/exp018/`.

Acceptance: two copied-data runs yield the same diff; the proposal records the source hash and rollback description; before/after source hashes match; `applied` remains false.

Claim boundary: the fixture is synthetic and the result is a dry-run artifact, not implementation authorization.
