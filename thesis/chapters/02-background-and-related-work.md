# Chapter 2 — Background and Related Work

> Draft. **All citations are real**, taken from the VEGO-AI (MAS4Models 2026) paper's own bibliography and
> the curated resource pack (`literature/hitl-resource-pack/bibliography.bib`). Full entries are listed in
> §2.9. Organized by the taxonomy in `docs/research/literature-review-taxonomy.md`. No accuracy claim.

## 2.1 Review lens and scope

This chapter positions the thesis contribution — *human judgment that is selectively triggered, structurally captured, and stored as reusable knowledge for future variability interpretation* — against prior work. The review spans six areas: LLM-assisted domain modeling, AI-assisted model assessment, the meaning of *variability* in models, human–AI collaboration patterns, explainability and reusable expert knowledge, and design-science methodology.

For each area, the relevant question is not only *what the system does* but *what role it assigns to human judgment* and *whether that judgment is reused*. This lens is intentional: the thesis does not claim to introduce human involvement into AI systems for the first time, but rather to show that the specific combination of selective triggering, structured capture, provenance-tracked storage, and cross-case reuse is absent from prior work in the model-assessment context. The review concludes with a gap synthesis (§2.8) that positions the contribution.

## 2.2 LLM-assisted domain modeling and generation

A growing body of work applies large language models to produce or assist conceptual models, establishing the technical context in which VEGO-AI operates. Cámara et al. (2023) report on generative AI in modeling tasks with ChatGPT and UML, finding that while LLMs can produce syntactically plausible diagrams, the semantic quality varies considerably and human verification remains essential. Chaaben et al. (2024) study the utility of domain-modeling assistance with LLMs and reach a similar conclusion: human modelers are still necessary to repair inaccuracies, particularly for domain-specific constraints that the LLM does not encode.

On the generation side, Calamo et al. (2025) assess LLM suitability for generating UML class diagrams as conceptual models, reporting that generated diagrams often capture surface-level structure but miss deeper domain relationships. Bragilovski et al. (2025) derive domain models from user stories, demonstrating that LLMs can bridge the requirements-to-model gap but introducing new questions about how to validate the resulting models. Rajbhoj et al. (2025, LLM4Model) author requirements-specification models with LLM assistance, and Ferrari et al. (2024) generate UML sequence diagrams from requirements.

At the architecture level, multi-agent approaches are emerging as a way to distribute modeling concerns across specialized roles. Dam (2025) proposes multi-agentic AI for automated software design and modeling, arguing that single-agent approaches cannot handle the combinatorial complexity of real-world design. Sami et al. (2024) experiment with multi-agent software development, and Jin et al. (2024) survey the broader shift from monolithic LLMs to LLM-based agent systems in software engineering.

Three patterns emerge from this body of work. First, LLMs are increasingly capable of producing models, but human judgment remains necessary for semantic validation. Second, multi-agent architectures are gaining traction as a way to manage modeling complexity. Third, none of these systems provide a mechanism for *capturing and reusing* the human judgments that arise during validation — the expert corrects the model, but the correction is consumed once and not stored for similar future cases. VEGO-AI belongs to this multi-agent lineage but targets *assessment and variability interpretation* rather than generation, and — unlike these systems — it operationalizes a reusable human-judgment loop.

## 2.3 AI-assisted model assessment and grading

A second line of research automates the grading or criticism of student and domain models. This is the most directly relevant technical context for VEGO-AI, because the thesis artifact operates within an assessment pipeline rather than a generation pipeline.

Early work by Auxepaules et al. (2008) matches class diagrams in a learning environment, establishing the pattern of comparing student submissions against a reference model. Bian et al. (2019, 2020) automate class-diagram grading and then critically examine whether such automated grading is effective, finding that while structural matching can identify surface-level deviations, it struggles with semantically equivalent alternatives. Singh et al. (2022) detect mistakes in a domain model, and Hamann et al. (2024) build an interoperable automated assessment system for CS education, focusing on architectural integration across assessment tools.

