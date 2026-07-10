# Chapter 7 — Experimental Results and Current Evidence

> Draft. This chapter reports the evidence that is currently available and preserves the evidence boundary:
> mechanism, traceability, escalation, and reproducibility are supported; classification accuracy improvement
> is not yet evaluable because no generalization-safe expert labels have been supplied. Sources:
> `docs/research/evaluation-report.md`, `docs/PROGRESS_TRACKER.md`,
> `docs/dashboards/e2e-dashboard.generated.md`, `reports/generated/exp001/`,
> `reports/generated/exp002/`, `reports/generated/exp003/`, and
> `reports/generated/exp005_label_review/`.

## 7.1 Result status at the time of writing

The VEGO-AI thesis artifact is complete through M4B-1. The evaluation tooling (EXP-001 through EXP-005) is implemented, the bias-controlled annotation package is ready, and 94 tests pass. The empirical label gate, however, remains closed: no independent expert labels have been supplied, so the accuracy-effect question cannot yet be answered.

This chapter therefore reports a mixed result set: the system-level mechanism is demonstrated with concrete evidence, while the accuracy-effect question remains pending the execution of the independent expert annotation protocol (§6.6). The central evidence boundary is: **current evidence supports mechanism readiness, not accuracy improvement**.

| Evidence area | Current status | Thesis interpretation |
| --- | --- | --- |
| Artifact build M1–M4B-1 | Complete, merged, tagged, and reproducible | The reusable human-judgment layer exists and can be evaluated. |
| Dashboard and visualizer | Complete and validated | The artifact can be inspected through local reports and read-only research panels. |
| Evaluation tooling EXP-001–EXP-005 | Complete with 94 passing tests | The project has the required machinery for controlled evaluation. |
| Annotation package | Ready with blind sheets, leakage controls, and randomization | Expert-label collection can begin immediately upon supervisor approval. |
| Expert labels | 0 supplied real labels | Accuracy and generalization cannot be evaluated yet. |

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

**M1 — Human Review Queue.** The selective intervention policy generates 11 review queue items from the 27 variability patterns, a targeting rate of 40.7%. The trigger distribution is: `requires_human_review = true` (the most common), low/medium confidence, and `flag_for_guidelines_update`. This shows that the policy does not review everything — it focuses expert attention on the cases where the AI's own signals indicate uncertainty or a need for human input. The targeting rate is a design parameter: a more aggressive policy would queue more patterns (up to 100%) at the cost of higher human workload, while a more selective policy would queue fewer but risk missing important cases. The current policy uses the AI's own review signals, which is a principled starting point.

**M2 — Human Feedback Manager.** Four feedback entries have been attached to review queue items, all with valid schemas, complete rationales, and matching signatures. The feedback includes `approve` and `reclassify` decisions, each with an expert rationale explaining the reasoning. The signature-verification mechanism has been exercised: no mismatches have occurred, confirming that the baseline outputs are stable across runs.

**M3 — Human Judgment Memory.** Three of the four feedback entries have been promoted to reusable memory entries (the fourth was not marked as reusable). Each memory item carries a complete provenance chain linking it back to the specific feedback entry, review queue item, Agent 4 classification, and student models that prompted the review. The memory entries cover patterns from the Cheers UCD setting, providing same-setting evidence for retrieval testing.

**M4A — Memory Advisory Layer.** Eight of the 27 patterns receive advisory evidence, with advice strengths ranging from `none` to `moderate`. The advisory layer retrieves relevant memory items and presents them with explainable match reasons (domain match, diagram-type match, guideline overlap). Across all 8 advised patterns, `ai_classification_changed = false` holds — the original Agent 4 classification is preserved verbatim alongside the advisory evidence.

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
| Human-review-after-memory flags | 2 | Escalation mechanism works |
| Conflicting memory flags | 0 | No memory conflicts in current data |

The important result of EXP-001 is not an accuracy gain — it is that M4B-1 produces a complete, auditable comparison table while preserving original Agent 4 classifications. The two `requires_human_review_after_memory` cases demonstrate that the memory layer can identify patterns that need additional human attention after advice is considered, even when the comparison policy does not change the classification. The three available labels are same-pattern memory labels, so they are excluded from generalization-safe metrics and are useful only as mechanism-validation evidence confirming that retrieval and matching work correctly.

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

**Supported conclusions.** The VEGO-AI pipeline can be extended with a reusable human-judgment layer that operates as a complete, traceable chain from review trigger through structured feedback, provenance-tracked memory, advisory retrieval, and parallel comparison. The extension preserves the original baseline without modification — this is verified by 18 consistency checks running at every prompt. The selective intervention policy reduces the review scope from 27 patterns to 11, focusing expert attention where the AI's own signals indicate uncertainty. The evaluation methodology and annotation package are ready, with blind labeling sheets, leakage controls, anonymization, and randomization in place for immediate use upon supervisor approval.

**Not supported.** The current evidence does not support any of the following: that classification accuracy improves; that reusable human judgment generalizes across held-out settings or domains; that synthetic policy-screening results constitute real evidence; that same-pattern memory labels prove generalization; or that Agent 4's behavior should be changed. These conclusions require independent expert labels that have not yet been collected.

The distinction between these two sets of conclusions is itself a result worth reporting: the project has identified precisely what evidence is missing, designed a protocol to obtain it, and built the machinery to process it — making the gap between mechanism readiness and empirical proof as narrow and well-defined as possible.

## 7.8 Summary

The current results are strong for artifact readiness and mechanism validity, and intentionally silent on empirical accuracy. The artifact is built, tested (94 passing tests), and governed by evidence-consistency guards. The evaluation methodology is designed, the annotation package is prepared, and the evaluation harness is implemented. The remaining work is clearly human-gated: supervisor approval of the annotation protocol, expert labeling by two independent reviewers, adjudication, and a single evaluation run.

The thesis contribution at this point is the construction and governance of reusable human judgment in VEGO-AI — a complete, traceable, non-destructive layer that makes human expertise a persistent, retrievable asset rather than a transient correction. Quantitative accuracy evidence will complete the picture once independent expert labels are available, but the design-science contribution (the artifact and its methodology) stands on its own merits.
