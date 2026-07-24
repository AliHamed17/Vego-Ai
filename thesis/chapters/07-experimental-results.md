# Chapter 7 — Experimental Results and Current Evidence

> Draft. This chapter reports the evidence that is currently available and preserves the evidence boundary:
> mechanism, traceability, escalation, and reproducibility are supported; classification accuracy improvement
> is not yet evaluable because no generalization-safe expert labels have been supplied. Sources:
> `docs/research/evaluation-report.md`, `docs/PROGRESS_TRACKER.md`,
> `docs/dashboards/e2e-dashboard.generated.md`, `reports/generated/exp001/`,
> `reports/generated/exp002/`, `reports/generated/exp003/`, and
> `reports/generated/exp005_label_review/`.

## 7.1 Result status at the time of writing

The VEGO-AI thesis artifact is complete through M4B-1. The evaluation tooling
through EXP-018 is present, the bias-controlled annotation package is ready, and
the accepted verification record reports the VEGO-AI and research-script suites
passing; exact counts remain attached to the dated verification manifest.
EXP-019–EXP-027 are preregistered specifications, not
completed results. The empirical label gate remains closed: no independent
expert labels have been supplied, so the accuracy-effect question cannot yet be
answered.

This chapter therefore reports a mixed result set: the system-level mechanism is demonstrated with concrete evidence, while the accuracy-effect question remains pending the execution of the independent expert annotation protocol (§6.6). The central evidence boundary is: **current evidence supports mechanism readiness, not accuracy improvement**.

| Evidence area | Current status | Thesis interpretation |
| --- | --- | --- |
| Artifact build M1–M4B-1 | Complete, merged, tagged, and reproducible | The reusable human-judgment layer exists and can be evaluated. |
| Dashboard and visualizer | Complete and validated | The artifact can be inspected through local reports and read-only research panels. |
| Evaluation and conformance tooling EXP-001–EXP-018 | Accepted mechanism, offline, synthetic, and conformance records | The project has machinery for controlled evaluation; evidence classes remain separate. |
| Accuracy-evidence roadmap EXP-019–EXP-027 | Preregistered specifications | No new empirical result is implied. |
| Annotation package | Ready with blind sheets, leakage controls, and randomization | Expert-label collection can begin immediately upon supervisor approval. |
| Expert labels | 0 supplied real labels | Accuracy and generalization cannot be evaluated yet. |

### 7.1.1 B0–B5 progress view

The baseline ladder separates what exists from what still requires human or
external evidence:

| Baseline | Current status | Evidence available | Next gate |
| --- | --- | --- | --- |
| B0 Frozen Agent 4 | Implemented | 179 models, 27 patterns, immutable outputs | Continue hash checks |
| B1 Human-judgment mechanism | Implemented | 11 queue items, 3 memories, 8 advice items, 27 comparisons, 0 changes | Independent validity audit |
| B2 Expert-labeled baseline | Pending expert input | 0/24 safe labels | EXP-019 calibration and EXP-020 labeling |
| B3 Deterministic candidate | Proposal — not approved | No candidate record | ≥3 correctable development errors across ≥2 settings plus approval |
| B4 Sealed holdout | Blocked | 8 rows sealed | Freeze B3 before opening |
| B5 External replication | Proposal — not approved | No external batch | New education batch, minimum 30 and target 48 |

This view is progress toward *stronger evidence*, not a graph of improving
accuracy. B0 and B1 are complete engineering and mechanism baselines. B2–B5 are
gated research stages whose outcomes may be positive, null, mixed, or harmful.

> **Figure 7.2.** B0–B5 evidence-maturity ladder. See
> `thesis/figures/fig-7-2-baseline-evidence-ladder.mmd`.

## 7.2 Prototype-scale evidence

The current VEGO-AI run covers four settings across two domains (Cheers and ParkWise) and two diagram types (use-case and class diagrams). The following table reports the scale at which the artifact operates, drawn from the local dashboard snapshot.

| Measure | Value |
| --- | ---: |
| Student model cases | 179 |
| Recurring variability patterns | 27 |
| Human-review queue items (M1) | 11 |
| Resolved feedback entries (M2) | 4 |
| Reusable judgment-memory entries (M3) | 3 |
| Memory-advice items (M4A) | 8 |
| M4B-1 comparison rows | 27 |
| Baseline AI classifications changed by the memory layer | 0 |

