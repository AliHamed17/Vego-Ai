# Validity Threats

## Internal Validity

- Model behavior can change across API versions.
- Prompts or configs may drift between runs.
- Crash-resume behavior may mix old and new output states.

## Construct Validity

- "Meaningful variability" must be operationalized clearly.
- Evaluation scores may not capture all expert reasoning.
- Compliance labels may hide partial or ambiguous modeling choices.
- Human judgment must be modeled specifically as review decisions, rationales, reuse scope, and guideline suggestions, not as a vague "human in the loop."

## External Validity

- Current domains appear to be ParkWise and Cheers.
- Current model types appear to be use case diagrams and class diagrams.
- Results may not generalize to other modeling languages or domains without additional experiments.

## Conclusion Validity

- Repeated runs and confidence intervals may be needed.
- Small case counts can overstate differences.
- LLM stochasticity and rate-limit retries can affect results.
- Future reuse claims require C4B evidence; M3 proves storage/retrieval and M4A proves advisory reporting, not improved AI behavior.
- Single-reviewer EXP-005 labels are preliminary and can encode reviewer bias.
- Synthetic EXP-004 policy gains can be misread as real accuracy improvement if not separated from real-label evidence.

## Mitigations

- Record exact configs and model settings.
- Repeat key runs.
- Compare against expert annotations.
- Use experiment cards.
- Preserve outputs used for claims.
- Surface conflicting human judgments for adjudication instead of merging them silently.
- Use reviewer-2 labels or supervisor adjudication for disputed EXP-005 rows before strong quantitative claims.
- Report same-pattern, cross-setting, and generalization-safe partitions separately.
- Separate implemented mechanisms from planned PhD continuation milestones.
