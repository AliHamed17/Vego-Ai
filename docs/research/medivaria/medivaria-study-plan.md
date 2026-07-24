# MediVARIA Study Plan - Medical-Domain Transfer of VEGO-AI + H-Layer

Last updated: 2026-07-04 by Fable (Claude). Status: PLANNING DRAFT for supervisor review (Iris + Arnon); no data work, no implementation, no partner commitments are made by this document.

Sources: `MediVARIA_OnePage_v1.docx` (one-page technical proposal, archived ignored at `artifacts/medivaria/MediVARIA_OnePage_v1.docx`; tracked summary below), `docs/research/extension-plan-2026-07-supervisor-redirect.md` (active plan), `docs/research/phd-extension-ideas.md` (idea 1), `docs/research/phd-thesis-optimization-plan.md` (P-RQ5, optimization-roadmap P4/P5).

Phase-namespace note: "redirect-plan P0-P6", "optimization-roadmap P0-P5", and "MV-P0..MV-P5" are three different numbering schemes; every cross-file phase reference in this document is qualified with its plan name.

## 1. What MediVARIA Is (One-Pager Summary)

MediVARIA transfers the VEGO-AI architecture to clinical guideline adherence. Existing Clinical Decision Support Systems (CDSS) check WHETHER clinicians follow guidelines; MediVARIA asks WHY they deviated and whether the reason is defensible. It classifies deviations into **justified clinical variability** (context-driven adaptation, e.g., adjusted dosing for renal impairment, deferred procedure after documented patient refusal) versus **erroneous deviations** (missed mandatory screening, contraindicated drug, absent follow-up), each with a structured rationale.

Motivation cited in the proposal: physicians override CDSS alerts at rates exceeding 80% because alerts ignore patient context, making real errors indistinguishable from ignored noise (sources cited in the one-pager: Felisberto et al. 2024; Nanji et al. 2021; Oliart et al. 2022 - citations to be independently verified during the literature survey, not re-verified here).

