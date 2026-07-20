# Supervisor Meeting Notes - 2026-07-01

- Date: 2026-07-01 09:13-09:51 +03:00 (Zoom, recorded).
- Participants: Ali Hamed (MSc student), Prof. Iris Reinhartz-Berger (supervisor, University of Haifa), Prof. Arnon (collaborating faculty, Ben-Gurion University).
- Source: local Zoom recording; Hebrew transcript generated locally with faster-whisper `large-v3-turbo` on 2026-07-03.
- Transcript location (ignored, not tracked): `artifacts/meetings/2026-07-01-iris/transcript_he.txt`.
- Note: the recording opens with a deliberate recap ("I will repeat the points we discussed"), so the transcript is a reliable summary of the session's decisions.

## 1. VEGO-AI Architecture: Two Communication Circles (00:00-04:24)

Iris described the original VEGO-AI architecture as having two distinct communication circles between the agents:

1. **Artifact circle**: Language Advisor -> Language Template -> Domain Advisor -> Reference Guidelines -> Model Inspector; Domain Advisor and Model Inspector pass identified/observed variability to the Variability Explorer.
2. **Questions-and-Answers (Q&A) circle**: e.g., when the Domain Advisor is uncertain about a language-specific issue (attribute vs. class), it asks the Language Advisor. The Q&A mechanism serves two purposes:
   - For the asker: resolve low-confidence guideline decisions (e.g., whether a construct should be an attribute or a class, and the implications).
   - For the answered agent: the question can reveal that parts of its own template/guidelines are imprecise, letting it refine its own artifact.

**Directive:** the human-judgment layer (good that it was defined as a separate layer) must define exactly how it enters, and to what degree it interferes with, BOTH circles. It may need to sit on those connections and listen to Q&A exchanges (deciding which to pick up or check) and/or listen to artifacts and their changes - and this should happen at EARLY stages, not only after Agent 4 has already decided on variability (the early-stages point was raised in dialogue and mutually confirmed).

Iris's mental model: the layer is a **listener** - mostly a quiet listener, but sometimes deciding what to take, what to involve the human in, and how to route feedback back (00:42-04:24).

## 2. Layer Decomposition: Agents vs. Skills (04:24-05:34, 13:03-14:08)

- Iris liked the separation between the review/intake stage and the feedback stage.
- The listening/deciding functionality may be one agent with SEVERAL skills (not a single skill); integrating feedback back into the agents may be another agent or another skill of the same agent - to be decided and defined explicitly.
- Feedback incorporation should let the agents keep working **iteratively**, improving the product **without entering infinite loops** where agents disturb each other.

## 3. Human Expert Is a Real Person (05:35-08:15)

- Iris understood Ali's "human expert" as an agent simulating a human; she insisted the human expert is and must remain a **real person**. Do not replace the human expert with a simulated agent.
- Real experts are available: Arnon has taught these courses, Iris teaches them, TAs, and later colleagues abroad. Iris also wants to bring parts of this into her own classroom.
- The framework layer needs at least two functionality types: (a) listening + deciding what merits human review and framing it; (b) percolating the feedback back - at early stages, not final stages.

## 4. Framework vs. Evaluation Separation (08:15-09:08, 22:36-22:59)

