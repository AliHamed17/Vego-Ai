# Codex Next-Step Handoff Prompt and Verified Context

Verified: 2026-07-20. Use `docs/research/h-layer/program-status-snapshot-v1.json` and accepted manifests as authoritative when a narrative file disagrees.

## 1. Current State

- **Branch:** `agent/publish-hlayer-and-supervisor-package` at source revision `af191f07849a0bb883750eba135ede0cec908abb`; the July 21 worktree is deliberately dirty until the package is committed.
- **Latest accepted iteration:** Iteration 14, run `hlayer-20260720T173308Z-d79047f5e2`, kind `reliability_only`, verdict `NEUTRAL`, normalized `fa3debf25ba705224bfa27748aaee7cd92d72e8f50b6704ccea2ff9f6255651e`.
- **Iteration classes:** Iterations 001-007 are historical/pre-manifest; 008-014 are manifest-backed.
- **Replay suite:** EXP-006, 007, 008, 009, 010, and 012. EXP-005 is a separate human-label gate.
- **Conformance suite:** EXP-013-018; current offline run `HLAYER-CONFORMANCE-8c458da3755870930900` passed. It does not authorize live hooks.
- **Evidence boundary:** offline mechanism, contract, safety, and reproducibility evidence only. No accuracy, generalization, reduced-effort, benchmark-superiority, or clinical-performance claim.
- **EXP-005/012 gate:** 24 generalization-safe candidates, 0 supplied labels, 0 valid safe labels; EXP-012 is `NOT YET COMPUTABLE`. Do not create or infer labels.
- **Decision gate:** M-01 through M-06 are unrecorded and therefore effective `Deferred`. M-02 through M-05 do not authorize architecture defaults, routing defaults, verification defaults, role delegation, live hooks, correction application, or automatic memory reuse.
- **Protected behavior:** Agent 4, M4B-2, protected VEGO-AI paths, baseline output, evaluation policy, and runtime behavior remain unchanged.
- **MediVARIA:** proposal-only future research. Education remains the MSc empirical domain; there is no clinical data or clinical-performance evidence.

## 2. Required Start Checks

```powershell
.\scripts\refresh-tracking.ps1 -Pull
git status --short --branch
python scripts\check_evidence_consistency.py
python scripts\validate_hlayer_offline.py
python scripts\validate_hlayer_program.py
```

A validator failure is status drift or a defect. Resolve it before producing a claim or package.

## 3. Current Human-Facing Task

Use the July 21 supervisor package to:

1. Confirm or correct D1-D12 without altering the raw ASR.
2. Record M-01 through M-06 as `Accepted`, `Accepted with changes`, `Rejected`, or `Deferred`.
3. Approve or revise the blind expert-labeling protocol and two-reviewer/adjudication plan.
4. Keep EXP-005/012 stopped at zero labels.
5. Keep all H-layer implementation choices provisional until their explicit decisions and any separate implementation authorization exist.

## 4. Work Allowed Before Decisions

- Documentation, diagrams, presentation materials, deterministic builders, schema/content validators, read-only program overviews, and offline fixture analysis.
- EXP-005 protocol preparation and reviewer scheduling without prefilled labels.
- Proposal-only MediVARIA research questions and ethics/partner prerequisites.

## 5. Work Not Authorized

- No Agent 4, M4B-2, baseline output, protected path, active correction, live listener, prompt/context mutation, semantic/LLM verifier, automatic guideline rewrite, or trusted-memory runtime work.
- No deterministic policy tuning on the same rows intended for final evaluation.
- No clinical schema/runtime extension and no claim that transferability, alert reduction, or clinical benefit has been demonstrated.

## 6. Finish Rules

1. Run `.\scripts\verify-hlayer-all.ps1 -WithOverview` without suppressing failures.
2. Run package/browser/document validators relevant to the change.
3. Confirm the protected VEGO-AI diff is empty.
4. Run `.\scripts\agent-memory-finish.ps1` with a concise, exact summary.
5. Run `.\scripts\refresh-tracking.ps1 -Viz`, build the Confluence outbox, and run dashboard health.
6. Stage explicit paths only. Keep draft PR #8 unmerged unless the user separately asks for merge.
