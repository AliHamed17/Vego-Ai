# Research Lifecycle

Use this lifecycle for each scientific claim.

1. Question: define the research question or sub-question.
2. Hypothesis or expectation: state what you expect and why.
3. Protocol: define dataset, configuration, model, evaluator, and metrics.
4. Run: execute with logged commands and environment.
5. Output: store generated files under `outputs/` or the experiment folder.
6. Interpretation: write what the result means and what it does not mean.
7. Validation: compare to expert judgment, baseline, repeated run, or sanity check.
8. Claim: connect only validated evidence to paper/thesis text.

Every experiment should have:

- an entry in `experiments/registry.md`,
- an experiment card,
- exact commands,
- config snapshot,
- output location,
- short interpretation,
- limitations and threats to validity.

