# Abstract

**Context.** AI-assisted assessment of domain models requires interpretive judgment — deciding whether a recurring deviation from a reference model is a valid alternative or an error. VEGO-AI addresses this with a four-agent LLM pipeline that distinguishes substantial variability (valid alternatives) from occasional variability (errors). The pipeline already produces review signals and confidence scores that anticipate human involvement, yet no mechanism captures, stores, or reuses a human expert's response.

**Gap.** Across the human–AI collaboration, explainable AI, and model-assessment literatures, human feedback is treated as a transient correction: it resolves one case and is consumed. No existing system combines selective triggering, structured capture, provenance-tracked storage, and cross-case reuse of human judgment for model-variability interpretation.

**Method.** Following design-science methodology (Hevner et al., 2004; Peffers et al., 2007; Gregor & Hevner, 2013), this thesis designs, implements, and evaluates a five-layer human–AI co-reasoning artifact that extends VEGO-AI without modifying its baseline. The layers are: a Selective Intervention Policy (M1) that routes uncertain cases to human review; a Feedback Manager (M2) that captures schema-validated expert decisions; a Human Judgment Memory (M3) that stores reusable, provenance-tracked judgments with conflict detection and explainable retrieval; an Advisory Layer (M4A) that surfaces past judgments as graded evidence while preserving the original AI classification; and a Deterministic Comparison (M4B-1) that evaluates the memory-informed assessment against the original in a parallel, non-destructive artifact.

**Results.** The artifact is implemented in pure Python (no LLM dependencies)
and governed by evidence-consistency and protected-path checks. The accepted
verification record reports both the VEGO-AI and research-script suites passing;
exact counts remain attached to that dated record. It processes 179 student models
across four settings, producing 27
comparison records with provenance traceability. A bias- and leakage-controlled
evaluation methodology with reviewer calibration, blind expert annotation, a
sealed 16/8 development/holdout split, paired net-correction analysis, and an
external replication gate is preregistered.

**Honest status.** The thesis demonstrates mechanism validity — the reusable
human-judgment lifecycle exists, is reproducible, and preserves the baseline. It
makes no accuracy-improvement claim: independent expert labels have not yet been
collected (0 of 24 generalization-safe rows labeled), and the current
conservative policy changes zero classifications by design. The first next step
is human-gated calibration and annotation. An eight-row holdout can provide only
pilot evidence; a formal improvement claim requires a separate new
education-domain set with at least 30 adjudicated rows and all preregistered
statistical and safety criteria. The design-science contribution stands
independently of whether the later result is positive, null, mixed, or harmful.

**Keywords:** human–AI collaboration, reusable human judgment, domain model assessment, variability interpretation, design-science research, VEGO-AI, human-in-the-loop
