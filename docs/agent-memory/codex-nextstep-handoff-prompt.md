# Codex Next-Step Handoff Prompt and Verified Context

Verified: 2026-07-11. Use the manifests and decision snapshot as authoritative if a narrative file disagrees.

## 1. Current State

- **Evidence boundary:** offline mechanism, contract, and reproducibility evidence only. Do not call the program accuracy-ready, generalization-ready, or clinically validated.
- **Latest numbered snapshot:** iteration 012 at `reports/generated/hlayer_iterations/iter_012/`; run `hlayer-20260711T123453Z-6cca11a0c8`; kind `reliability_only`; verdict `NEUTRAL`.
- **Canonical replay suite:** six experiments — EXP-006, EXP-007, EXP-008, EXP-009, EXP-010, and EXP-012. EXP-005 is a separate human-label gate; EXP-013–018 form a separate six-experiment conformance suite. EXP-004 is not wired into the canonical H-layer replay runner.
- **Decision state:** M-02 through M-05 remain deferred; the generated decision snapshot is `offline_only`; no live hook, prompt/context mutation, automatic memory reuse, or correction application is authorized.
- **EXP-005 gate:** 0 supplied labels and 0 validated generalization-safe labels. EXP-012 reports `NOT YET COMPUTABLE`. Do not infer or auto-fill labels.
- **Protected paths:** do not modify `VEGO-AI/framework/`, `VEGO-AI/schemas/`, `VEGO-AI/tests/`, baseline execution paths, Agent 4 behavior, or evaluation logic without the required branch, allowed-touch approval, and reviewed PR.

Key files:

- `reports/generated/hlayer_iterations/iter_012/iteration_manifest.json`
- `reports/generated/hlayer_suite_manifest.json`
- `reports/generated/h_layer_decisions/decision_snapshot.json`
- `docs/research/h-layer/experiment-iteration-ledger.md`
- `docs/research/h-layer/feedback-learning-rlhf-plan.md`
- `docs/research/h-layer/prompt-architecture-guide.md`
- `scripts/hlayer_prototype/hlayer-prototype-scaffold.py`

## 2. Required Start-of-Session Checks

```powershell
git status --short --branch
python scripts/check_evidence_consistency.py
python scripts/validate_hlayer_offline.py
python scripts/validate_hlayer_program.py
```

Treat a validator failure as status drift or an implementation defect; do not work around it with a narrative claim.

## 3. Actionable Tasks

### Task A — Prepare the July 15 supervisor demo

Use only the isolated offline demo output directory. Demonstrate interaction design and deterministic checks; do not describe the demo records as trusted memory or empirical evidence.

```powershell
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --dry-run
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --test-conflict
python -B scripts/hlayer_prototype/hlayer-prototype-scaffold.py --mock-session --output-dir <temporary_directory>
```

For a live session, show the evidence attached to each selected queue item. An override must go only to an adjudication-candidate log and remain `needs_adjudication`; it must never enter ordinary feedback memory.

### Task B — Advance EXP-005 only after real labels arrive

When a supervisor/expert returns a saved and closed CSV or workbook:

```powershell
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <path_to_excel_or_csv>
```

Resolve validation errors before any downstream run. At 0 safe labels, stop. At 1–19 valid safe labels, results remain pilot-only. Do not run or report a quantitative accuracy result unless the validated gate permits it.

### Task C — Offline Vector 1 feedback-generalization proposal

Run the proposal-only generator. It may group only verified or supervisor-adjudicated, allowlisted-origin records with `trusted_memory_eligible = true`, reusable scope, provenance, and a companion `trusted-feedback-export-validator-v1` manifest binding the exact input hash and eligible record IDs. Current informal, demo, synthetic, and pending-adjudication records must be excluded.

```powershell
# Current gate check: produces zero candidates.
python scripts/feedback_generalizer.py

# Future validated export: still produces proposal-only requests.
python scripts/feedback_generalizer.py --input <trusted_feedback_export.json> --trusted-manifest <validated_trusted_export_manifest.json>
```

Without a valid companion manifest, the expected current outcome is `BLOCKED_NO_VERIFIED_FEEDBACK`, with zero candidate rules. The generated S7 synthesis requests and `synthesized_meta_rules.json` are provisional artifacts with `runtime_eligible = false`. Do not call an LLM, inject Agent B, or alter a runtime prompt until M-05 and separate implementation authorization are recorded.

## 4. Finish Rules

- Re-run the three validators and relevant targeted tests.
- Confirm `git diff --name-status -- VEGO-AI/framework VEGO-AI/schemas VEGO-AI/tests VEGO-AI/eval` is empty.
- Refresh project memory/tracking using the repo workflow and record commands/results.
- Keep synthetic, demo, offline replay, real-label, and decision evidence visibly separate.