- Iris explicitly invoked design science (build/develop vs. evaluate, per Pnina's course): what Ali described about measuring final-output improvement is EVALUATION, not framework.
- **Evaluation design**: compare **Version 0 (no human involvement)** vs. **Version 1 (with human involvement)** on defined evaluation criteria (e.g., number of errors), plus a **usability questionnaire** for Version 1 users.
- **Directive:** put evaluation in a SEPARATE diagram; move everything evaluation-related there; do not work on it now - first stabilize the framework, then progress to evaluation.

## 5. Evaluation Resources (09:08-11:13)

- Local: course team, a second lecturer who teaches the course in another semester, TA teams.
- Abroad (later stages): colleagues at Stockholm University (Sweden) and in Belgium teach modeling courses with hundreds of students where grading is painful; Iris believes they would at least examine the idea. Pilots must run locally first.
- Iris: "regarding evaluation you have nothing to worry about" - venues will exist and evaluation can be done meaningfully against real teams.

## 6. M3/M4 Positioning and Renaming (11:13-13:10)

- Distinguish which of the M-milestones belong to the FRAMEWORK and which to EVALUATION.
- Iris's reading: **M3 (human judgment memory) is part of the framework**, but should be reached through M2 (as a skill/extension of M2) feeding back into VEGO-AI. **M4 (memory advisory / memory-informed comparison) belongs to evaluation** - Ali confirmed M4 is currently used for evaluation-style architecture comparison.
- **Directive: defer M4 to a later stage.**
- **Directive: rename the human-layer milestones from M1/M2/M3 to H1/H2/H3** ("H" for human), since this is the human layer.
- **Directive:** decide whether H1-H3 are separate agents or different skills of one agent, and define specifically both the skills and the involvement points across VEGO-AI's stages.

## 7. Arnon's Points: Continuous Monitoring and Parallel Human Decisions (14:08-15:19)

- Arnon: monitoring by the human layer should be **continuous** - across all agents and every interaction (he saved the whole discussion and agrees with Iris).
- Arnon proposed that, in the first stage, the human expert could enter a decision for EVERY decision the automatic agent makes - collecting agent decision + human decision in parallel, learning from agreements, and inserting validated decisions into context for subsequent queries.
- Iris's caution: that demands too much expert time and risks blocking Ali's progress while waiting for feedback; the **dosage** of human involvement must be calibrated. But the framework must still allow receiving feedback and doing something with it. (Iris returned to the dosage point at 16:45-17:13, inside the discussion covered in section 8.)

## 8. Bidirectional Interfaces and Learning Beyond Save/Retrieve (15:19-17:29)

- Part of the thesis is to **define the human/user interface**. It must not be one-directional.
- Many arrows in Ali's architecture diagram are one-directional; most should probably be **bidirectional**, at least in early stages.
- Percolating feedback back is not just "save it in memory and retrieve when needed": the layer must **reason and learn** from feedback - machine-learning-style improvement - **including correcting the prior knowledge of Agents 1-4**.

## 9. Expert Trust and Anti-Sycophancy (17:29-19:58)

- Ali asked how expert feedback should be treated (subjective vs. objective) given the model learns from it.
- Iris: known failure of agentic tools is being immediately swayed by the user even when wrong. She wants the layer to behave like a **colleague at her level**: when told X, it checks X against its own sources; if X seems inconsistent, it does not flatly contradict but raises questions that make the expert reconsider.
- True human-AI interaction: the human talks to the AI and the AI talks to the human, and the interaction must **converge** (not an hour-long argument about one attribute).
- Motivating examples: a TA giving a wrong instruction discovered months later; Iris herself misreading a question (e.g., dropping a "not") - the AI should say "wait, this contradicts A, B, C - let us discuss whether it is a mistake."

## 10. Flexible/Configurable Human Intervention (19:51-21:19)

- Arnon: the human-interaction architecture must be **flexible/configurable**, e.g.:
  - pop-up for every agent decision;
  - pop-up only for decisions below a confidence threshold;
  - massive human review on the first N (e.g., ten) exercises, then automatic handling of the rest based on the approvals collected.
- The evaluator must be flexible to a configuration "we can decide on."
- Iris: this belongs in the **detailed specification** ("detail spec" - not detailed design, since the LLM is autonomous) that will be written for each element - premature now, but part of the spec work.

## 11. Deliverables Requested for the Next Meeting (21:19-22:59)

Iris asked to see two things next:

1. **Skills map**: the skills of the human-layer agent(s) relative to Agents 1-4, and how they integrate at the different points of VEGO-AI (are H1-H3 separate agents or skills of one agent?).
2. **Prompt requirements** (explicitly NOT the prompts themselves) for these agents: what should be said, what context they receive, what task, what steps - enough to understand what we want to see there.

Evaluation is not forgotten but parked in a separate diagram until the framework stabilizes.

## 12. Literature Survey and Course Work (23:03-27:30)

- Iris asked about a literature survey on human-in-the-loop in the agentic world. Ali's initial check: nothing specific to this exact problem; many generic HITL architectures based on continuous human feedback plus ML/deep-learning improvement loops (fine-tuning/alignment style).
- Arnon: this sounds like reinforcement learning; unclear how it transfers to the LLM world where the model is not actually retrained - worth examining RL + LLM approaches specifically.
- Iris: do not go only to classic ML-on-the-loop; cover **generative AI in this context** as well; compare works; the key output is articulating **what we innovate relative to the literature** - the gap the thesis is built around.
- Ali is taking Pnina's research-methodology course; the course work should be this literature survey. Presentation mid-August; written submission around end of September/October.
- Iris's hope: by September/early October there is enough for a **paper**: the framework plus the literature survey connecting it to the literature.

## 13. Administrative / Trajectory (27:30-33:57)

- Next supervisor meeting: **2026-07-15**; Arnon will be invited.
- MSc-to-PhD direct track (Ali asked): the project is broad and is also being taken toward the **medical domain**; thesis is roughly one journal paper; a PhD is 3-4; the thesis can serve as the small study inside the larger PhD research; PhD proposals include preliminary results, which the thesis provides. Administrative details to be checked with Sigal / Graduate Studies Authority (procedures differ between Haifa and Ben-Gurion).
- If the pace is fast, thesis submission around **March 2027** is plausible, with a PhD proposal about a semester later on similar topics.
- Arnon: while reading, keep an **idea log** of extensions/topics for separate studies (to be closed with Iris later).
- Iris: the extension she and Arnon are most interested in is the **medical domain** - can the same architecture/evaluation be transferred to other domains, and with what implications.
- Target: toward **October 2026**, a consolidated ("crystallized") framework + survey.
- Human interface design comes after the framework stabilizes ("the easier part").
- Ali's closing summary: start from the points raised, establish a baseline architecture we are confident in, then run experiments on it.
