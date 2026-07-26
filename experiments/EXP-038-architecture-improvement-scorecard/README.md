# EXP-038 — Architecture improvement scorecard

## Question

Which architectural properties added after the paper baseline are demonstrated
by accepted mechanism, parity, replay, and safety evidence?

## Method

Use a multidimensional scorecard rather than a weighted total. The scorecard
separates:

- implemented human-judgment capabilities;
- semantic parity and deterministic replay;
- baseline preservation and fault containment;
- classification validity and human effort, which remain unmeasured.

## Acceptance

- Every scorecard cell traces to an accepted metric or is explicitly null.
- No mixed-scale global score is calculated.
- Classification and effort cells remain null until their human evidence gates
  open.

## Claim boundary

The scorecard can demonstrate capability and reliability extension. It cannot
establish classification accuracy, generalization, or reduced effort.
