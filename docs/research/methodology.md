# Methodology

## Pipeline Under Study

The preserved package describes a framework with four main agents and an evaluation pipeline.

Framework agents:

- Agent 1: language advisor.
- Agent 2: domain advisor.
- Agent 3: model inspector.
- Agent 4: variability explorer.

Human-AI co-reasoning layer:

- Selective Intervention Policy: determines when AI variability decisions need human review.
- Human Review Queue: stores reviewable AI decisions with signatures and trigger reasons.
- Human Feedback Manager: validates and attaches expert feedback.
- Human Judgment Memory: stores reusable human judgments and retrieves them with explainable matching.
- Memory Advisory Layer: retrieves relevant judgments for Agent 4 patterns and emits advisory reports without changing AI classifications.

Evaluation agents:

- Agent A: language template evaluator.
- Agent B: domain guideline evaluator.
- Agent C: case scorer.
- Agent D: variability evaluator/classes.

## Domain/Diagram Settings

| Setting | Language | Domain |
| --- | --- | --- |
| `ucd_pw` | UML Use Case Diagram | ParkWise |
| `cd_pw` | UML Class Diagram | ParkWise |
| `ucd_ch` | UML Use Case Diagram | Cheers |
| `cd_ch` | UML Class Diagram | Cheers |

## Evaluation Conditions

Use the staged C0-C4 design in `evaluation-plan.md`.

| Condition | Summary | Purpose |
| --- | --- | --- |
| C0 | Original VEGO-AI | Baseline without structured human review or memory. |
| C1 | Review queue | Measures selective triggering and review workload. |
| C2 | Structured feedback | Measures whether expert decisions can be captured reproducibly. |
| C3 | Reusable memory | Measures memory construction, retrieval, and conflict handling while remaining inert. |
| C4A | Memory advisory report | Implemented M4A report where prior judgments are retrieved as advisory-only evidence. |
| C4B | Memory-assisted reclassification | Planned controlled M4B experiment where Agent 4 receives relevant prior judgments as context. |

## Measures

Quantitative:

- agreement across repeated runs,
- precision,
- recall,
- F1,
- case score distributions,
- class counts by variability type,
- review trigger rate,
- reusable-judgment yield,
- conflict/adjudication count,
- advisory strength distribution in C4A,
- memory-assisted reclassification delta in C4B.

Qualitative:

- representative examples,
- explanation quality,
- expert disagreement notes,
- visualizer usefulness,
- usefulness and limits of retrieved prior judgments.

## Method Rules

- Separate pipeline generation from evaluation.
- Preserve exact configs used for reported results.
- Record model names and API settings.
- Do not compare runs unless input data, prompts, and configs are documented.
- Treat expert labels and IRB constraints as controlled research assets.
- Keep M3 memory inert and M4A advisory-only: no Agent 4 classification change, embeddings, or visualizer changes.
- Treat C4B as a controlled experiment, not a default product behavior.
