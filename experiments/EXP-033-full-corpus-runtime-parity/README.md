# EXP-033 — Full-corpus runtime parity

## Purpose

Run legacy, unified, and parity modes from identical immutable M1–M4B-1
artifacts. Compare normalized review identities, signatures, states, memory
matches, advice, classifications, escalation flags, safety fields, and counts.

## Acceptance

- Three repetitions produce identical normalized outputs.
- Legacy and unified outputs have zero semantic differences.
- Parity publishes the legacy result on every injected mismatch.
- Baseline outputs remain byte-identical.
- Controlled aggregates contain no raw student, reviewer, or transcript data.

## Claim boundary

Passing establishes mechanism-level compatibility only, never accuracy.
