# Workspace Diagram

This diagram shows how the VEGO-AI PhD research workspace is organized across source, research method, experiments, outputs, writing, and shared agent memory.

```mermaid
flowchart TD
    User[Researcher] --> Memory[docs/agent-memory<br/>Shared Codex and Claude memory]
    Memory --> AgentWork[AI-assisted work sessions]
    AgentWork --> Charter[PROJECT_CHARTER.md<br/>Purpose and boundaries]
    AgentWork --> Architecture[docs/architecture<br/>Project map and reproducibility rules]
    AgentWork --> Research[docs/research<br/>Questions, method, ethics, validity]

    Research --> Registry[experiments/registry.md]
    Registry --> Experiment[experiments/EXP-*<br/>Experiment cards and run records]

    Experiment --> Source[VEGO-AI/<br/>Preserved runnable source package]
    Experiment --> FutureSource[src/<br/>Future cleaned reusable package]
    Experiment --> Data[data/<br/>Controlled data zones]

    Source --> Framework[VEGO-AI/framework<br/>Multi-agent pipeline]
    Source --> Eval[VEGO-AI/eval<br/>Evaluation pipeline]
    Source --> Inputs[VEGO-AI/inputs<br/>Tracked lightweight inputs]
    Source --> Visualizer[VEGO-AI/vego_visualizer_delivery<br/>Visualizer code and config]

    Data --> Outputs[outputs/<br/>Generated results and figures]
    Framework --> Outputs
    Eval --> Outputs
    Visualizer --> Reports[reports/<br/>Curated reports]
    Outputs --> Reports

    Reports --> Evidence[papers and thesis evidence]
    Evidence --> Papers[papers/<br/>Manuscripts]
    Evidence --> Thesis[thesis/<br/>Chapters and defense material]

    Tests[tests/<br/>Regression and reproducibility tests] --> Source
    Scripts[scripts/<br/>Memory, health, experiment automation] --> Memory
    Scripts --> Experiment
    Scripts --> Tests

    GitHub[(Private GitHub repo<br/>AliHamed17/Vego-Ai)] --> Memory
    GitHub --> Architecture
    GitHub --> Source
    GitHub --> Research
    GitHub --> Registry

    Sensitive[Ignored pending audit<br/>PDFs, archives, models, analysis, eval outputs] -. not published .-> GitHub
```

## Reading The Flow

- Start each AI-assisted session from `docs/agent-memory/`, then use the project charter and architecture docs to choose the right workspace area.
- Keep research questions and experiment protocols outside the preserved `VEGO-AI/` source package.
- Connect source changes and generated outputs back to experiment records before using them as paper or thesis evidence.
- Keep sensitive or bulky artifacts ignored until the data, provenance, and IRB audit is complete.