These counts establish that the artifact operates at a scale sufficient to exercise the full workflow: review items are generated, feedback is attached, memories are stored, advice is retrieved, and comparisons are produced. The scale is, however, modest — 27 patterns across four settings — which means that future quantitative claims must be framed as pilot evidence unless additional labeled runs are conducted. This limitation is acknowledged in the evidence gates (§6.8) and the threats to validity (Chapter 8).

## 7.3 Mechanism results by milestone

The mechanism evidence shows that reusable human judgment is represented as a traceable chain rather than a single model-output change. Each milestone contributes a distinct layer to the chain, and each layer can be inspected independently.

**M1 — Human Review Queue.** The selective intervention policy generates 11
review queue items from the 27 variability patterns, an observed queue-item to
pattern ratio of 40.7%. The trigger distribution includes
`requires_human_review = true`, low/medium confidence, and
`flag_for_guidelines_update`. This demonstrates selective routing rather than
reviewing every pattern. It does not yet demonstrate that the queued set contains
more expert-confirmed errors, that the routing is optimal, or that human time is
reduced; those questions are reserved for EXP-021, EXP-022, and EXP-026.

**M2 — Human Feedback Manager.** Four feedback entries have been attached to
review queue items, all with valid schemas, complete rationales, and matching
signatures. The feedback includes `approve` and `reclassify` decisions, each
with a human rationale explaining the reasoning. No signature mismatch appears
in the current records; independent baseline-hash checks, rather than this
absence alone, establish baseline integrity.

**M3 — Human Judgment Memory.** Three of the four feedback entries have been promoted to reusable memory entries (the fourth was not marked as reusable). Each memory item carries a complete provenance chain linking it back to the specific feedback entry, review queue item, Agent 4 classification, and student models that prompted the review. The memory entries cover patterns from the Cheers UCD setting, providing same-setting evidence for retrieval testing.

**M4A — Memory Advisory Layer.** Eight of the 27 patterns receive advisory
evidence, with advice strengths ranging from `none` to `moderate`. The advisory
layer retrieves candidate memory items through deterministic match reasons
(domain match, diagram-type match, guideline overlap). Across all eight advised
patterns, `ai_classification_changed = false` holds. Independent human judgment
of retrieval relevance and scope is still pending EXP-022.

**M4B-1 — Parallel Comparison.** All 27 patterns produce comparison records with complete decision traces. Under the current conservative policy (`memory-informed-classifier-v1`), zero of 27 memory-informed classifications differ from the original Agent 4 classifications. Two patterns are flagged as `requires_human_review_after_memory`, indicating that the memory layer has identified cases where the advisory evidence is ambiguous or conflicting enough to warrant additional human attention.

Taken together, these results support the design-science claim (Hevner et al., 2004) that a reusable human-judgment layer can be added to an AI-assisted domain-model assessment pipeline while preserving the original AI output. The chain is complete, traceable, and inspectable from review trigger through memory storage, advisory retrieval, and parallel comparison.

> **Figure 7.1.** Evidence flow from baseline through each milestone layer, annotated with current counts. See `thesis/figures/fig-7-1-evidence-flow.mmd`.

### Running example: "Customer as actor" in the results

The "Customer as actor" pattern (ucd_ch P6, introduced in §4.4) concretely illustrates the mechanism results. Agent 4 classified it as occasional variability with Medium confidence. M1 queued it for review (trigger: `medium_confidence`). A human expert reviewed it and disagreed: "Customer as an actor who places orders is a legitimate alternative interpretation, not a modeling error" (§5.6). The feedback was promoted to memory entry `HJM-ucd_ch-P6`, retrieved by M4A with `advice_strength = moderate`, and processed by M4B-1 under policy row `moderate_disagreement_keep_original_require_review`.

The result: the original Occasional classification is preserved in the comparison artifact, but `requires_human_review_after_memory = true` is set — this is one of the two review-after-memory flags in the EXP-001 table above. The row's `evaluation_leakage_status = same_pattern_memory_used` correctly excludes it from generalization-safe metrics. This single case demonstrates the full mechanism: selective triggering, structured disagreement capture, memory storage, advisory retrieval, conservative comparison, escalation, and leakage tagging — all operating on real VEGO-AI data.