More recently, LLM-as-grader studies have produced cautionary findings about the limits of fully automated assessment. Bouali et al. (2025) compare LLM-generated scores with teaching-assistant grades and find significant discrepancies, particularly for models that deviate from the expected structure in valid ways. Ibáñez et al. (2025) ask whether multimodal LLMs can grade UML class diagrams like an expert and report systematic accuracy limits, especially for nuanced quality judgments that require domain context. Chen et al. (2024) propose embedding-based automated assessment of domain models, achieving structural similarity scores but not interpretive classification. Ahmed et al. (2025, MCeT) evaluate behavioral-model correctness with LLMs, focusing on state machines and sequence diagrams.

These works share a common limitation: a single-reference, error-centric stance in which deviation from the reference is treated as defect. This is appropriate when the reference is authoritative and deviations are unambiguously wrong, but it breaks down precisely where domain-model assessment is most interesting — when a student's deviation represents a valid alternative interpretation. VEGO-AI's substantial-vs-occasional distinction is a direct response to this limitation, and this thesis adds the missing capability: capturing and reusing the human judgment that decides which deviations are valid.

## 2.4 Variability in models

The term *variability* has a rich software-engineering heritage that grounds VEGO-AI's usage and distinguishes it from generic notions of "difference" or "error."

In software product lines, variability refers to the planned, managed ability of a system to differ across configurations. Pohl et al. (2005) establish the foundational framework for software-product-line engineering, defining variability as a first-class design concern. Metzger and Pohl (2014) survey achievements and challenges in variability management, noting that the field has matured from ad-hoc difference management to systematic, tool-supported variability modeling. Systematic literature reviews by Galster et al. (2013), Pol'la et al. (2021), and El-Sharkawy et al. (2019) survey variability and its metrics across software systems. Rosa et al. (2017) extend variability modeling to business processes, and Ananieva et al. (2022) propose a conceptual model unifying variability in space (across product variants) and time (across evolution).

VEGO-AI narrows this broad concept to **assessment-time variability** — distinguishing valid alternatives from errors in student domain models at the point of evaluation. This is a different concern from product-line variability management: the question is not "how should we plan for variation" but "is this observed variation a valid interpretation or a mistake." The product-line-centric treatments do not address this interpretive, judgment-laden aspect of variability. It is precisely this interpretive nature that makes human judgment essential: an automated tool can detect that a deviation exists, but deciding whether it represents a valid alternative requires contextual reasoning that draws on domain expertise, pedagogical goals, and precedent — the kind of reasoning that, once made, should be preserved for reuse.

## 2.5 Human–AI collaboration: in-the-loop, on-the-loop, and co-reasoning

The most directly relevant work for the thesis contribution concerns where the human sits relative to the AI system and what role their input plays. The literature distinguishes several patterns, which this section organizes into a progression from supervisory to collaborative.

**Human-in-the-loop (HITL)** systems place the human as a necessary participant in each decision cycle. The human labels, corrects, or approves before the system proceeds. Mosqueira-Rey et al. (2023) provide a comprehensive survey of HITL machine learning, identifying patterns such as active learning, interactive labeling, and human-guided training. The defining characteristic is that the human's input is consumed immediately — it improves the current model iteration but is not stored as a separable, retrievable knowledge asset.

**Human-on-the-loop (HOTL)** systems allow the AI to operate autonomously by default, with the human monitoring and intervening by exception. The NIST AI Risk Management Framework (2023) frames human oversight in these terms, emphasizing accountable use and the importance of meaningful human control. This pattern reduces the human's workload but retains the same transience problem: when the human does intervene, their judgment typically corrects the current case without being preserved for future similar cases.

**Human–AI co-reasoning** is a newer, less standardized concept in which both the human and the AI contribute reasoning that remains visible, attributable, and potentially reusable. The term implies a partnership in which neither party's contribution is consumed and discarded: the AI's evidence and the human's judgment coexist as inspectable, persistent artifacts.

In the domain-modeling context, Silva et al. (2025) explicitly propose *human-in-the-loop LLM-enabled domain modeling*, establishing the most directly relevant precedent. Ali et al. (2024) study how LLMs are used for conceptual modeling, examining interaction behavior and user perception. Klievtsova et al. (2023) investigate conversational and iterative process modeling, where the human and AI take turns refining a model. At the earliest end of the timeline, Tselonis et al. (2005) frame diagram matching as *human–computer collaborative assessment*, anticipating the idea that assessment is a joint activity.

