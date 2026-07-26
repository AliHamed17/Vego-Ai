# Chapter 8 — Threats to Validity

> Draft. Sources: `docs/research/validity-threats.md`, `artifacts/EVALUATION_STRICT_REVIEW.md`,
> `docs/research/evaluation-plan.md`. Threats are stated honestly and paired with the mitigation already in
> place or planned in the evaluation protocol (Chapter 6).

## 8.1 Overview

Every empirical study faces threats to validity, and design-science research is no exception. This chapter identifies the threats most relevant to this thesis, organized by the standard four-category framework (construct, internal, conclusion, and external validity), plus ethical and data-governance considerations. Each threat is paired with the mitigation already in place or defined in the evaluation protocol (Chapter 6). The chapter is intentionally honest: threats are not minimized, and where mitigations are partial or pending, this is stated explicitly.

## 8.2 Construct validity (are we measuring the right thing?)

Construct validity concerns whether the measures and operationalizations used in the study actually capture the theoretical constructs they are intended to represent.

**No independent benchmark in the repository.** The author-reviewed classification files `analysis/agentD_variability_classes_*` duplicate Agent 4's output byte-for-byte, so they cannot serve as ground truth. If used as labels, any evaluation would be circular — measuring the system's agreement with itself. *Mitigation:* this threat is addressed at the protocol level. The independent expert annotation study (§6.6) is the only admissible source of ground truth. The byte-identical files are documented and never used as evaluation labels.

**Agent 4 output is not ground truth.** More broadly, treating the system's own classification as the evaluation target would make any "accuracy" metric meaningless — a system that agrees with itself will always appear accurate. *Mitigation:* the evaluation design explicitly separates the AI's output from the evaluation target. The `ai_prelabel` field appears only in the adjudication audit sheet, clearly marked as the AI's opinion rather than ground truth, and is hidden during blind labeling.

**The classification task is inherently interpretive.** The distinction between substantial variability (valid alternative) and occasional variability (error) is not a binary fact but an expert judgment call. Reasonable domain experts may disagree about whether a specific deviation is a valid alternative or a mistake, particularly for borderline cases. *Mitigation:* the annotation protocol accounts for this by providing a third label (`Undetermined / Needs Review`), requiring written rationales, using two independent reviewers, computing Cohen's κ to measure agreement, and adjudicating disagreements through a third expert. The inter-rater agreement score will be reported alongside the accuracy metrics, so the reader can judge the reliability of the ground truth itself.

**Reviewer-role ambiguity.** A reviewer who also designed the policy may
unintentionally interpret ambiguous items in a way that supports the design.
*Mitigation:* two reviewers label independently before adjudication; raw returns
remain immutable; policy development uses only adjudicated development labels;
and the adjudication role is recorded separately in `GoldLabelRecord-v2`.

**Class prevalence and missing classes.** The frozen Agent 4 distribution is
9 Substantial, 18 Occasional, and 0 Undetermined. This is an output prevalence,
not the true class distribution. Accuracy may appear high under an imbalanced
gold set, while the Undetermined class may be impossible to estimate reliably.
*Mitigation:* report the adjudicated class distribution, macro-F1, per-class
precision/recall, confusion matrices, and Wilson intervals. Do not interpret a
missing class as perfect performance.

## 8.3 Internal validity (are observed effects real?)

Internal validity concerns whether the observed relationship between the intervention (the reusable human-judgment layer) and the outcome (classification quality) is genuine or an artifact of confounding factors.

**Anchoring bias in annotation.** If annotators are shown the AI's classification or the memory-informed recommendation before making their judgment, they may be anchored toward the system's answer, inflating apparent accuracy for whichever system they are anchored to. *Mitigation:* the blind labeling sheets carry neutral context only — pattern description, setting, affected cases, and related guideline. All AI-derived fields (original label, justification, memory advice, leakage status, priority, and ranking) are withheld. Row order is randomized separately per reviewer, and items carry anonymous IDs.

**Same-pattern leakage.** Memory derived from a pattern must not be used to "evaluate" that same pattern. If a human labeled pattern X, and that label was stored in memory, and memory was then used to inform the classification of pattern X, then any agreement between the memory-informed classification and the expert label is circular — the system is comparing a judgment against itself. The running example illustrates this concretely: the "Customer as actor" memory (`HJM-ucd_ch-P6`) was derived from feedback about pattern P6, so P6's comparison row carries `evaluation_leakage_status = same_pattern_memory_used` and is excluded from generalization-safe metrics (see §5.6 and §6.5). *Mitigation:* every comparison row carries a per-row `evaluation_leakage_status`. Same-pattern rows are isolated and excluded from all generalization-safe metrics. Currently, all three existing memory labels are same-pattern, yielding zero generalization-safe rows.

