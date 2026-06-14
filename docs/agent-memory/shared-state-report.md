# VEGO-AI Shared State Report For Claude And Codex

Last curated update: 2026-06-14 14:59 +03:00 by Codex.

Use this report as the high-level shared orientation for Claude and Codex. It summarizes the research framing, implemented milestone chain, governance boundaries, validation state, and next research direction. For exact moving status, always pair this report with `docs/agent-memory/current-state.md` and `git log -1`.

## 0. Purpose

This report keeps both agents aligned on:

- the research goal,
- what has already been built,
- what must not be changed,
- what is still pending,
- how Claude and Codex should divide responsibilities,
- what the next correct steps are.

The project is not simply "add human-in-the-loop." The contribution is:

> Transform human judgment into structured, reusable knowledge for AI-assisted domain model assessment.

## 1. Research Framing

### 1.1 Original VEGO-AI Baseline

The original VEGO-AI paper/system is an agentic AI framework for variability exploration in domain models.

It distinguishes between:

- Substantial variability: meaningful or valid modeling alternatives.
- Occasional variability: mistakes, misconceptions, or isolated deviations.

Original VEGO-AI has four main agents:

1. Language Advisor.
2. Domain Advisor.
3. Model Inspector.
4. Variability Explorer.

The original system can assess and explain model variability, but it does not operationalize reusable human judgment.

### 1.2 Research Question

The agreed research direction is:

> What approaches have been proposed to support human-AI collaboration in AI-assisted domain modeling and model assessment, and how can they inform the design of reusable human judgment mechanisms in systems such as VEGO-AI?

This is a literature-review-oriented and design-science-compatible question. VEGO-AI is the motivating case and artifact, not the only object of the literature review.

### 1.3 Core Contribution

The contribution is a reusable human-judgment layer for AI-assisted domain model assessment.

Formal statement:

> This work extends VEGO-AI from an automated agentic model-assessment pipeline into a staged human-AI co-reasoning framework. The extension selectively identifies cases requiring human review, captures expert feedback in structured form, stores reusable judgments with provenance and conflict handling, retrieves relevant past judgments as advisory evidence, and produces a non-destructive memory-informed comparison against the original AI classification.

Short statement:

> Human judgment becomes structured, reusable knowledge inside VEGO-AI.

## 2. Novelty Boundary

### 2.1 Do Not Claim Novelty For

Do not claim this project invented:

- human-in-the-loop AI,
- human feedback for AI,
- AI memory,
- explainable AI,
- active learning,
- generic human-AI collaboration.

These already exist in the literature.

### 2.2 What Can Stand Out

The narrower and stronger contribution is:

> Reusable human judgment for AI-assisted domain model variability assessment.

The distinctive pipeline is:

```text
AI detects uncertainty / review need
  -> human review item is created
  -> human feedback is captured structurally
  -> feedback becomes reusable Human Judgment Memory
  -> memory is retrieved as advisory evidence
  -> memory-informed comparison is produced without overwriting baseline AI output
```

This matters because domain modeling is interpretive. A deviation from a reference model may be:

- a real mistake,
- a valid alternative,
- a domain-specific interpretation,
- a language-level issue,
- a pedagogical issue,
- a guideline-update candidate,
- an ambiguity needing expert adjudication.

This is more specific than generic human-in-the-loop grading.

## 3. Implemented Milestone Chain

The implemented research pipeline is:

```text
Original VEGO-AI
  -> M1 Human Review Queue
  -> M1.2 Stable Review Identity
  -> M2 Human Feedback Manager
  -> M3 Human Judgment Memory
  -> M4A Memory Advisory Layer
  -> M4B-1 Deterministic Memory-Informed Comparison
  -> Dashboard + Visualizer UX for analysis
```

M4B-2 is not implemented and remains blocked.

## 4. Milestone Details

### M1 - Human Review Queue

Purpose: operationalize VEGO-AI's latent human-review signals.

VEGO-AI already had signals such as `requires_human_review`, confidence values, `Undetermined`, and `flag_for_guidelines_update`, but they were not used as an actionable review pipeline.

Added components:

- `VEGO-AI/framework/selective_intervention_policy.py`
- `VEGO-AI/framework/human_review_queue.py`
- `VEGO-AI/schemas/human_review_item.schema.json`
- `VEGO-AI/tests/test_human_review_queue.py`
- `VEGO-AI/docs/human_review_queue.md`

Output:

- `human_review_queue.jsonl`

Contribution:

- VEGO-AI can identify and persist cases where human judgment is needed.

### M1.2 - Stable Review Identity

Purpose: prevent human feedback from attaching to the wrong regenerated item.

Added fields:

- `review_signature`
- `source_pattern_id`
- `signature_fields`

