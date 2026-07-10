# EXP-017 - Verification Provenance

Status: Offline synthetic-source implementation complete; M-04 remains a decision input, not an approved default.

Question: Does deterministic-first checking trace four fixture source families in a fixed order and escalate missing, mismatched, or conflicting evidence?

Run:

```powershell
python scripts/exp017_verification_provenance.py
```

Generated, ignored outputs: `reports/generated/exp017/`.

Acceptance: each case traces baseline, guideline, review, and memory sources in that order; missing/mismatched/conflicting cases require adjudication; synthetic records never enter trusted memory.

Claim boundary: all sources carry `SYNTHETIC_NOT_HUMAN`. Semantic checking is not implemented or implied.
