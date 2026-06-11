# Methodology

## Pipeline Under Study

The preserved package describes a framework with four main agents and an evaluation pipeline.

Framework agents:

- Agent 1: language advisor.
- Agent 2: domain advisor.
- Agent 3: model inspector.
- Agent 4: variability explorer.

Evaluation agents:

- Agent A: language template evaluator.
- Agent B: domain guideline evaluator.
- Agent C: case scorer.
- Agent D: variability evaluator/classes.

## Experimental Conditions

| Setting | Language | Domain |
| --- | --- | --- |
| `ucd_pw` | UML Use Case Diagram | ParkWise |
| `cd_pw` | UML Class Diagram | ParkWise |
| `ucd_ch` | UML Use Case Diagram | Cheers |
| `cd_ch` | UML Class Diagram | Cheers |

## Measures

Quantitative:

- agreement across repeated runs,
- precision,
- recall,
- F1,
- case score distributions,
- class counts by variability type.

Qualitative:

- representative examples,
- explanation quality,
- expert disagreement notes,
- visualizer usefulness.

## Method Rules

- Separate pipeline generation from evaluation.
- Preserve exact configs used for reported results.
- Record model names and API settings.
- Do not compare runs unless input data, prompts, and configs are documented.
- Treat expert labels and IRB constraints as controlled research assets.

