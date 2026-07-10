# Chapter 4 — The VEGO-AI Baseline Pipeline (C0)

> Draft. Describes the original, unmodified VEGO-AI system that serves as the baseline (C0) and as the
> design artifact's host. Sources: `VEGO-AI/framework/`, `VEGO-AI/eval/`, the MAS4Models 2026 paper, and
> `docs/research/methodology.md`. Frozen at tag `official-vego-ai-baseline` (`2eeccb1`).

## 4.1 Overview

VEGO-AI is an asynchronous four-agent LLM pipeline (OpenAI `gpt-4o`) that operationalizes a conceptual distinction central to this thesis: between **substantial variability** — contextually justified, valid alternative modeling choices — and **occasional variability** — errors, misconceptions, or unintended deviations. Unlike single-reference grading tools that treat every deviation from a reference as a defect (Bian et al., 2019; Ibáñez et al., 2025), VEGO-AI reasons about whether a recurring deviation is a legitimate alternative or a mistake. The pipeline is coordinated by `framework/orchestrator.py` and runs four phases, each handled by a specialized LLM agent with a distinct concern.

This chapter describes the baseline system as it exists before any modification by this thesis. Understanding the baseline is essential for two reasons. First, the thesis artifact (Chapter 5) extends the baseline without modifying it, so the reader must know what the artifact builds upon. Second, the baseline's existing architecture contains latent, unused affordances for human involvement (§4.4) — signals and data fields that anticipate human review but are never acted upon — and it is precisely these affordances that the thesis artifact completes.

> **Figure 4.1.** Architecture of the VEGO-AI four-agent pipeline. Agent 4's latent human-review outputs (red) are produced but never acted upon. See `thesis/figures/fig-4-1-baseline-pipeline.mmd` for the Mermaid source.
>
> ```mermaid
> flowchart TB
>     subgraph inputs["Inputs"]
>         DD["Domain Description"]
>         SM["Student Models (179)"]
>     end
>     subgraph pipeline["VEGO-AI Four-Agent Pipeline"]
>         A1["Agent 1 — Language Advisor"]
>         A2["Agent 2 — Domain Advisor"]
>         A3["Agent 3 — Model Inspector"]
>         A4["Agent 4 — Variability Explorer"]
>     end
>     subgraph outputs["Agent 4 Outputs"]
>         VC["27 Variability Classifications ✓"]
>         HR["requires_human_review ✗ (unused)"]
>         CF["confidence scores ✗ (ungated)"]
>     end
>     DD --> A2; A1 --> A3; A2 --> A3; SM --> A3; A3 --> A4
>     A4 --> VC; A4 --> HR; A4 --> CF
>     A4 -- "guidelines update" --> A2
>     A3 -. "Q&A (max 10)" .-> A1; A3 -. "Q&A (max 10)" .-> A2
> ```

## 4.2 The four agents

Each agent is a prompted LLM call with structured JSON output, specialized for a distinct concern in the assessment process.

**Agent 1 — Language Advisor** (`framework/agent1_language_advisor.py`) constructs a fixed *Language Template* that enumerates the constructs of the modeling language — actors, use cases, associations, and multiplicities for UML use-case diagrams; classes, attributes, operations, relationships, and cardinalities for UML class diagrams. The template defines what *can* appear in a valid model of the given type, independent of any specific domain. Agent 1 runs once per language–diagram-type pair and its output is consumed by all subsequent agents. By separating language-level concerns into a dedicated agent, VEGO-AI ensures that domain-specific reasoning in later agents does not conflate syntactic validity with semantic correctness.

**Agent 2 — Domain Advisor** (`framework/agent2_domain_advisor.py`) takes a *Domain Description* (a natural-language specification of the problem domain, such as the description of the Cheers cinema-booking system) and produces evolving *Reference Guidelines*. Unlike a single reference model, these guidelines describe what a correct model *should contain* at the guideline level, with each guideline carrying a `mapping_certainty` score indicating how confidently the domain description implies that element. Crucially, Agent 2 records valid alternatives — for example, that "Customer" could validly be modeled as a single actor or split into "Registered Customer" and "Walk-In Customer" — so that later assessment considers multiple valid interpretations rather than insisting on a single correct answer.