Beyond the modeling literature, Amershi et al. (2019) provide widely-adopted *Guidelines for Human–AI Interaction* that establish principles for when and how AI systems should involve humans — principles that inform the selective intervention policy of this thesis. The guidelines emphasize making the AI's uncertainty visible, supporting efficient correction, and learning from human input — but they do not prescribe how that input should be stored and reused across cases.

The thesis positions its contribution between the on-the-loop and co-reasoning patterns. It is on-the-loop in that the Selective Intervention Policy escalates by exception rather than reviewing every case. It is co-reasoning in that the human's rationale becomes durable, retrievable evidence that informs later assessments — not a correction that is consumed and forgotten. The distinctive move relative to the surveyed literature is **persistence and reuse**: a judgment about, say, "Customer as an actor" is not discarded after one case but stored with scope, provenance, and conflict status, and surfaced when a similar pattern recurs in a different setting or model.

## 2.6 Explainability, expert feedback, and reusable knowledge

VEGO-AI already exposes evidence, justification, and confidence to its users, placing it within the explainable AI tradition. The relevant external anchor is Silva Mercado (2024) on *AI-assisted domain modeling explainability and traceability*, which motivates the transparent, embedding-free `match_reasons` of the judgment memory (M3) — the idea that reuse decisions should be as inspectable as the original AI decisions.

The crucial gap across the surveyed assessment and collaboration work is that human feedback, when collected, is consumed once and discarded. In HITL machine learning, annotator labels feed into the training loop and are absorbed into model weights — the individual judgment is no longer retrievable as a separable knowledge item. In interactive modeling tools, the user's correction fixes the current model but does not create a persistent record that can be retrieved when a similar situation arises later. In assessment systems, the grader's override resolves a single case but is not indexed by pattern, domain, or diagram type for future lookup.

This thesis's Human Judgment Memory (M3) is precisely such a store: a structured, provenance-tracked collection of expert judgments that can be queried by domain, diagram type, guideline, and keyword overlap, with human-readable match reasons explaining why a past judgment is relevant to a current case. The store does not rely on embeddings or LLM calls — it uses deterministic, explainable matching — and it surfaces conflicts rather than auto-resolving them. This design choice reflects a deliberate stance: the reuse mechanism should be as transparent and auditable as the original AI decision, so that the human can trust and verify the advice rather than accepting it as an opaque recommendation.

## 2.7 Design-science methodology

The work is framed as design science, following the established tradition of building and evaluating IT artifacts to solve identified field problems. Hevner et al. (2004) define the foundational framework for design-science research in information systems, establishing seven guidelines including relevance, design as an artifact, design evaluation, and research contributions. Peffers et al. (2007) refine this into a structured process model — problem identification, objectives, design and development, demonstration, evaluation, and communication — that this thesis follows. Gregor and Hevner (2013) further classify design-science contributions into levels of maturity, from specific instantiations to generalizable design theories.

This thesis operates at the *situated implementation* level: the artifact (the reusable human-judgment layer) is built and demonstrated within a specific system (VEGO-AI), and the evaluation methodology is designed to establish both mechanism validity (the artifact works as intended) and empirical effect (the artifact changes assessment quality). The design-science framing is important because it legitimizes the mechanism contribution even before empirical results are available: a well-designed, well-evaluated artifact that closes a real gap is a research contribution in its own right, independent of whether the eventual accuracy measurements show improvement (Hevner et al., 2004).

The contribution types are kept distinct throughout the thesis: a literature-review contribution (the taxonomy and gap analysis of §2.1–§2.8), a design contribution (the co-reasoning architecture, feedback schema, and judgment-memory concept of Chapter 5), a technical prototype (the implemented and tested M1–M4B-1 pipeline of Chapter 5), and a planned empirical contribution (the leakage-aware evaluation of Chapter 6). This separation follows Gregor and Hevner's (2013) recommendation to be explicit about which knowledge types a design-science study contributes.

## 2.8 Gap and positioning

Synthesizing the above six areas, four interrelated gaps emerge that together define the space this thesis occupies:

1. **One-way explanation.** Explanation is mature but mostly flows AI→human. Systems explain their decisions to people (evidence, confidence, justification) but rarely ingest *why* a human disagrees in a structured, reusable form.

