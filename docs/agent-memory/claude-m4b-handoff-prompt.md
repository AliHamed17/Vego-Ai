# Claude M4B-1 Handoff Prompt

Status: historical / superseded. M4B-1 is now implemented and merged. Keep this file for provenance only; use `docs/agent-memory/shared-state-report.md` and `docs/research/evaluation-report.md` for current direction.

Paste this prompt into Claude after it has run the normal startup routine from `claude-bootstrap-prompt.md`.

```text
M4A is approved, reviewed by Codex, merged, and tagged.

Current milestone tags:
- milestone-m3-human-judgment-memory -> 5e109e5f9f2073d9cdc2325bcea2823d57c77882
- milestone-m4a-memory-advisory -> ecd097245c463089a5721d68b17d6b22a1005a43
- research-state-m4a -> 28289405fc7cb687665f949bf039355a97967c59

Read these files first:
- docs/agent-memory/compiled-memory.md
- docs/research/m4b-conditional-approval.md
- docs/research/evaluation-plan.md
- experiments/EXP-001-memory-assisted-agent4-controlled-experiment/README.md
- docs/agent-memory/milestone-workflow-rules.md

You have two tasks.

Task 1: Refresh the review artifact

Create ignored local review artifacts:
- artifacts/vego-ai-M1-M2-M3-M4A-changes.zip
- artifacts/M1-M2-M3-M4A-manifest.md

The ZIP should include:
- all M1 files
- all M2 files
- all M3 files
- all M4A files
- modified orchestrator.py and evaluator.py hooks if relevant to M1-M4A history
- schemas
- docs
- tests
- example feedback files
- .gitignore changes if relevant

The manifest should include:
- official baseline commit
- M3 commit
- M4A merge commit
- current research-state commit
- files by milestone
- tests run
- CLI reproduction commands
- confirmation that M4A is advisory-only and does not change AI behavior

Task 2: Implement M4B-1 only after confirming the design contract

M4B-1 is conditionally approved as:

deterministic, experimental, parallel comparison

M4B-1 must never overwrite the original Agent 4 output and must never modify baseline eval_output.

Before coding, confirm that the design includes:
1. field name memory_informed_differs_from_original
2. ai_behavior_changed_in_baseline=false
3. policy_version=memory-informed-classifier-v1
4. decision_trace on every comparison item
5. requires_human_review_after_memory
6. evaluation_leakage_status values:
   - none
   - same_pattern_memory_used
   - same_setting_memory_used
   - cross_setting_memory_used
   - unknown
7. deterministic rules:
   - no memory -> keep original
   - weak advice -> keep original
   - moderate agreement -> keep original, support note
   - moderate disagreement -> keep original, requires human review
   - strong agreement -> keep original, stronger support
   - strong disagreement -> propose memory-supported alternative in parallel only
   - conflicting advice -> keep original, requires human review
   - ambiguous human decision -> keep original, requires human review
   - guideline update memory -> keep classification unless explicit human classification exists; flag guideline review

Approved future implementation scope:
- VEGO-AI/framework/memory_informed_classifier.py
- VEGO-AI/schemas/memory_informed_comparison.schema.json
- VEGO-AI/tests/test_memory_informed_classifier.py
- VEGO-AI/docs/memory_informed_classifier.md

Do not implement M4B-2.
Do not call Agent 4.
Do not use resolve_with_answers.
Do not use LLMs.
Do not use embeddings.
Do not use API keys.
Do not modify visualizer.
Do not overwrite original Agent 4 outputs.
Do not modify baseline eval_output.

Output only:
- memory_informed_comparison.json

The future schema must enforce:
- mode = experimental
- ai_behavior_changed_in_baseline = false
- required original classification, memory advice, memory-informed classification, human memory used, decision trace, policy version, leakage status, and human-review flag

Acceptance criteria:
1. It writes memory_informed_comparison.json only.
2. It never overwrites agentD_variability_classes.json.
3. It never modifies eval_output baseline files.
4. It has no LLM calls.
5. It has no OpenAI/API calls.
6. It has no embeddings.
7. It has no Agent 4 prompt changes.
8. It has no visualizer changes.
9. It preserves original_agent4_classification verbatim.
10. It sets ai_behavior_changed_in_baseline=false.
11. It includes policy_version and decision_trace.
12. It marks evaluation leakage when memory comes from the same pattern.
13. It handles conflicting memory by requiring human review.
14. All M1-M4A tests still pass.
15. New M4B-1 tests pass.

Workflow:
- create/switch to branch: feature/memory-informed-comparison
- commit there, not on main
- open PR into main
- stop if Codex or Claude has touched M4B implementation files directly on main

Codex isolation reminder:
Codex will not commit directly to main for files under:
- VEGO-AI/framework/
- VEGO-AI/schemas/
- VEGO-AI/tests/
- VEGO-AI/eval/
- VEGO-AI/inputs/
- VEGO-AI/docs/memory_*
- VEGO-AI/docs/*advisor*

M4B touches the AI-decision boundary, so branch/PR discipline is mandatory.
```
