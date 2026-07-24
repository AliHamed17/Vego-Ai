# PhD Extension Idea Log

Last updated: 2026-07-04 by Fable (Claude).

Purpose: lightweight idea log, NOT a commitment. Per Arnon's instruction in the 2026-07-01 meeting (transcript 33:05-33:22), collect extension ideas while reading; each must later be reviewed and approved with Iris. Sizing context from the same meeting: an MSc thesis is roughly one journal paper / one small study; a doctorate is roughly three studies / three-four journal papers, and the thesis can serve as the preliminary-results study inside the larger PhD research.

Governance: every idea below is subject to the gates in `docs/operations/alignment-control.md` - the EXP-005 real-label gate, the no-accuracy-claim boundary, the parked evaluation track, and the protected VEGO-AI source paths. No evaluation activity for any idea starts without supervisor approval.

Preferred direction: **medical-domain transfer** is the extension Iris and Arnon explicitly said they would be most interested in (transcript 33:36-33:49).

## Seed Ideas

### 1. H-layer transfer to medical model assessment (preferred) - NOW ACTIVE AS MediVARIA

- Status update (2026-07-04): this idea has materialized as **MediVARIA** - a one-page technical proposal (TRL 3 -> TRL 5, 3 years, IIA Applied Research track, medical partner TBD) transferring VEGO-AI to clinical guideline adherence (justified clinical variability vs. erroneous deviations, with structured rationale). Full study plan: `docs/research/medivaria/medivaria-study-plan.md` (MV-RQ1-MV-RQ6, phases MV-P0..MV-P5). Ideas 2, 3, and 5 below now have their natural clinical setting inside MediVARIA. Boundary: education-domain TRL3 metrics are not clinical evidence; no MediVARIA performance claims exist yet; supervisor endorsement (MV-P0 gate) is pending.
- Research question: can the H-layer architecture (listener, dosage-configured intervention, verified expert feedback, judgment memory) transfer from student domain-model assessment to medical-domain model/knowledge assessment, and what changes are forced by the domain?
- Required evidence: a medical modeling corpus or partner dataset; domain-expert availability; a mapping of the E1-E14 event catalog (pipeline + human-feedback lifecycle; E15-equivalent evaluation events stay in the gated clinical evaluation track) onto the medical pipeline; ethics/IRB clearance appropriate to medical data.
- Possible study: replicate the framework Version-0/Version-1 comparison in a medical modeling course or clinical-guideline modeling setting; measure expert-effort and review-quality differences against the original domain.
- Risks: data access and ethics are much heavier; medical expert time is scarcer than course-staff time; domain semantics may not decompose into the same two communication circles.
- Relation to MSc thesis: direct architecture transfer; the thesis is the preliminary-results study proving the mechanism in the education domain.

### 2. Human-dosage policies across domains

- Research question: how much human involvement (every-decision / confidence-threshold / first-N-then-auto) yields which quality gain per expert-hour, and does the optimal dosage policy transfer across domains and expert populations?
- Required evidence: instrumented S2 triage logs across multiple dosage configurations; expert time accounting; task-quality measures per configuration.
- Possible study: within-subjects comparison of dosage modes on the same exercise corpus with course staff, then a cross-domain replication (e.g., medical, idea 1).
- Risks: expert-hour cost of running multiple arms; confounding between reviewer skill and policy; small-N expert pools.
- Relation to MSc thesis: the dosage configuration is specified (not evaluated) in the thesis framework; this idea turns it into an empirical study.

### 3. Source-grounded anti-sycophancy for expert feedback

- Research question: does source-grounded verification of HUMAN input (S5 H-Verify: check expert claims against templates/guidelines/prior judgments, raise questions on conflict) measurably reduce error propagation from wrong expert feedback, while converging in bounded dialogue?
- Required evidence: seeded wrong-feedback trials (the TA-nonsense and dropped-"not" scenarios from the meeting); logs of verification outcomes, question rounds, and convergence; comparison against a comply-always baseline.
- Possible study: controlled experiment injecting known-wrong expert rulings into the feedback stream with and without S5; measure caught/propagated errors and expert-perceived friction.
- Risks: designing realistic wrong-feedback without contaminating real memory - seeded/synthetic feedback MUST be hard-isolated from real judgment memory and real evidence stores and never counted as EXP evidence; expert annoyance if questioning is miscalibrated; generalizing beyond one source set.
- Relation to MSc thesis: S5 is specified as a framework requirement in the thesis; this isolates it as an independently publishable contribution.

### 4. Cross-institution evaluation with modeling courses

- Research question: does the H-layer generalize across institutions, languages, and grading cultures - specifically the modeling courses with hundreds of students at Stockholm University and in Belgium mentioned by Iris?
- Required evidence: successful local pilots first (explicit meeting precondition); partner agreement at one or both institutions; comparable exercise corpora; cross-site expert labels.
- Possible study: replicate the Version-0/Version-1 comparison at a partner institution; analyze reusable-judgment transfer (does memory from one course help another?) under strict leakage controls.
- Risks: coordination overhead; data-sharing and privacy constraints across institutions; course differences confounding results.
- Relation to MSc thesis: uses the thesis framework unchanged; extends the parked evaluation track's resource plan into a full generalization study.

### 5. Longitudinal human-judgment memory and learning

- Research question: how should judgment memory behave over semesters - does accumulated, verified expert judgment (S7) keep improving triage/verification quality, and how are conflicts, drift, and obsolescence handled long-term?
- Required evidence: multi-semester deployment logs; memory-growth and reuse statistics; conflict/adjudication records; quality trends over time.
- Possible study: longitudinal observational study across 2-4 course iterations, measuring reuse rate, conflict rate, correction acceptance, and expert-effort trends as memory grows.
- Risks: long timeline; course content changes confound trends; memory quality depends on early labeling discipline.
- Relation to MSc thesis: the thesis specifies memory with provenance/conflict handling; this studies its long-run learning dynamics - the strongest "beyond save/retrieve" evidence.

## Admin Note

Ask Sigal / the Graduate Studies Authority about direct-track PhD requirements: entry route (Iris believes direct track may formally start from the bachelor's degree; Ali's understanding is via research-proposal milestones with credit/GPA conditions), course-credit reductions (Iris: "not 28 plus 12, but less - unsure how much"), and timeline implications of a ~March-2027 thesis submission followed by a proposal one semester later.
