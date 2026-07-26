# EXP-039 — Cross-experiment comparability and deltas

## Question

When may two experiment results be compared directly, and what valid trade-offs
are visible within routing, topology, and runtime-mode experiments?

## Method

- Require the same cohort, metric definition, grain, evidence class, and
  invariant context.
- Permit only the declared treatment dimension to differ.
- Produce deltas for routing modes, topology alternatives, and runtime modes.
- Refuse paper-versus-current classification deltas while safe labels are zero.

## Acceptance

- Incompatible comparisons are labelled and produce no delta.
- Every valid delta includes direction, denominator, trade-off, and claim
  boundary.
- Synthetic and empirical evidence never share a headline series.

## Claim boundary

“Better” is metric-specific and conditional on guardrails. This experiment
does not select a global winner or an approved production topology.