Proposal facts: TRL 3 -> TRL 5 target over 3 years, IIA Applied Research track, medical partner TBD; the proposal also names target customers - Israeli HMOs, public hospitals, international health systems - recorded here for provenance only (proposal-side commercial framing, excluded from research framing per section 6). TRL 3 baseline = the MAS4Models @ MODELS 2026 workshop submission results (the one-pager says "MODELS 2026"; the repo record identifies it as the MAS4Models workshop paper - flag this imprecision back to the one-pager's authors). As reported there: Language Advisor F-scores 0.75-1.0; Domain Advisor guideline alignment 0.70-0.88; compliance scoring 0.80-0.96 vs. expert review; identified variability patterns validated by domain experts. These figures are the PAPER's reported education-domain results - they are not clinical evidence and must never be quoted as MediVARIA performance.

## 2. Why This Is The Same Research Track

The research spine is unchanged: **reusable human judgment for variability assessment under structured normative specifications.** MediVARIA is the concrete instantiation of the medical-domain transfer DIRECTION that Iris and Arnon named as their preferred extension (2026-07-01 meeting, transcript 33:36-33:49). Supervisor endorsement of MediVARIA itself has not yet happened - it is the MV-P0 exit gate (section 5).

| VEGO-AI (MSc thesis, education domain) | MediVARIA (PhD track, clinical domain) |
| --- | --- |
| Domain description | Clinical guideline corpus |
| Student case model | Patient EHR trajectory |
| Substantial variability (valid alternative) | Justified clinical variability |
| Occasional variability (error/misconception) | Erroneous deviation |
| Variability patterns | Candidate clinical quality signals (actionability is an MV-RQ2/MV-RQ5 outcome, not a given) |
| Course staff as human experts | Clinicians / clinical reviewers as human experts |
| Agent 1 Language Advisor (modeling-language semantics) | Guideline-language semantics, incl. conditional phrasing ("as tolerated", "in the absence of contraindications") |
| Agent 2 Domain Advisor (reference guidelines) | Clinical guideline operationalization per domain |
| Agent 3 Model Inspector (compliance vector) | Per-patient adherence assessment over the EHR trajectory |
| Agent 4 Variability Explorer (pattern classification) | Population-level deviation-pattern classification |

## 3. The H-Layer Is MediVARIA's Missing Piece (Iris-Directive Synthesis)

The July 2026 H-layer redesign (`docs/research/h-layer/skills-map.md`) maps one-to-one onto MediVARIA's stated problem. This is the strongest thesis-to-PhD bridge we have:

| H-layer element (thesis) | MediVARIA counterpart | Iris directive it implements |
| --- | --- | --- |
| S1 Listen over both circles, early stages | Continuous observation of guideline-interpretation and adherence events, not only final deviation verdicts | D1, D2 |
| S2 Triage with configurable dosage (`every_decision` / `threshold` / `first_n_then_auto` / `silent`) | The DESIGNED answer to alert fatigue, to be tested by MV-RQ3: route to clinicians only what merits attention instead of firing indiscriminately (the reported >80% override problem, as cited in the one-pager) | D6 |
| S3 Ask human (self-contained review items) | Contextualized clinical review requests instead of context-free alerts | D5, D7 |
| S4 Capture structured feedback (decision, rationale, confidence, scope) | Structured override rationale - the "account of why" the proposal promises | D5, D8 |
| S5 H-Verify (anti-sycophancy, source-grounded challenge) | Verify clinician override rationale against the guideline corpus and patient record; question, never blindly accept or flatly contradict; bounded rounds | D9, D10 |
| S6 Integrate (approval-gated corrections) | Guideline-operationalization refinements from validated clinical judgment (design-only; heavily gated in the clinical setting) | D8 |
| S7 Percolate/learn (judgment memory beyond save/retrieve) | Reusable clinical-judgment memory: recurring justified-deviation patterns are INTENDED to become quality signals and reduce repeat review load (hypothesis, tested by MV-RQ5) | D8 |
| Real human expert, never simulated | Clinician-in-the-loop; MediVARIA never simulates the clinician | D5 |
| Framework/evaluation separation | Clinical evaluation (with partner) is a separate, later, gated track | D4 |

## 4. Research Questions (MediVARIA Study Set)

These extend the PhD questions in `docs/research/phd-thesis-optimization-plan.md` (P-RQ5 transfer question) and operationalize ideas 1, 2, 3, and 5 of `docs/research/phd-extension-ideas.md`:

| ID | Question | Builds on |
| --- | --- | --- |
| MV-RQ1 | Can the four-agent + H-layer architecture transfer from student model assessment to clinical guideline adherence, and which components are domain-agnostic in practice (not only "in principle")? | Idea 1; P-RQ5 |
| MV-RQ2 | Can justified vs. erroneous deviation classification, with structured rationale, reach expert-acceptable quality on real EHR trajectories? | One-pager core claim (to be tested, not assumed) |
| MV-RQ3 | Which intervention-dosage policies reduce clinician review load without missing erroneous deviations (the alert-fatigue trade-off, measured)? | Idea 2; D6 |
| MV-RQ4 | Does source-grounded verification of clinician overrides (S5) distinguish defensible from indefensible overrides while converging within clinically acceptable interaction time? | Idea 3; D9/D10 |
| MV-RQ5 | Does accumulated clinical-judgment memory (S7) improve triage/verification quality across patients and time without unsafe generalization? | Idea 5; leakage discipline |
| MV-RQ6 | What are the domain-transfer costs: medical ontology mapping, temporal reasoning over longitudinal records, conditional guideline language? | One-pager challenges section |

## 5. Phased Plan (aligned: IIA TRL timeline x academic trajectory)

| Phase | Window | Content | Gate to exit |
| --- | --- | --- | --- |
| MV-P0 Groundwork (now) | 2026-07 .. 2026-09 | This plan; supervisor alignment (2026-07-15 agenda item); MediVARIA-aware literature branches in the course survey (CDSS overrides, healthcare conformance checking, guideline modeling); no data, no code | Iris/Arnon endorse scope + role split (thesis vs. IIA project) |
| MV-P1 Thesis alignment | 2026-09 .. 2027-03 | MSc thesis stays education-domain; MediVARIA appears ONLY in motivation/discussion/future-work chapters as the transfer target; the H-layer detail specs are PRODUCED earlier during redirect-plan P2 (2026-07-15..2026-08-15, written domain-parameterized per skills-map open question 8) and are consumed/kept transferable here | Thesis submitted (~March 2027 fast path) |
| MV-P2 Feasibility spec | 2026-10 .. 2027-06 | Domain-transfer specification: guideline-corpus selection method, EHR-trajectory event mapping onto E1-E14 (pipeline events E1-E9 plus the E10-E14 human-feedback lifecycle; E15-equivalent clinical evaluation events belong to the gated clinical evaluation track, MV-P4/MV-P5), clinical H-layer dosage modes, S5 source set for clinical claims; ethics/IRB requirements catalog; synthetic/public-data pilot design per the section-6 rules | Ethics review path defined (including the no-partner fallback determination); partner conversations informed by spec |
| MV-P3 PhD proposal | ~2027 (semester after thesis) | PhD proposal: thesis as preliminary results (Iris: proposals include preliminary results); MediVARIA studies as the 2-3 PhD studies (MV-RQ1/2 transfer study; MV-RQ3/4 dosage + override-verification study; MV-RQ5 longitudinal memory study) | Proposal approved |
| MV-P4 TRL 4 pilot | Partner-dependent | With medical partner + IRB approval: retrospective, de-identified guideline-adherence pilot in one clinical domain; Version-0/Version-1 style comparison with clinician panel; usability instrument | IRB approval; partner agreement; local pilot success (mirrors the education-track rule: pilots local/small first) |
| MV-P5 TRL 5 validation | Years 2-3 of IIA track | Broader validation across guideline domains; reliability (multi-clinician, adjudication); quality-signal utility evaluation with HMO/hospital stakeholders | Evidence gates equivalent to EXP-005 discipline, clinical edition |

Parallelism note: MV-P1 and MV-P2 overlap deliberately - the thesis is not delayed by MediVARIA; MediVARIA reuses the thesis's H-layer specs.

## 6. Governance, Ethics, And Claim Boundaries (clinical edition)

- All existing gates hold: no accuracy claims without real expert labels; no invented/synthetic labels as evidence; no VEGO-AI source behavior changes; frozen tags; framework/evaluation separation.
- Clinical additions (stricter, not looser):
  - NO patient data of any kind enters this repository - not raw, not de-identified, not synthetic-derived-from-real, and PUBLIC de-identified clinical datasets count as patient data for repo purposes. Partner data work happens only in a partner-approved environment after IRB/ethics approval (`docs/research/ethics-irb.md` extends before MV-P4).
  - No-partner fallback rule: fully-synthetic or public de-identified datasets may support a mechanism-validation pilot outside a partner environment ONLY after (a) supervisor approval, (b) an explicit ethics/IRB determination for that dataset and use, and (c) a named non-repo working environment. Any such pilot yields mechanism/feasibility evidence only - never accuracy or generalization evidence - consistent with the standing no-synthetic-labels-as-evidence gate.
  - TRL 3 education-domain metrics are never quoted as clinical performance; every TRACKED doc that quotes MediVARIA proposal facts or metrics carries this boundary line until clinical evidence exists (checkable rule scope).
  - MediVARIA is decision-SUPPORT research: no autonomous clinical decisions; the clinician is always the authority (D5 made domain-critical).
  - The IIA/product framing (customers, market size) stays in proposal documents; research docs keep design-science framing (problem, artifact, evaluation).
  - Same-pattern leakage discipline transfers: judgment memory reused for the same patient/case is mechanism validation, never generalization evidence.
- Repo hygiene: the one-pager stays ignored under `artifacts/medivaria/`; partner names/negotiation details are not recorded in tracked docs while "TBD - discussions ongoing".

## 7. Thesis Enhancement Actions (what this adds to the MSc thesis NOW)

| Chapter (drafted) | Enhancement | Size |
| --- | --- | --- |
| 1 Introduction | One paragraph: the interpretive-variability problem generalizes to any practice governed by structured norms; clinical guideline adherence as the flagship example (cite one-pager motivation after source verification) | Small |
| 2 Related Work | New survey branches (CDSS override/alert-fatigue, healthcare conformance checking, guideline modeling) - already added to the taxonomy; strengthens the gap statement beyond education | Medium (via course survey) |
| 3 Problem/RQ | Note that RQ generality is tested by the medical transfer (future work), sharpening construct validity | Small |
| 9 Discussion | "Transferability" subsection: the mapping table of section 2 + what is domain-agnostic by design | Medium |
| 10 Conclusion / Future Work | MediVARIA as the concrete PhD continuation with the MV-RQ set; direct-track narrative (thesis = preliminary results) | Medium |
| Thesis defense/story | The thesis is no longer "a course-grading helper": it is the education-domain instantiation of a two-domain research program - a materially stronger narrative for the direct-track case | - |

Chapter edits themselves are queued for the thesis-writing workflow (not performed in this planning pass); this table is the checklist.

## 8. 2026-07-15 Meeting Agenda Additions

1. Present this plan: MediVARIA as the PhD umbrella; thesis untouched in scope, strengthened in narrative.
2. Confirm the role split: MSc = education-domain H-layer framework; PhD studies = MV-RQ1/2, MV-RQ3/4, MV-RQ5.
3. Ask: which clinical guideline domain to target first (affects MV-P2 corpus selection)?
4. Ask: ethics/IRB route at Haifa for retrospective de-identified EHR work; when to engage the partner discussion (Iris/Arnon own the partner relationship)?
5. Ask: should the H-layer detail specs (redirect plan P2) be written domain-parameterized from the start (recommended), or education-first with a transfer appendix?

## 9. Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| MediVARIA distracts from the thesis (Iris's pace concern) | MV-P1 rule: thesis scope frozen to education domain; MediVARIA consumes only survey/spec effort until the thesis is submitted |
| No medical partner materializes | MV-P2 designs a public/synthetic-data pilot fallback under the section-6 no-partner fallback rule (supervisor approval + ethics determination + non-repo environment; mechanism evidence only); the PhD proposal can stand on transfer-spec + pilot design + education evidence |
| Ethics/IRB timeline longer than expected | Ethics requirements catalog starts at MV-P2 (early), before any data conversation |
| Clinical overclaiming (TRL3 numbers cited as clinical evidence) | Hard rule in section 6; evidence guard style: every MediVARIA doc carries the boundary line |
| Alert-fatigue replication (H-layer itself becomes noise) | MV-RQ3 makes dosage a measured research question, not a configuration afterthought |
| Scope creep into repo code | Documentation-only boundary continues; any MediVARIA code lives in a future separate package/repo decided with supervisors |

## 10. Acceptance Checklist (this planning pass)

- [x] One-pager archived (ignored) and summarized (tracked).
- [x] MediVARIA linked to the active redirect plan, PhD idea log, thesis structure, taxonomy, and July-15 agenda.
- [x] Supervisor directives D1-D2 and D4-D10 traceable into the MediVARIA framing (section 3); D3 (H-naming) is inherited via the skills-map canon this plan reuses; D11 (July-15 deliverables) is served by the section-8 agenda; D12 (survey + idea log) by the taxonomy MediVARIA branches and the updated idea log.
- [x] Clinical claim boundaries and no-patient-data rule stated.
- [x] No VEGO-AI source changes; memory and dashboards updated; validations run.
