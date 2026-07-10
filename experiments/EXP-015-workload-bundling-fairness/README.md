# EXP-015 - Workload, Bundling, and Fairness

Status: Offline comparison implementation complete; neither cap configuration is an approved default.

Question: How do explicit fixture caps, composite bundling, and queue aging affect workload and deferred-item recovery?

Run:

```powershell
python scripts/exp015_workload_bundling_fairness.py
```

Generated, ignored outputs: `reports/generated/exp015/`.

Acceptance: denominators remain fixed; high-severity fixture coverage is preserved; bundle keys never cross setting/case/guideline/question boundaries; deferred recovery is reported at the next checkpoint.

Claim boundary: observed reductions apply only to this fixture. They are not a workload forecast or an approved dosage policy.