## 7.4 EXP-001: mechanism and readiness evaluation

EXP-001 evaluates whether the M4B-1 comparison can be built and audited across the current run. It is a mechanism/readiness experiment, not an accuracy experiment — its purpose is to confirm that the evaluation infrastructure works correctly and that the comparison artifact is well-formed.

| Measure | Value | Interpretation |
| --- | --- | --- |
| M4B-1 comparison rows | 27 | Full coverage of all patterns |
| Settings covered | 4 | All four domain×diagram combinations |
| Expert labels from same-pattern memory | 3 | Mechanism validation only (leakage) |
| Generalization-safe expert-labeled rows | 0 | No generalization evidence available |
| Memory-informed differs from original | 0 | Conservative policy maintains all originals |
| Human-review-after-memory flags | 2 | Two policy-triggered escalation records; precision pending labels |
| Conflicting memory flags | 0 | No memory conflicts in current data |

The important result of EXP-001 is not an accuracy gain — it is that M4B-1 produces a complete, auditable comparison table while preserving original Agent 4 classifications. The two `requires_human_review_after_memory` records demonstrate that the configured policy can emit an escalation after advice is considered, even when the comparison policy does not change the classification. Whether those escalations correspond to cases that genuinely require additional expert attention is not yet known and is evaluated only after independent labels exist. The three available labels are same-pattern memory labels, so they are excluded from generalization-safe metrics and are useful only as mechanism-validation evidence confirming that retrieval and matching execute as specified.

## 7.5 EXP-002 and EXP-003: annotation readiness and labeling package

EXP-002 prepares the expert-labeling package, and EXP-003 implements the accuracy-improvement evaluation tooling. Together, they show that the project is ready to conduct the empirical evaluation once expert labels are collected.

The annotation package contains 27 labelable rows, of which 24 are generalization-safe candidates (the other 3 are same-pattern rows isolated in a mechanism-validation sheet). The blind labeling sheets hide all AI-derived fields — the original Agent 4 label, the memory-informed label, the advice strength, the leakage status, and the internal ranking — presenting reviewers with only neutral context: an anonymous identifier, the setting, the pattern description, affected cases, and the related guideline.

| Item | Value |
| --- | ---: |
| Total labeling rows | 27 |
| Generalization-safe candidates | 24 |
| Same-pattern mechanism rows (isolated) | 3 |
| Recommended labeling targets | 27 |
| Independent expert labels supplied | 0 |
| EXP-003 accuracy gate status | Cannot be evaluated yet |

The EXP-003 evaluation harness is fully implemented and tested. When expert labels are supplied, it will compute: per-row comparisons between original, memory-informed, and expert labels; leakage-tiered accuracy and macro-F1; a paired correctness table; error-type analysis; and escalation precision/recall. The harness enforces the evidence gates — it will refuse to assert accuracy improvement until at least 20 generalization-safe labels exist.

## 7.6 EXP-004 and EXP-005: policy-risk screening and the real-label gate

**EXP-004** is a synthetic-only policy-sensitivity simulation. It tests hypothetical policy variants (more aggressive classification-change rules) against synthetic truth scenarios to screen for policy risks — variants that might help in some scenarios but harm in others. EXP-004 is explicitly *not* empirical evidence: it uses synthetic labels generated by rule, not independent expert judgment. Its role is to inform the discussion (Chapter 9) about which policy directions are worth exploring after real labels are available, and which are risky.

The current EXP-004 result: under the current conservative policy, the memory-informed accuracy is identical to the original (Δ = 0.00 pp) regardless of the synthetic truth scenario, because the policy changes zero classifications. More aggressive hypothetical policies can produce synthetic gains but also synthetic losses, confirming that policy refinement requires real evidence and cannot be justified by synthetic screening alone.

