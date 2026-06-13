# Claude M4B Handoff Prompt

Paste this prompt into Claude after it has run the normal startup routine from `claude-bootstrap-prompt.md`.

```text
M4A is approved, reviewed by Codex, and merged.

Current milestone tags:
- milestone-m3-human-judgment-memory -> 5e109e5f9f2073d9cdc2325bcea2823d57c77882
- milestone-m4a-memory-advisory -> ecd097245c463089a5721d68b17d6b22a1005a43
- research-state-m4a -> 28289405fc7cb687665f949bf039355a97967c59

Your next work is two tasks only.

Task 1: Refresh the review artifact

Create:
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

Task 2: Draft M4B design only

Do not implement M4B.
Do not modify Agent 4.
Do not change AI behavior.
Do not create new M4B code yet.

M4B should be an experimental comparison layer, not a default behavior:

Original Agent 4 classification
        ↓
M4A memory advice
        ↓
M4B optional memory-informed reclassification
        ↓
Comparison report

The output design should preserve both original and memory-informed results:

{
  "original_agent4_classification": { },
  "memory_advice": { },
  "memory_informed_classification": { },
  "classification_changed": true,
  "change_reason": "",
  "human_memory_used": ["HJM-..."],
  "mode": "experimental"
}

The M4B design must include:
1. Goal
2. Non-goals
3. Inputs
4. Outputs
5. Where it plugs into the pipeline
6. Whether it calls Agent 4 resolve_with_answers or creates a separate comparison module
7. How memory advice is converted into structured answers
8. How original vs memory-informed classifications are compared
9. How conflicts are handled
10. How guideline updates remain human-approved
11. Evaluation plan
12. Risks
13. Acceptance criteria

Most important boundary:
M4B may generate a memory-informed alternative classification, but it must not overwrite the original Agent 4 result.
```