2. **Transient judgment.** Human judgment is treated as a transient correction — a label, an override, a free-text comment — that resolves one case. It is not stored as durable, indexed knowledge that can be retrieved for similar future cases.

3. **Generation over assessment.** Collaboration is studied extensively for model *generation* and generic *grading*, but not for *interpreting model variability* — the specific task of deciding whether a recurring deviation is a valid alternative or an error.

4. **Unused signals.** Where systems even compute the signals that would route work to a human (confidence scores, review flags, uncertainty indicators), they rarely act on them. VEGO-AI is a concrete example: it produces `requires_human_review` and `human_review_reason` fields that no component ever reads.

VEGO-AI exhibits all four gaps concretely. This thesis closes them with a layer that **captures human judgment as structured, reusable knowledge and applies it non-destructively to variability assessment** — the contribution detailed in Chapters 3–5.

Table 2.1 summarizes the positioning against the surveyed literature.

| Dimension | Prior work | This thesis |
| --- | --- | --- |
| Human role | Correct, label, or approve (consumed once) | Capture as reusable, provenance-tracked knowledge |
| Feedback persistence | Transient (absorbed into model or discarded) | Durable memory with conflict detection and retrieval |
| Reuse mechanism | None (or implicit via retraining) | Explicit, explainable, embedding-free matching |
| Assessment target | Generic grading or generation | Variability interpretation (substantial vs occasional) |
| AI output preservation | Often modified by human input | Preserved verbatim; comparison is parallel and non-destructive |
| Explanation direction | AI→human | Bidirectional (AI explains; human explains back) |

## 2.9 References (verified)

