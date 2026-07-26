# EXP-035 — Fault injection and authority safety

## Purpose

Exercise malformed, duplicate, missing, late, conflicting, timed-out, rejected,
and unauthorized inputs against the canonical contracts and human-authority
state machine.

## Acceptance

Every case preserves the baseline, creates zero unsafe trusted-memory writes,
applies zero corrections, and ends in the expected reject, park, or
adjudication state. Repeated runs must produce the same failure manifest.

## Claim boundary

This is finite offline fixture evidence, not a guarantee against every future
fault or deployment environment.