**Optimistic tuning.** If the M4B-1 policy is designed using the same rows on which it is evaluated, the policy is optimized to perform well on those specific cases, inflating results beyond what would hold on unseen data. *Mitigation:* a sealed 16-development / 8-holdout split is defined before any labels are inspected. Policy design and error analysis use the 16 development rows only. The 8 holdout labels are sealed until the refined policy is frozen and are evaluated exactly once (§6.7).

**Researcher degrees of freedom.** A small development set permits many
post-hoc trigger combinations, thresholds, subgroups, and definitions. Trying
several variants and reporting the most favorable one would overfit even if the
holdout remained technically sealed. *Mitigation:* EXP-023 permits at most one
approved deterministic candidate, requires at least three potentially
correctable development errors across two settings, freezes the rules and
hashes, and records deviations. Exploratory analyses are labeled exploratory
and cannot replace the preregistered primary analysis.

**Synthetic results mistaken for evidence.** Synthetic trials (EXP-004) exist for pipeline exercise and policy-risk screening only. They use rule-generated labels with a reviewer ID of `SYNTHETIC_NOT_HUMAN`. *Mitigation:* synthetic outputs are stored in isolated folders, explicitly labeled as non-evidence, and excluded from all claims. The evidence-consistency guard checks for the presence of synthetic artifacts in any claim-level reporting.

## 8.4 Conclusion validity (is the statistical basis adequate?)

Conclusion validity concerns whether the study has sufficient statistical power to detect real effects and whether the statistical methods are appropriate.

**Very small sample.** Only 27 variability patterns exist; at most 24 are generalization-safe; currently zero are labeled. Even with a full labeling, the sample is small enough that standard statistical tests may lack power, and point estimates may have wide confidence intervals. *Mitigation:* the evidence gates (§6.8) are explicit — 0 labels means not evaluable, 1–19 means pilot only with explicit small-sample threats, and ≥20 permits quantitative reporting with stated limitations. The thesis will not claim statistical significance from an 8-row holdout; it will report the results as a pilot with appropriate caveats.

**Paired benefit can hide paired harm.** Two systems can have similar aggregate
accuracy while a candidate corrects some baseline errors and breaks other
correct decisions. *Mitigation:* net correction
(`changed-and-correct - changed-and-wrong`) is the primary estimand, supported by
the full paired correctness matrix. Accuracy and macro-F1 are secondary.

**Unstable inference at small N.** Asymptotic intervals and tests can be
misleading with sparse classes and few discordant pairs. *Mitigation:* use
Wilson proportion intervals, a 10,000-replicate paired bootstrap with fixed seed
`20260721`, and describe the eight-row holdout only as a pilot. Exact McNemar is
reserved for the external set.

**No current delta is possible.** The current deterministic policy (`memory-informed-classifier-v1`) changes zero of 27 classifications. This means that, by construction, original and memory-informed accuracy are identical — no labeling can produce a difference under the current policy. *Mitigation:* this is reported as a structural fact, not as a negative result. The conservative policy reflects a deliberate design choice: the first version of the comparison should change nothing, to establish that the mechanism works without introducing any behavioral risk. Only a future, holdout-validated M4B-1.1 could change the comparison result.

**Single-reviewer risk.** If only one annotator's labels are available, the ground truth reflects one person's judgment, which may be idiosyncratic. *Mitigation:* the protocol requires two independent reviewers plus adjudication. Cohen's κ will be computed and reported. If only one reviewer's labels are available at the time of writing, the results will be explicitly labeled as preliminary single-reviewer evidence.

## 8.5 External validity (how far do results generalize?)

External validity concerns whether the findings generalize beyond the specific conditions of the study.

**Narrow scope.** The study covers two domains (Cheers cinema-booking, ParkWise parking system), two diagram types (UML use-case diagrams, UML class diagrams), one institution, one LLM (OpenAI gpt-4o), and one course context. The 27 variability patterns may not represent the full diversity of modeling situations encountered in practice. *Mitigation:* the scope is stated explicitly in every result table and claim. All conclusions are bounded by the studied settings, and cross-context transfer (cross-domain, cross-diagram, cross-institution) is identified as future work (§10.4). The thesis makes no claim beyond the studied settings.

**LLM stochasticity and version drift.** The committed Agent 4 outputs are a single sample from a specific model version (gpt-4o) with specific prompts and parameters. A different LLM version, temperature, or prompt phrasing might produce different classifications for the same student models. *Mitigation:* the baseline is frozen by reproducibility tag (`official-vego-ai-baseline`). All evaluation runs are deterministic and offline — they do not re-invoke the LLM but use the committed outputs. Re-runs with different model versions would be treated as separate experiments with separate baselines.

**Memory sparsity.** The judgment memory contains only three entries, all from the Cheers UCD setting. Cross-setting reuse (using a memory from Cheers UCD to inform a ParkWise CD classification) is untested for correctness, and the retrieval matching may not be robust to domain or diagram-type differences. *Mitigation:* the leakage discipline (§6.5) separates cross-setting reuse from same-pattern reuse. Cross-setting correctness is deferred to the labeled evaluation, and the thesis does not claim that the current memory supports cross-domain generalization.