Design:

- `review_id` remains human-readable.
- `review_signature` is deterministic and stable.
- M2 feedback joins by `review_id` and verifies `review_signature`.

Contribution:

- Human review items became reproducible and safe for future joins.

### M2 - Human Feedback Manager

Purpose: capture, validate, and attach structured human feedback to review items.

Added components:

- `VEGO-AI/framework/human_feedback_manager.py`
- `VEGO-AI/schemas/human_feedback.schema.json`
- `VEGO-AI/inputs/human_feedback.example.jsonl`
- `VEGO-AI/tests/test_human_feedback_manager.py`
- `VEGO-AI/docs/human_feedback_manager.md`

Output:

- `human_review_queue_resolved.jsonl`

Key rules:

- Match feedback by `review_id`.
- Verify `review_signature`.
- Signature mismatch is not applied silently.
- Original queue is not overwritten.
- Non-approve decisions require rationale.

Contribution:

- Human feedback is no longer informal free text. It becomes structured, validated, and linked to AI decisions.

### M3 - Human Judgment Memory

Purpose: turn resolved reusable feedback into persistent Human Judgment Memory.

Added components:

- `VEGO-AI/framework/human_judgment_memory.py`
- `VEGO-AI/schemas/human_judgment.schema.json`
- `VEGO-AI/tests/test_human_judgment_memory.py`
- `VEGO-AI/docs/human_judgment_memory.md`

Output:

- `human_judgment_memory.jsonl`

Ingestion rules:

- Ingest only resolved feedback.
- Require `reusable == true`.
- Require a valid signature.
- Require human rationale.

Stored information:

- `memory_id`
- `memory_signature`
- source review and feedback IDs
- human decision
- human rationale
- reuse scope
- provenance
- conflict status

Retrieval is transparent and does not use embeddings:

- domain match,
- diagram type match,
- guideline match,
- keyword overlap,
- explainable `match_reasons`.

Contribution:

- Human feedback becomes reusable Human Judgment Memory.

### M4A - Memory Advisory Layer

Purpose: retrieve relevant Human Judgment Memory as advisory evidence for future Agent 4 variability patterns.

Added components:

- `VEGO-AI/framework/memory_advisor.py`
- `VEGO-AI/schemas/memory_advice.schema.json`
- `VEGO-AI/tests/test_memory_advisor.py`
- `VEGO-AI/docs/memory_advisor.md`

Output:

- `memory_advice.json`

Hard boundary:

```text
advice_mode = advisory_only
ai_classification_changed = false
```

M4A never changes AI classifications.

Contribution:

- VEGO-AI can surface reusable human judgment as advisory evidence while preserving original AI output.

### M4B-1 - Deterministic Memory-Informed Comparison

Purpose: create a deterministic, non-destructive, parallel comparison between original Agent 4 output and memory-informed assessment.

Added components:

- `VEGO-AI/framework/memory_informed_classifier.py`
- `VEGO-AI/schemas/memory_informed_comparison.schema.json`
- `VEGO-AI/tests/test_memory_informed_classifier.py`
- `VEGO-AI/docs/memory_informed_classifier.md`

Output:

- `memory_informed_comparison.json`

Hard boundary:

```text
mode = experimental
ai_behavior_changed_in_baseline = false
```

M4B-1 must never overwrite:

- `agentD_variability_classes.json`
- `agentD_deviation_patterns.json`
- `VEGO-AI/eval_output/*`
- baseline outputs

Output includes:

- `original_agent4_classification`
- `memory_advice`
- `memory_informed_classification`
- `memory_informed_differs_from_original`
- `classification_changed_meaning`
- `human_memory_used`
- `decision_trace`
- `requires_human_review_after_memory`
- `evaluation_leakage_status`
- `policy_version`

Research guard:

- Same-pattern memory is useful for mechanism demonstration, but not proof of generalization.
- Generalization claims need leakage-aware evaluation.

Contribution:

- Reusable human judgment can support a parallel, measurable assessment comparison without changing the original VEGO-AI result.

## 5. Dashboard And Visualization Work

### Results Dashboard

Purpose: make VEGO-AI outputs inspectable visually and analytically.

Added components:

- `VEGO-AI/analysis/build_results_dashboard.py`
- `VEGO-AI/docs/results_dashboard.md`
- `VEGO-AI/tests/test_results_dashboard.py`
- `VEGO-AI/schemas/results_dashboard_snapshot.schema.json`

Generated outputs, intentionally ignored:

- `VEGO-AI/reports/results_dashboard/index.html`
- `VEGO-AI/reports/results_dashboard/metrics_snapshot.json`
- per-setting pages

Dashboard shows:

