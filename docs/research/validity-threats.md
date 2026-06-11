# Validity Threats

## Internal Validity

- Model behavior can change across API versions.
- Prompts or configs may drift between runs.
- Crash-resume behavior may mix old and new output states.

## Construct Validity

- "Meaningful variability" must be operationalized clearly.
- Evaluation scores may not capture all expert reasoning.
- Compliance labels may hide partial or ambiguous modeling choices.

## External Validity

- Current domains appear to be ParkWise and Cheers.
- Current model types appear to be use case diagrams and class diagrams.
- Results may not generalize to other modeling languages or domains without additional experiments.

## Conclusion Validity

- Repeated runs and confidence intervals may be needed.
- Small case counts can overstate differences.
- LLM stochasticity and rate-limit retries can affect results.

## Mitigations

- Record exact configs and model settings.
- Repeat key runs.
- Compare against expert annotations.
- Use experiment cards.
- Preserve outputs used for claims.