**Internal holdout is not external validation.** The sealed eight rows come from
the same overall artifact and educational context as the development rows. Even
a favorable holdout result would not establish transfer to a new cohort or
context. *Mitigation:* B4 is explicitly pilot-only. A formal improvement claim
requires EXP-025 on a new education-domain batch with at least 30 and preferably
48 independently adjudicated rows, a policy frozen before data inspection, and
all statistical and subgroup-safety gates.

**External replication may still be narrow.** A new education batch improves
temporal or cohort separation but does not automatically establish transfer to
other institutions, model types, languages, or clinical settings. *Mitigation:*
the formal claim remains scoped to the sampled education context. Clinical
performance and cross-domain transfer remain out of scope.

## 8.6 Ethical and data-governance threats

**Human-subject considerations.** The expert annotators who label the blind sheets are human participants providing professional judgments. Depending on institutional requirements, this may require ethics review or IRB approval. *Mitigation:* the protocol requires that reviewer consent, anonymity, and any IRB documentation needs are confirmed with the supervisor before outreach. Reviewer identities are not disclosed in the thesis; labels are attributed to anonymized reviewer IDs.

**Data sensitivity.** Student models are pseudonymous — they are identified by case number within their setting, with no personal student information included in the data or in any published artifact. *Mitigation:* all reporting uses aggregate summaries, and a publishability check is required before any external release of raw data.

## 8.7 Interactions between threats

Several threats interact in ways that compound their effects. The small sample (§8.4) amplifies the impact of the narrow scope (§8.5): with only 27 patterns from two domains, even a few idiosyncratic labeling decisions could substantially affect accuracy metrics. The same-pattern leakage (§8.3) compounds the memory sparsity (§8.5): the three existing memory entries are the only available evidence for retrieval quality, and they are all same-pattern, so the retrieval mechanism has not been tested in the conditions (cross-pattern, cross-setting) where it is most valuable.

The conservative policy (§8.4) interacts with both the small sample and the construct validity: because the current policy changes zero classifications, the evaluation will initially measure only the *baseline's* accuracy against expert labels, not the artifact's effect on accuracy. This means that even with full labeling, the first evaluation cycle may show no difference between original and memory-informed classifications — a result that is by design, not a failure of the artifact.

## 8.8 Runtime, cybersecurity, and model-provenance threats

**Implementation divergence.** Maintaining legacy and unified paths can create
silent semantic drift. *Mitigation:* parity mode runs both paths from the same
immutable inputs in separate temporary directories and compares all
decision-relevant fields after normalizing only timestamps and run identifiers.
Any mismatch publishes the legacy result and fails the parity gate. Controlled
parity is compatibility evidence only; it does not validate classification
quality.

**Unsafe files and output paths.** Malformed JSON/CSV/ZIP inputs, archive
traversal, symlinks, oversized records, or an unauthorized output root could
corrupt evidence or expose local data. *Mitigation:* the unified I/O boundary
validates schemas, magic bytes, archive members, path containment, overwrite
policy, file size, and record count before atomic publication. Baseline output
directories are never allowed as unified destinations.

**Credential and interaction-log exposure.** API keys, raw prompts, model
responses, student data, feedback, or supervisor material could enter tracked
configuration or logs. *Mitigation:* plaintext keys in project/runtime
configuration are rejected; credentials come from environment or project
secret stores. Interaction logging defaults to `metadata_only`; full content is
an explicit local-only opt-in with redaction, rotation, size limits, and
retention. CI is API-free and scans the tree, candidate artifacts, and history
for prohibited material.

**Dependency and supply-chain drift.** A reproducibility claim can fail if
dependency resolution changes or third-party automation is mutable.
*Mitigation:* Python and Node environments are locked, legacy requirement files
are generated and freshness-checked, direct dependencies are audited, release
SBOMs are generated, and GitHub Actions are pinned to full commit identifiers.
Passing scans describe the checked revision; they are not a guarantee against
future vulnerabilities.

**Model alias drift.** The historical baseline requested `gpt-4o`, but the
served dated snapshot was not retained. A later call to the same alias may not
behave identically. *Mitigation:* preserve the committed Agent 4 output as B0,
record all available model metadata in future manifests, and keep EXP-029
blocked behind independent labels, a sealed comparison protocol, supervisor
approval, and a cost limit. No candidate model is promoted by Iteration 15.

## 8.9 Summary

Key threats are missing labels, leakage, small and unstable classes, policy
overfitting, and model drift. Dual review, a frozen split, paired analysis, a
one-time holdout, and external replication keep outcomes interpretable under
rules fixed in advance; none guarantees benefit.
