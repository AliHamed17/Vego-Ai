# Scientific Experiment Crosswalk

Last updated: 2026-08-01

Status: **planning crosswalk only; no experiment result or approval is created
by this document**

## Purpose and ID discipline

The enhanced Zoom-to-submission plan uses `SCI-EXP-01` through `SCI-EXP-06` as
plain-language study concepts. They are **not new canonical experiment IDs**.
Canonical execution, data, manifests, and results remain under the existing
`EXP-000` through `EXP-040` registry.

Apply these rules:

1. Cite a `SCI-EXP` label only as a proposal or presentation alias and always
   link it to the canonical experiment or experiments that execute the work.
2. Store protocols, inputs, outputs, and results under canonical `EXP` IDs. Do
   not create a second result set under a `SCI-EXP` folder.
3. Where the concept exceeds an existing protocol, record the gap and obtain a
   preregistration amendment or a newly approved canonical ID before execution.
   This crosswalk does not silently expand an approved experiment.
4. Preserve dependency order, sealed partitions, reviewer independence, and
   non-destructive baseline behavior from the canonical protocols.
5. Keep `IRIS-EXP-01` through `IRIS-EXP-10` separate. They assess meeting and
   closure assurance, not scientific outcomes.

## Crosswalk

| Planning label | Study / question | Intended comparison or evidence | Canonical experiment anchors | Coverage and required disposition | Current gate and permitted claim |
| --- | --- | --- | --- | --- | --- |
| `SCI-EXP-01` — Selective intervention | Study 1 / SQ1 | Compare never, always, uncertainty-triggered, and novelty-triggered human intervention; measure assessment quality, calibration, burden, and latency. | Mechanism inputs: [EXP-006](../../../experiments/EXP-006-hlayer-event-replay/README.md), [EXP-007](../../../experiments/EXP-007-dosage-mode-replay/README.md), [EXP-008](../../../experiments/EXP-008-early-trigger-mining/README.md), [EXP-013](../../../experiments/EXP-013-event-contract-fidelity/README.md), [EXP-015](../../../experiments/EXP-015-workload-bundling-fairness/README.md), and [EXP-016](../../../experiments/EXP-016-authority-timeout-safety/README.md). Human/evaluation chain: [EXP-019](../../../experiments/EXP-019-reviewer-calibration/README.md)–[EXP-026](../../../experiments/EXP-026-human-effort-study/README.md), especially EXP-021, EXP-022, EXP-023, EXP-024, and EXP-026. | Current replay protocols supply event, trigger, dosage, workload, and safety scaffolds. The exact four-arm comparison is not yet a frozen canonical protocol; add it only as an approved preregistered arm in the routing/effort evaluation chain or assign a new canonical ID through registry governance. | EXP-005/EXP-020 remain `0/24`; two reviewers and adjudication are absent. Existing replay findings are mechanism/Pareto evidence only. No optimal intervention, accuracy, calibration, effort, or latency benefit may be claimed. |
| `SCI-EXP-02` — Governed judgment reuse | Study 2 / SQ2 | Test compatible, conflicting, stale, and under-specified judgments for provenance, conflict detection, safe abstention, and unsafe-reuse rate. | Mechanism/safety anchors: [EXP-009](../../../experiments/EXP-009-hverify-seeded-conflict-dry-run/README.md), [EXP-016](../../../experiments/EXP-016-authority-timeout-safety/README.md), [EXP-017](../../../experiments/EXP-017-verification-provenance/README.md), and [EXP-035](../../../experiments/EXP-035-fault-injection-authority-safety/README.md). Human relevance and follow-up: [EXP-022](../../../experiments/EXP-022-routing-retrieval-validity/README.md) and [EXP-027](../../../experiments/EXP-027-ablation-robustness/README.md). | Existing synthetic fixtures cover bounded conflict, authority, provenance, and fail-closed behavior. Human judgments, longitudinal staleness, and the complete four-condition matrix are not validated. Freeze missing conditions as an approved protocol amendment before execution; EXP-027 remains post-primary and cannot rescue the primary analysis. | Synthetic and offline safety findings do not establish safe reuse with real experts or improved outcomes. Human retrieval validity is blocked by the zero-label chain. |
| `SCI-EXP-03` — Longitudinal reuse | Study 2 feeding Study 3 / SQ2 and SQ3 | Reapply reviewed judgments to later cases and versions; measure retrieval precision, acceptance, decay, maintenance effort, and error propagation. | Replication/effort/robustness anchors: [EXP-025](../../../experiments/EXP-025-external-education-replication/README.md), [EXP-026](../../../experiments/EXP-026-human-effort-study/README.md), [EXP-027](../../../experiments/EXP-027-ablation-robustness/README.md), [EXP-028](../../../experiments/EXP-028-model-execution-reproducibility/README.md), and [EXP-036](../../../experiments/EXP-036-scale-latency-reproducibility/README.md). | No current canonical protocol supplies a complete longitudinal repeated-measures design. Before data collection, preregister timepoints, version boundaries, memory exposure, expiry/revocation rules, repeated-review measures, attrition, and analysis under an approved canonical protocol or a new registry-approved ID. | Planned only. Current reproducibility and scale evidence is operational, not longitudinal human-reuse evidence. No decay, maintenance-effort, acceptance, or error-propagation result may be claimed. |
| `SCI-EXP-04` — Plan B transfer | Study 3 / SQ3 | Replicate the frozen common core in an authorized non-medical modeling or education setting and measure transfer degradation, traceability, workload, and reviewer agreement. | Primary anchor: [EXP-025](../../../experiments/EXP-025-external-education-replication/README.md). Preparation and interpretation: [EXP-019](../../../experiments/EXP-019-reviewer-calibration/README.md), [EXP-020](../../../experiments/EXP-020-independent-expert-labeling/README.md), [EXP-026](../../../experiments/EXP-026-human-effort-study/README.md), and [EXP-027](../../../experiments/EXP-027-ablation-robustness/README.md). | EXP-025 is the canonical Plan B replication path: minimum `N=30`, target `N=48`, frozen policy, two reviewers, adjudication, paired analysis, and preregistered harm checks. The authorized corpus/context and reviewer route still require approval. | Proposal only; not approved or run. This is the only planned formal-improvement gate, and every EXP-025 criterion must pass. Failure or null results remain reportable but do not support improvement. |
| `SCI-EXP-05` — Plan A medical transfer | Study 3 / SQ3 conditional extension | Run one bounded clinical transfer pilot with clinician-approved inputs, outcomes, interpretation, and governance. | No active canonical medical experiment exists. If all medical gates pass, methods may reuse the reviewer, replication, effort, and robustness controls from [EXP-019](../../../experiments/EXP-019-reviewer-calibration/README.md), [EXP-020](../../../experiments/EXP-020-independent-expert-labeling/README.md), [EXP-025](../../../experiments/EXP-025-external-education-replication/README.md), [EXP-026](../../../experiments/EXP-026-human-effort-study/README.md), and [EXP-027](../../../experiments/EXP-027-ablation-robustness/README.md), but those protocols do not authorize clinical work. | Keep this label conditional and unmapped to execution. Only after medical readiness reaches `6/6`, the clinical protocol and outcome are approved, and supervisors authorize the study may registry governance assign or approve a canonical medical protocol. Reusing methods must not relabel education evidence as medical evidence. | Medical readiness is `0/6`. No row-level access, clinical experiment, medical result, safety conclusion, or patient-benefit claim is permitted. At `0–5/6` on the fallback gate, Plan B remains the executable path. |
| `SCI-EXP-06` — Ablation and usability | Study 3 / SQ3 with Studies 1–2 attribution | Remove routing, retrieval/memory, conflict/governance, or provenance controls; separately study usability and effort. | Primary ablation anchor: [EXP-027](../../../experiments/EXP-027-ablation-robustness/README.md). Human-effort and interface anchors: [EXP-026](../../../experiments/EXP-026-human-effort-study/README.md), [EXP-031](../../../experiments/EXP-031-bigui-formative-usability/README.md), and [EXP-032](../../../experiments/EXP-032-bigui-decision-support/README.md). Safety/operational context: [EXP-035](../../../experiments/EXP-035-fault-injection-authority-safety/README.md) and [EXP-036](../../../experiments/EXP-036-scale-latency-reproducibility/README.md). | Keep ablation, human effort, and interface usability as separate canonical analyses with their own participants, outcomes, and gates. EXP-027 runs only after the primary external EXP-025 analysis and cannot tune or rescue it; EXP-031/032 apply only when the BigUI interface is the approved object of study. | Proposal/human-gated except for existing offline safety and operational evidence. No component-necessity, usability, decision-value, or effort conclusion exists yet. |