- model and case counts,
- Agent C scores,
- Agent D variability patterns,
- substantial, occasional, and undetermined counts,
- review queue counts,
- feedback counts,
- memory counts,
- memory advice counts,
- M4B-1 comparison counts when present,
- health warnings.

Contribution:

- The system is inspectable through visual research dashboards, not only raw JSON files.

### Visualizer UX Refresh - PR #7

Current status:

- PR #7 was real-display validated.
- PR #7 was marked ready and squash-merged into `main` on 2026-06-14.
- Merge commit: `78b261e033fc4f3f66170985a884aa5cd0a0cfd2`.
- Reproducibility tag: `research-state-visualizer-ux-clean`.

Main issue fixed:

- The original GUI could silently show a selected model with the wrong result JSON.
- Example risk: selected ParkWise model plus Cheers result.
- This was a serious correctness problem for research analysis.

PR #7 added:

- `VEGO-AI/vego_visualizer_delivery/visualizer_utils.py`
- `VEGO-AI/tests/test_visualizer_helpers.py`
- major updates to `VEGO-AI/vego_visualizer_delivery/visualize_compliance.py`
- visualizer README updates

UX fixes:

- case ID extraction from model filename,
- case ID extraction from `agentC_case_<id>.json`,
- exact `<case_id>_` model matching,
- mismatch banner,
- no matching model warning,
- auto-load matching model,
- search/status filters,
- summary counts,
- read-only M1/M2/M3/M4A/M4B-1 research panels.

Important boundary:

- The visualizer remains read-only.
- It must not edit feedback files, memory files, advice files, comparison files, or baseline outputs.

Real-display GUI validation passed for:

- mismatch warning,
- stale model clearing when no matching model exists,
- auto-load matching model,
- filters/search/details,
- read-only research panels,
- graceful diagram failure handling.

## 6. Validation State

Latest validated state after PR #7 merge:

- `python -m pytest VEGO-AI\tests -q` -> 93 passed.
- `python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery` -> passed.
- `.\scripts\project-health.ps1` -> passed.
- `.\scripts\research-health.ps1` -> passed.
- `.\scripts\dashboard-health.ps1 -RequireOutbox` -> passed.

System validation report:

- `VEGO-AI/reports/system_validation_report.md` is tracked as a research validation artifact.
- Latest report status: PASS after governance cleanup.

Governance warnings fixed:

- `scripts/research-health.ps1` allowlists only `VEGO-AI/analysis/build_results_dashboard.py`.
- `VEGO-AI/reports/system_validation_report.md` is tracked.
- local `baseline/official-vego-ai` branch tracking was restored.

No broad QA sweep is needed unless major behavior files change.

## 7. Git, Branch, And Governance State

Preserved baseline:

- tag `official-vego-ai-baseline`
- branch `baseline/official-vego-ai`

Important stable tags:

- `milestone-m3-human-judgment-memory`
- `milestone-m4a-memory-advisory`
- `research-state-m4a`
- `research-state-results-dashboard`
- `research-state-m4b1-deterministic-comparison`
- `research-state-visualizer-ux-clean`

Do not move stable tags. If a tag must change, get explicit user approval first.

Role split:

- Claude: primary feature implementation agent when working on feature branches.
- Codex: infrastructure, review, tests, docs, dashboards, fixes, gap filling, and guarded implementation when requested.
- ChatGPT/research orchestration: research framing, architecture review, thesis/evaluation direction.

Governance rule:

- Codex must not commit milestone implementation files directly to `main` unless the user explicitly asks for that exact action.
- Milestone code should use feature branch -> PR -> review -> merge.

Milestone-sensitive paths include:

- `VEGO-AI/framework/*`
- `VEGO-AI/schemas/*`
- `VEGO-AI/tests/*`
- `VEGO-AI/eval/*`
- `VEGO-AI/inputs/*`
- `VEGO-AI/docs/memory_*`
- `VEGO-AI/docs/*advisor*`

Root-level infrastructure, memory, dashboard, and Confluence work may be done separately, but must not pollute milestone PRs.

## 8. Blocked Or Deferred Work

### M4B-2

M4B-2 is not implemented and remains blocked.

M4B-2 would involve optional LLM/Agent 4 `resolve_with_answers` mode and requires:

- explicit design approval,
- API key and budget decision,
- strict experimental mode,
- non-destructive output,
- baseline preservation,
- separate evaluation.

Do not implement M4B-2 now.

### Live Confluence Sync

Live Confluence sync remains blocked because Atlassian Rovo lacks explicit access to the target cloud:

```text
724252a1-a5b7-45a5-b6ec-27a8292197ec
```

This is not a VEGO-AI research blocker. Local dashboards, Confluence outbox, and manual sync pack are ready.

## 9. Strict Research Review