**Agent 3 — Model Inspector** (`framework/agent3_model_inspector.py`) scores each student model against the reference guidelines, producing a per-guideline *compliance vector* (Satisfied, Partially-Satisfied, or Not-Satisfied) and auditing uncovered model fragments as Alternative, Domain Mistake, or Language Mistake with a severity level. Agent 3 processes each of the 179 student models individually, generating a detailed case-level assessment. The output preserves the mapping between model elements and guideline expectations, which later agents use to identify recurring patterns.

**Agent 4 — Variability Explorer** (`framework/agent4_variability_explorer.py`) aggregates the per-model results from Agent 3 into recurring *deviation patterns* — groups of models that deviate from the guidelines in the same way — and classifies each pattern as **Substantial** (valid alternative), **Occasional** (error), or **Undetermined** (ambiguous). Each classification carries a `confidence` score, a textual `justification`, a `flag_for_guidelines_update` boolean, and — critically for this thesis — a `requires_human_review` field with an accompanying `human_review_reason`. Agent 4 also implements two advanced skills that are relevant to the thesis: `probe_for_missed_alternatives` (skill 4-0), which re-examines a pattern for alternatives the initial analysis might have missed, and `resolve_with_answers` (skill 4-3), which is designed to incorporate externally provided answers. Neither skill is invoked by the orchestrator or evaluator in the baseline.

## 4.3 Coordination, Q&A, and the guideline-refinement loop

The orchestrator (`framework/orchestrator.py`) coordinates the agents through two interaction mechanisms that go beyond a simple sequential pipeline.

First, **cross-agent question-answer loops** allow downstream agents to query upstream agents for clarification. For example, Agent 3 may ask Agent 2 to clarify whether a particular domain element is required or optional, and Agent 2 responds with a targeted refinement of the relevant guideline. These Q&A rounds are capped at `MAX_QA_ROUNDS = 10` to prevent infinite loops. A key property for this thesis is that **every question is answered by another LLM agent**, never by a human; the cross-agent dialogue is entirely automated.

Second, a **guideline-refinement feedback loop** triggers when Agent 4 classifies a pattern as substantial variability and sets `flag_for_guidelines_update = true`. In this case, the orchestrator re-invokes Agent 2 to consider whether the reference guidelines should be updated to accommodate the newly recognized valid alternative. This loop operationalizes the idea that assessment is not a fixed comparison but an evolving process — yet the evolution is driven entirely by AI reasoning, with no human input or approval.

The strict separation of *language* concerns (Agent 1), *domain* concerns (Agent 2), *per-model inspection* (Agent 3), and *cross-model variability reasoning* (Agent 4) is a key architectural decision. It means that each agent's prompts and outputs can be examined independently, and it creates natural points where human oversight could be inserted — between any two agents, or at the point where Agent 4 produces its final classification. The thesis artifact (Chapter 5) exploits these natural insertion points.

## 4.4 The latent human hooks (the gap that motivates this work)

The baseline is fully automated, yet it already contains *latent, unused* affordances for human involvement — data fields, skills, and architectural patterns that anticipate a human in the loop but never activate one.

Agent 4 emits `requires_human_review` (boolean) and `human_review_reason` (text) for each variability pattern. In the current data, 11 of the 27 patterns have `requires_human_review = true`, meaning Agent 4's own assessment is that a human should examine these cases. Yet no component reads these fields; they flow into the output JSON and stop there.

Confidence values are produced for every classification but never gate anything. A pattern classified as "Substantial" with `confidence = 0.6` is treated identically to one with `confidence = 0.95` — the system makes no distinction between confident and uncertain classifications.

The two advanced skills — `probe_for_missed_alternatives` (4-0) and `resolve_with_answers` (4-3) — are implemented in the Agent 4 codebase but never invoked by the orchestrator or evaluator. Skill 4-3 is particularly relevant: it is designed to receive externally provided answers and incorporate them into the classification process, but no external answers are ever provided.

