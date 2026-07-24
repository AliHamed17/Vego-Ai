# EXP-013 - Event-Contract Fidelity

Status: Offline implementation complete; supervisor decisions M-02 through M-05 remain deferred.

Question: Can reconstructable E1-E15 fixtures satisfy the versioned observation contract while E3/E9 gaps remain explicit and E15 remains evaluation-only?

Run:

```powershell
python scripts/exp013_event_contract_fidelity.py
```

Generated, ignored outputs: `reports/generated/exp013/`.

Acceptance: every fixture validates; every observed or reconstructed event has a source path and SHA-256; E3/E9 are explicit gaps; E15 is parked and cannot create a framework action.

Claim boundary: offline mechanism evidence from fixtures only. It does not validate empirical performance or authorize runtime hooks.
