# EXP-014 - Replay Determinism

Status: Offline implementation complete; no routing policy is treated as approved.

Question: Do three replays over the same versioned fixture produce identical IDs, ordering, triage decisions, review items, and normalized hashes?

Run:

```powershell
python scripts/exp014_replay_determinism.py
```

Generated, ignored outputs: `reports/generated/exp014/`.

Acceptance: all three normalized SHA-256 values match and review-item IDs contain no duplicates.

Claim boundary: deterministic fixture behavior only; this is not empirical validation.