### 9.1 What Is Useful

The implemented pipeline is useful because it creates a complete path:

```text
AI uncertainty
  -> human review
  -> structured feedback
  -> judgment memory
  -> advisory retrieval
  -> parallel comparison
```

This is a design-science artifact for reusable human judgment in AI-assisted model assessment.

### 9.2 What Is Not Yet Proven

Engineering validation is strong, but empirical research validation is not complete.

Do not claim:

- the system improves VEGO-AI accuracy,
- memory-informed classification is better,
- reusable judgment generalizes.

until evaluation proves it.

Current safe claim:

- the system enables structured, reusable human judgment and produces controlled artifacts for evaluating its effect.

### 9.3 Biggest Current Weakness

The main weakness is evaluation.

Need to prove:

- Are review triggers good?
- Does structured feedback capture useful expert knowledge?
- Does memory retrieve relevant judgments?
- Does M4A advice help reviewers?
- Does M4B-1 comparison align better with expert labels?
- Does memory reduce repeated human effort?
- Does the system generalize beyond same-pattern memory?

### 9.4 Leakage Warning

Same-pattern memory is useful for mechanism validation, but not proof of generalization.

If `HJM-ucd_ch-P5` is used to evaluate `ucd_ch-P5`, label it as:

```text
same_pattern_memory_used
```

Generalization evaluation should use:

- leave-one-pattern-out,
- cross-setting,
- cross-domain,
- cross-diagram,
- expert holdout.

## 10. Next Steps

Immediate next step:

1. Review and merge PR #6 schema hardening if clean.
2. Keep M4B-2, Agent 4 calls, LLM/API calls, embeddings, baseline output overwrites, and non-read-only visualizer behavior changes blocked.
3. Refresh the artifact bundle after PR #6 / health follow-up decisions.
4. Move from implementation to evaluation design.

Post-merge validation for PR #6 or future safe merges:

```powershell
python -m pytest VEGO-AI\tests -q
python -m compileall -q VEGO-AI\framework VEGO-AI\eval VEGO-AI\analysis VEGO-AI\vego_visualizer_delivery
.\scripts\project-health.ps1
.\scripts\research-health.ps1
.\scripts\dashboard-health.ps1 -RequireOutbox
```

Expected:

- all pass,
- no baseline outputs modified,
- no AI behavior changed.

## 11. Evaluation Phase

After the technical merge loop closes, stop adding modules and move to evaluation.

Needed evaluation table:

| Research Question | Metric |
| --- | --- |
| Where does VEGO-AI need human review? | Review queue count, trigger reasons. |
| How much feedback becomes reusable? | Resolved feedback, `reusable=true` count. |
| Does memory retrieve relevant judgments? | Match count, match reasons, human relevance rating. |
| Does advisory memory help? | `advice_strength` distribution and reviewer usefulness rating. |
| Does M4B-1 differ from original? | `memory_informed_differs_from_original`. |
| Where is human still needed? | Conflicts, moderate disagreements, `requires_human_review_after_memory`. |
| Does memory improve alignment with expert labels? | Original vs memory-informed vs expert labels. |
| Does memory reduce repeated review? | Repeated questions avoided, memory-hit rate. |

The thesis should shift from implementation to evidence.

## 12. Thesis Contribution Statement

Use this as the main contribution statement:

> This work extends VEGO-AI with a reusable human-judgment layer for AI-assisted domain model assessment. The extension selectively identifies cases requiring human review, captures expert feedback in a structured schema, stores reusable judgments with provenance and conflict handling, retrieves relevant past judgments as advisory evidence, and produces a non-destructive memory-informed comparison against the original AI classification.

Short version:

> The contribution is a reusable human-judgment layer for AI-assisted domain model assessment.

## 13. What To Avoid

Do not implement now:

- M4B-2,
- Agent 4 `resolve_with_answers` integration,
- LLM-based reclassification,
- automatic guideline rewriting,
- feedback editing inside GUI,
- embeddings,
- default memory-informed override of Agent 4.

Do not claim:

- the system improves accuracy.

until evaluation proves it.

Instead claim:

- the system enables structured, reusable human judgment and supports controlled evaluation of its effect.

## 14. Current Status Summary

The project currently has:

- strong research idea,
- strong design-science artifact,
- good implementation architecture,
- good QA/test coverage,
- dashboard and visualizer support,
- preserved baseline,
- clear governance.

It still needs:

- PR #6 schema hardening review,
- artifact refresh,
- research evaluation,
- comparison against expert labels,
- write-up.

Strict assessment:

- Strong prototype.
- Strong MSc direction.
- Potential PhD seed.
- Not yet a proven empirical research result.

The next major milestone should be evaluation, not more features.
