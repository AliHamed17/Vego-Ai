# Evaluation Plan

This plan evaluates VEGO-AI as a staged human-AI co-reasoning artifact. The central question is whether reusable human judgment can be captured and later used responsibly in AI-assisted variability interpretation.

## Conditions

| Condition | Name | Implementation State | What Changes | Primary Evidence |
| --- | --- | --- | --- | --- |
| C0 | Original VEGO-AI | Available baseline | No human review, feedback, or memory layer. | Existing pipeline/evaluator outputs and Agent D variability classes. |
| C1 | Review queue | Implemented in M1 | Selective Intervention Policy flags cases and creates signed review items. | Queue size, trigger reasons, review coverage, signature stability. |
| C2 | Structured feedback | Implemented in M2 | Expert decisions are validated and attached to review items. | Feedback schema validation, resolved queue records, mismatch handling. |
| C3 | Reusable memory | Implemented in M3 | Reusable feedback becomes Human Judgment Memory with provenance and conflict detection. | Memory item count, skipped reasons, retrieval reasons, conflict status. |
| C4A | Memory advisory report | Implemented in M4A | Relevant memory is retrieved for Agent 4 patterns and emitted as advisory-only evidence. | Advice strength distribution, match reasons, conflict warnings, zero classification changes. |
| C4B | Memory-informed parallel comparison | Implemented in M4B-1; evaluation pending | Deterministic experimental module compares original Agent 4 output with a separate memory-informed result without changing baseline behavior. | Parallel classification delta, agreement with human judgment, leakage status, decision trace quality, failure cases. |

## Comparison Logic

- C0 establishes the original AI-only baseline.
- C1 measures whether review is selective rather than exhaustive.
- C2 measures whether human decisions can be captured as auditable structured records.
- C3 measures whether reusable knowledge can be built and retrieved transparently without changing AI behavior.
- C4A tests whether retrieved memory can be presented as useful advisory evidence without changing AI behavior.
- C4B tests whether retrieved memory improves or stabilizes later variability interpretation under a controlled experimental setting, without treating the comparison result as default VEGO-AI behavior.

## Metrics

| Dimension | Candidate Measures |
| --- | --- |
| Variability classification quality | Agreement with expert labels, precision/recall/F1 where labels are available, confusion patterns. |
| Human review effort | Number and proportion of cases queued, trigger distribution, unresolved/pending count. |
| Feedback quality | Schema validity, rationale completeness, signature mismatch rate, reusable flag rate. |
| Memory utility | Retrieved relevant judgments, advice strength, match reasons, conflict warnings, skipped reasons. |
| Stability | Repeated-run agreement and sensitivity to model/API/config changes. |
| Research validity | Threats, limitations, expert disagreement, artifact publishability status. |

## M4 Experiment Boundary

M4A is advisory-only and already merged. It generates `memory_advice.json` while keeping `ai_classification_changed=false`.

M4B-1 is implemented as a deterministic parallel-comparison experiment. It must not silently turn memory into default product behavior. It should now be evaluated as a controlled experiment that:

- selects a documented subset of cases,
- consumes relevant M4A memory advice without calling Agent 4,
- logs which memory items were supplied,
- compares outputs against C0-C3 records,
- records whether the memory helped, harmed, or had no effect,
- preserves conflicting human judgments as warnings requiring adjudication.
- preserves `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `memory_informed_differs_from_original`, `requires_human_review_after_memory`, `evaluation_leakage_status`, `decision_trace`, `policy_version`, and `human_memory_used`.
- keeps `ai_behavior_changed_in_baseline=false`.

The implementation contract is tracked in `docs/research/m4b-conditional-approval.md`.

## M4B-1 Deterministic Policy

| Advice case | Rule |
| --- | --- |
| No memory or weak advice | Keep the original classification. |
| Moderate agreement | Keep the original classification and add a support note. |
| Moderate disagreement | Keep the original classification and require human review. |
| Strong agreement | Keep the original classification and record stronger support. |
| Strong disagreement | Propose a human-supported alternative in the parallel comparison only. |
| Conflicting or ambiguous memory | Keep the original classification and require human review. |
| Guideline update memory | Keep the classification unless an explicit human class exists; flag guideline review. |

## Evaluation Leakage Guard

Every M4B-1 comparison item must set `evaluation_leakage_status` to one of:

- `none`
- `same_pattern_memory_used`
- `same_setting_memory_used`
- `cross_setting_memory_used`
- `unknown`

Same-pattern memory reuse can demonstrate the mechanism, but clean evaluation claims should use leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert-only holdout designs.

## Acceptance Criteria

- Every reported result maps to an experiment ID and code commit.
- Controlled artifacts remain local or ignored until publishability is approved.
- Reusable memory claims are limited to what M3, M4A, and future C4B evidence supports.
- The thesis distinguishes implemented mechanisms from planned PhD continuation work.
- Any C4B improvement claim reports leakage status and the deterministic policy version used.