**EXP-005** is the real-label gate. It is designed to validate any original-vs-memory-informed-vs-expert comparison once expert labels exist, including adjudication support (a third reviewer for disputed items), reliability metrics (Cohen's κ), and a reproducibility manifest that records the exact inputs, parameters, and outputs of each evaluation run.

| Item | Value |
| --- | ---: |
| Rows | 27 |
| Generalization-safe candidates | 24 |
| Safe memory disagreements | 4 |
| Review-after-memory cases | 2 |
| Supplied real labels | 0 |
| Generalization-safe valid labels | 0 |
| Gate status | Blocked |

Because there are zero supplied real labels, EXP-005 remains blocked. No M4B-1.1 policy refinement, M4B-2 LLM reclassification, or accuracy-improvement claim is justified at this stage.

## 7.7 What can and cannot be concluded

The evidence collected to date supports several conclusions about the artifact's mechanism and readiness, while clearly bounding what cannot yet be claimed.

**Supported conclusions.** The VEGO-AI pipeline can be extended with a reusable
human-judgment layer that operates as a complete, traceable chain from review
trigger through structured feedback, provenance-tracked memory, advisory
retrieval, and parallel comparison. The extension preserves the original
baseline without modification. The current policy selects 11 of 27 patterns for
review; this is an observed routing result, not evidence of optimal targeting or
reduced human effort. The evaluation methodology and annotation package are
ready, with blind labeling sheets, leakage controls, anonymization, and
randomization in place for use after supervisor approval.

**Not supported.** The current evidence does not support any of the following: that classification accuracy improves; that reusable human judgment generalizes across held-out settings or domains; that synthetic policy-screening results constitute real evidence; that same-pattern memory labels prove generalization; or that Agent 4's behavior should be changed. These conclusions require independent expert labels that have not yet been collected.

The distinction between these two sets of conclusions is itself a result worth reporting: the project has identified precisely what evidence is missing, designed a protocol to obtain it, and built the machinery to process it — making the gap between mechanism readiness and empirical proof as narrow and well-defined as possible.

### 7.7.1 Paired performance panel at the current gate

The paired matrix is deliberately unpopulated while safe N=0:

|  | Candidate correct | Candidate wrong |
| --- | ---: | ---: |
| Baseline correct | — | — |
| Baseline wrong | — | — |

| Metric | Current value |
| --- | --- |
| Baseline accuracy | Not yet computable |
| Candidate accuracy | Not yet computable |
| Baseline macro-F1 | Not yet computable |
| Candidate macro-F1 | Not yet computable |
| Net correction | Not yet computable |
| Paired p-value | Not yet computable |

Dashes are missing evidence, not zeros. The values are filled only from
adjudicated, generalization-safe records after the relevant gate opens.

### 7.7.2 Reliability and conformance progress after EXP-005

EXP-006–EXP-018 add observability, dosage, synthetic verification, determinism,
authority, provenance, and proposal-safety evidence. Their accepted status is
offline or synthetic, and they do not change the accuracy verdict:

- EXP-006–EXP-008 provide replay and Pareto/cap trade-off evidence without
  selecting a routing default.
- EXP-009/010 are `SYNTHETIC_NOT_HUMAN` rule fixtures and cannot validate expert
  behavior.
- EXP-012 correctly reports `NOT YET COMPUTABLE` at safe N=0.
- EXP-013–EXP-018 demonstrate offline conformance and safety properties only.
- Accepted Iteration 14 is `NEUTRAL`, reliability-only, and selects no default.

EXP-019–EXP-027 now define the path from reviewer calibration to external
replication. Their presence is planning progress, not an experiment result.

## 7.8 Summary

The current results are strong for artifact readiness and mechanism validity,
and intentionally silent on empirical accuracy. The artifact is built and
governed by evidence-consistency and protected-path checks. The evaluation
methodology is preregistered, the annotation package is prepared, and the
evaluation interfaces are implemented. The remaining decisive work is
human-gated: supervisor approval, reviewer calibration, two independent blind
returns, adjudication, and development-only error characterization.

The thesis contribution at this point is the construction and governance of reusable human judgment in VEGO-AI — a complete, traceable, non-destructive layer that makes human expertise a persistent, retrievable asset rather than a transient correction. Quantitative accuracy evidence will complete the picture once independent expert labels are available, but the design-science contribution (the artifact and its methodology) stands on its own merits.