## Dependency view

The scientific aliases do not alter the canonical critical path:

1. `EXP-019` calibrates two human reviewers on excluded rows.
2. `EXP-020` supplies independent/adjudicated labels; this is the same human
   evidence gate represented by EXP-005 and is currently `0/24`.
3. `EXP-021` and `EXP-022` characterize development errors, routing, and
   retrieval without opening the sealed holdout.
4. `EXP-023` may freeze one deterministic parallel policy only if every entry
   condition and supervisor approval passes.
5. `EXP-024` is a one-time eight-row pilot, never a formal improvement gate.
6. `EXP-025` is the Plan B external replication and only planned formal
   improvement gate.
7. `EXP-026` measures human effort separately; queue counts are not effort
   evidence.
8. `EXP-027` follows the primary analysis and cannot tune or rescue it.
9. `SCI-EXP-05` stays outside execution while medical readiness is `0/6`.

## Study-contract linkage

| Study | Scientific aliases | Canonical evidence role |
| --- | --- | --- |
| Study 1 — Selective-intervention architecture | `SCI-EXP-01` | Existing replay/conformance artifacts support mechanism analysis; EXP-019–026 supply the future human and outcome evidence. |
| Study 2 — Governed judgment lifecycle | `SCI-EXP-02`, `SCI-EXP-03` | Existing conflict/provenance/fault fixtures support mechanism safety; longitudinal human reuse remains an explicit protocol gap. |
| Study 3 — Evaluation and transfer | `SCI-EXP-04`, conditional `SCI-EXP-05`, `SCI-EXP-06` | EXP-025 is Plan B; medical transfer has no active canonical experiment at `0/6`; EXP-026/027 and approved usability protocols provide separate effort, ablation, and interface evidence. |

## Global evidence boundary

- EXP-005 and EXP-020 remain at **0 of 24** generalization-safe human labels.
- Medical readiness remains **0 of 6** mandatory entry gates.
- `SCI-EXP-01` through `SCI-EXP-06` have no independent result state; cite the
  canonical experiment's actual status.
- No accuracy, generalization, calibration, effort-reduction, usability,
  medical-performance, patient-benefit, or deployment claim is created by this
  crosswalk.
