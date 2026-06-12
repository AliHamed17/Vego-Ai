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
| C4B | Memory-assisted reclassification | Planned M4B | Agent 4 receives relevant memory advice as context in a controlled experiment. | Classification delta, agreement with human judgment, rationale quality, failure cases. |

## Comparison Logic

- C0 establishes the original AI-only baseline.
- C1 measures whether review is selective rather than exhaustive.
- C2 measures whether human decisions can be captured as auditable structured records.
- C3 measures whether reusable knowledge can be built and retrieved transparently without changing AI behavior.
- C4A tests whether retrieved memory can be presented as useful advisory evidence without changing AI behavior.
- C4B tests whether retrieved memory improves or stabilizes later AI variability interpretation under a controlled experimental setting.

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

M4B must not silently turn memory into default product behavior. It should run as a controlled experiment that:

- selects a documented subset of cases,
- supplies relevant M4A memory advice as explicit Agent 4 context,
- logs which memory items were supplied,
- compares outputs against C0-C3 records,
- records whether the memory helped, harmed, or had no effect,
- preserves conflicting human judgments as warnings requiring adjudication.
- preserves `original_agent4_classification`, `memory_advice`, `memory_informed_classification`, `classification_changed?`, `change_reason`, and `human_memory_used`.

## Acceptance Criteria

- Every reported result maps to an experiment ID and code commit.
- Controlled artifacts remain local or ignored until publishability is approved.
- Reusable memory claims are limited to what M3, M4A, and future C4B evidence supports.
- The thesis distinguishes implemented mechanisms from planned PhD continuation work.
