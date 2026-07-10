# EXP-016 - Authority and Timeout Safety

Status: Offline synthetic-rule implementation complete; it grants no implementation authority.

Question: Do timeout, rejection, unauthorized-role, unresolved-override, and missing-approval cases preserve the baseline and block trusted-memory writes or correction application?

Run:

```powershell
python scripts/exp016_authority_timeout_safety.py
```

Generated, ignored outputs: `reports/generated/exp016/`.

Acceptance: timeouts end at `timed_out_parked`; the explicit actor-role/action policy is checked before case-type handling; every unauthorized action ends at `needs_adjudication`; baseline hashes match; trusted-memory writes and correction applications are both zero.

Claim boundary: all cases carry `SYNTHETIC_NOT_HUMAN`; this checks deterministic safety rules only.