The read-only Tkinter visualizer (`vego_visualizer_delivery/`) shows AI assessments to a human user with detailed panels for each pattern's classification, justification, and evidence — but provides no channel to capture a response. The human can *see* the AI's reasoning but cannot *respond* to it.

The artifact of this thesis (Chapter 5) does not bolt a human onto an unwilling system. It *completes loops the architecture already implies*, using the existing data fields, uncertainty signals, and architectural insertion points that the baseline already provides.

### Running example: "Customer as actor" (ucd_ch, P6)

To make these latent hooks concrete, consider pattern P6 in the Cheers use-case-diagram setting. Five student models represent "Customer" as an actor who interacts directly with the system — placing orders, browsing the wine catalog, or initiating bookings. Agent 4 classifies this recurring deviation as **occasional variability** (an error) with **Medium confidence**, reasoning that "the representation of 'Customer' as an actor is consistent; however, frequently marked as an alternative indicates an error." The pattern's `flag_for_guidelines_update` is `false` and `requires_human_review` is `false`.

Yet a domain expert might reasonably disagree: modeling Customer as an actor who places orders is a defensible interpretation, not a misconception. The five students are not making the same mistake — they are making the same valid design choice. Agent 4's Medium confidence reflects genuine uncertainty, but no mechanism exists to capture or act on a human expert's judgment about this case. The confidence score flows into the JSON output and stops there. Chapter 5 (§5.2) shows how the thesis artifact routes this pattern to a human, captures the disagreement, and stores it as reusable knowledge (see also Figure 5.2).

## 4.5 Evaluation pipeline and datasets

A separate evaluation pipeline (`eval/evaluator.py`) runs in four phases (Agents A–D) that parallel and extend the main pipeline. Phase A measures template stability (whether Agent 1's language template is consistent across runs). Phase B measures guideline stability (whether Agent 2's reference guidelines converge). Phase C scores models against a junior grader's expectations. Phase D re-runs Agent 4 to produce the committed variability classifications that constitute the evaluation output.

The study spans **four settings** defined by the crossing of two factors:

| Setting | Domain | Diagram type | Student models | Variability patterns |
| --- | --- | --- | --- | --- |
| ucd_ch | Cheers (cinema booking) | Use-case diagram | varies | varies |
| ucd_pw | ParkWise (parking system) | Use-case diagram | varies | varies |
| cd_ch | Cheers (cinema booking) | Class diagram | varies | varies |
| cd_pw | ParkWise (parking system) | Class diagram | varies | varies |

Across the four settings, the pipeline processes **179 student models** aggregated into **27 recurring variability patterns** (9 classified as Substantial, 18 as Occasional, 0 as Undetermined). These committed outputs (`eval_output/<setting>/agentD_variability_classes*.json`) constitute the **C0 baseline** used throughout the evaluation.

## 4.6 Baseline outputs and the read-only contract

Each evaluation run writes per-setting JSON artifacts — language templates, domain guidelines, model compliance vectors, and variability classifications — plus an `interaction_log.jsonl` recording all cross-agent Q&A exchanges. For this thesis, the baseline is treated as **immutable**: no experiment overwrites `eval_output/`, no extension modifies Agent 1–4, and no LLM or API call is introduced into the human-judgment extension.

A critical, easily-missed point that governs the entire evaluation: the repository contains **no independent benchmark**. The author-reviewed classification files `analysis/agentD_variability_classes_*.json` are **byte-identical** to the Agent 4 output for all 27 patterns — every field, including the textual justification, matches exactly. They therefore record author *agreement* with Agent 4, not an independent label set. Using them as ground truth would be grading Agent 4 against itself. This finding, documented in §6.2, means that the only admissible ground truth for evaluating the artifact's effect on classification accuracy is **newly collected, independent expert labels** — the subject of the annotation protocol defined in Chapter 6.

The baseline's role in this thesis is to be preserved, reproduced, and compared against — never to be edited or treated as ground truth for itself. This read-only contract is enforced by the evidence-consistency guard (`scripts/check_evidence_consistency.py`), which verifies at every prompt that the baseline outputs remain unmodified, that `ai_classification_changed` remains zero, and that no extension has overwritten controlled artifacts.