From the VEGO-AI (MAS4Models 2026) bibliography:
- Ahmed, K., Song, J., Chen, B., Wei, O., & Zheng, B. (2025). *MCeT: Behavioral Model Correctness Evaluation using Large Language Models.* Proc. ACM/IEEE 28th MODELS, 84–95.
- Ali, S. J., Reinhartz-Berger, I., & Bork, D. (2024). *How are LLMs used for conceptual modeling? An exploratory study on interaction behavior and user perception.* Int. Conf. Conceptual Modeling, 257–275. Springer.
- Ananieva, S., et al. (2022). *A conceptual model for unifying variability in space and time.* Empirical Software Engineering, 27(5), 101.
- Auxepaules, L., Py, D., & Lemeunier, T. (2008). *A diagnosis method that matches class diagrams in a learning environment for object-oriented modeling.* 8th IEEE ICALT, 26–30.
- Bian, W., Alam, O., & Kienzle, J. (2019). *Automated grading of class diagrams.* MODELS Companion (MODELSC), 700–709. IEEE.
- Bian, W., Alam, O., & Kienzle, J. (2020). *Is automated grading of models effective? Assessing automated grading of class diagrams.* 23rd ACM/IEEE MODELS, 365–376.
- Bouali, N., Gerhold, M., Rehman, T. U., & Ahmed, F. (2025). *Toward Automated UML Diagram Assessment: Comparing LLM-Generated Scores with Teaching Assistants.* Proc. CSEDU, 158–169.
- Bragilovski, M., van Can, A. T., Dalpiaz, F., & Sturm, A. (2025). *Leveraging machines to derive domain models from user stories.* Requirements Engineering, 30(2), 241–262.
- Calamo, M., Mecella, M., & Snoeck, M. (2025). *Assessing the Suitability of Large Language Models in Generating UML Class Diagrams as Conceptual Models.* Int. Conf. BPMDS, 211–226. Springer.
- Cámara, J., Troya, J., Burgueño, L., & Vallecillo, A. (2023). *On the assessment of generative AI in modeling tasks: an experience report with ChatGPT and UML.* Software and Systems Modeling, 22(3), 781–793.
- Chaaben, M. B., Burgueño, L., David, I., & Sahraoui, H. (2024). *On the utility of domain modeling assistance with large language models.* arXiv:2410.12577.
- Chen, K., Chen, B., Yang, Y., Mussbacher, G., & Varró, D. (2024). *Embedding-based Automated Assessment of Domain Models.* MODELS Companion '24, 87–94.
- Dam, H. K. (2025). *Towards Multi-Agentic AI for automated software design and modelling.* Proc. ASEW 2025, 311–314.
- El-Sharkawy, S., Yamagishi-Eichler, N., & Schmid, K. (2019). *Metrics for analyzing variability and its implementation in software product lines: A systematic literature review.* Information and Software Technology, 106, 1–30.
- Ferrari, A., Abualhaija, S., & Arora, C. (2024). *Model generation with LLMs: From requirements to UML sequence diagrams.* IEEE RE Workshops (REW), 291–300.
- Galster, M., Weyns, D., Tofan, D., Michalik, B., & Avgeriou, P. (2013). *Variability in software systems — a systematic literature review.* IEEE TSE, 40(3), 282–306.
- Hamann, M., Götz, S., & Aßmann, U. (2024). *Towards an Interoperable Model-driven Automated Assessment System for Computer Science Education.* MODELS Companion '24, 95–102.
- Ibáñez, M. B., Barrón-Estrada, M. L., & Zatarain-Cabada, R. (2025). *Can multimodal large language models grade like an expert? A study on UML class diagram assessment accuracy.* Computer Applications in Engineering Education, 33(5).
- Jin, H., Huang, L., Cai, H., Yan, J., Li, B., & Chen, H. (2024). *From LLMs to LLM-based agents for software engineering: A survey.* arXiv:2408.02479.
- Klievtsova, N., Benzin, J.-V., Kampik, T., Mangler, J., & Rinderle-Ma, S. (2023). *Conversational process modelling: State of the art, applications, and implications in practice.* BPM Forum 2023, 319–336. Springer.
- Metzger, A., & Pohl, K. (2014). *Software product line engineering and variability management: achievements and challenges.* FOSE, 70–84.
- Pohl, K., Böckle, G., & Van Der Linden, F. (2005). *Software product line engineering: foundations, principles, and techniques.* Springer.
- Pol'la, M., Buccella, A., & Cechich, A. (2021). *Analysis of variability models: a systematic literature review.* Software and Systems Modeling, 20, 1043–1077.
- Rajbhoj, A., Somase, A., Sant, T., Vale, S., & Kulkarni, V. (2025). *LLM4Model: Automated Requirements Specification Model Authoring.* CAiSE, 128–136. Springer.
- Rosa, M. L., van der Aalst, W. M. P., Dumas, M., & Milani, F. P. (2017). *Business process variability modeling: A survey.* ACM Computing Surveys, 50(1), 1–45.
- Sami, M. A., Waseem, M., Rasheed, Z., Saari, M., Systä, K., & Abrahamsson, P. (2024). *Experimenting with multi-agent software development: Towards a unified platform.* arXiv:2406.05381.
- Silva, J., Ma, Q., Cabot, J., Kelsen, P., & Proper, H. A. (2025). *Towards Human-in-the-Loop LLM-Enabled Domain Modeling.* Int. Conf. Conceptual Modeling, 127–145. Springer.
- Singh, P., Boubekeur, Y., & Mussbacher, G. (2022). *Detecting mistakes in a domain model.* MODELS '22 Companion, 257–266.
- Tselonis, C., Sargeant, J., & Wood, M. M. (2005). *Diagram matching for human-computer collaborative assessment.* 9th Int. Computer Assisted Assessment Conf.

From the curated resource pack (`literature/hitl-resource-pack/bibliography.bib`):
- Amershi, S., et al. (2019). *Guidelines for Human-AI Interaction.* CHI 2019. doi:10.1145/3290605.3300233.
- Gregor, S., & Hevner, A. R. (2013). *Positioning and presenting design science research for maximum impact.* MIS Quarterly, 37(2), 337–355.
- Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). *Design science in information systems research.* MIS Quarterly, 28(1), 75–105.
- Mosqueira-Rey, E., Hernández-Pereira, E., Alonso-Ríos, D., Bobes-Bascarán, J., & Fernández-Leal, Á. (2023). *Human-in-the-loop machine learning: a state of the art.* Artificial Intelligence Review, 56, 3005–3054.
- National Institute of Standards and Technology (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0).* NIST AI 100-1. doi:10.6028/NIST.AI.100-1.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). *A design science research methodology for information systems research.* Journal of Management Information Systems, 24(3), 45–77.
- Silva Mercado, J. (2024). *AI Assisted Domain Modeling Explainability and Traceability.* MODELS Companion 2024. doi:10.1145/3652620.3688197.
