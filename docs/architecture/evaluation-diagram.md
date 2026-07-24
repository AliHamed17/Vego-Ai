# VEGO-AI Evaluation Diagram - Parked Evaluation Track

Last updated: 2026-07-04 by Fable (Claude).

This is the EVALUATION view required by the 2026-07-01 supervisor meeting (notes:
`docs/research/meetings/2026-07-01-supervisor-meeting-iris.md`). Iris invoked the design-science
build-versus-evaluate distinction and directed that everything evaluation-related move OUT of the framework
diagram into this separate one, and that evaluation not proceed until the framework stabilizes. The
framework itself is in `docs/architecture/framework-diagram.md`; M4 components appear only here, never
wired into the framework diagram.

## Status: PARKED / FUTURE

No evaluation work proceeds until the framework stabilizes, and no quantitative claim is permitted until
real expert labels exist (EXP-005 gate, currently 0 generalization-safe labels).

```mermaid
flowchart TD
    STATUS[["STATUS: PARKED until the framework stabilizes - 2026-07-01 supervisor directive"]]

    subgraph DESIGN[Evaluation design: two framework versions]
        direction TB
        V0[Framework v0: no H-layer, or H-layer in silent mode - the preserved baseline]
        V1[Framework v1: H-layer enabled with human involvement]
        CRIT[Agreed evaluation criteria, e.g. error counts and agreed metrics]
        USE[Usability questionnaire, collected from v1 users only]

        V0 --> CRIT
        V1 --> CRIT
        V1 --> USE
    end

    subgraph INSTRUMENTS[Evaluation instruments - M4 lives here, not in the framework]
        direction TB
        M4A[M4A Memory Advisory - advisory only, frozen at tags]
        M4B1[M4B-1 Deterministic Memory-Informed Comparison - frozen at tags]
        EXPS[EXP-001..EXP-004 tooling - mechanism, labeling, accuracy tooling, synthetic screening]
        EXP5[EXP-005 real-label accuracy gate]
        GATE{{"Entry gate: real generalization-safe expert labels - currently 0 of 24 safe candidates, need at least 20"}}

        M4A -.-> EXPS
        M4B1 -.-> EXPS
        EXPS --> EXP5
        EXP5 --> GATE
    end

    subgraph RESOURCES[Evaluation resources - pilots local first]
        direction TB
        LOCAL[Course team]
        LECT[Second-semester lecturer]
        TA[TA teams]
        PILOT[Local pilots]
        STOCKHOLM[Stockholm University - later expansion]
        BELGIUM[Belgium colleagues - later expansion]

        LOCAL --> PILOT
        LECT --> PILOT
        TA --> PILOT
        PILOT -->|only after local pilots succeed| STOCKHOLM
        PILOT -->|only after local pilots succeed| BELGIUM
    end

    STATUS -.-> DESIGN
    STATUS -.-> INSTRUMENTS
    STATUS -.-> RESOURCES

    DESIGN <-->|criteria and questionnaire parameterize the instruments| INSTRUMENTS
    INSTRUMENTS <-->|pilots supply labelers and subjects| RESOURCES

    BOUND[["Claim boundary: NO quantitative or accuracy-improvement claim until real labels exist; synthetic and same-pattern evidence never counts as real"]]
    GATE --> BOUND
```

## Reading The Track

- Version 0 vs. Version 1 is the core comparison Iris asked for: the same framework without and with human
  involvement, compared on agreed criteria (e.g., error counts), plus a usability questionnaire answered by
  Version 1 users only.
- M4A and M4B-1 are evaluation instruments here - repositioned out of the framework per the M3-vs-M4
  distinction: judgment memory belongs to the framework (H3), advisory/comparison belongs to evaluation.
- EXP-005 remains the current evidence gate: 0 of 24 generalization-safe candidate rows are labeled; at
  least 20 valid, generalization-safe expert labels are required before any quantitative reporting (1-19 is
  pilot-only). Labels must come from real experts - never invented, auto-filled, or synthetic.
- Resources per the meeting: local course team, the second-semester lecturer, and TA teams run pilots
  first; Stockholm University and Belgium colleagues (modeling courses with hundreds of students) are
  later-stage expansions only after local pilots succeed.
