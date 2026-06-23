# Codex Next-Step Loop

This project can use a supervised one-cycle loop for "review", "continue", and "next step" prompts.

The loop is intentionally not a background service. Codex runs one safe cycle per prompt or per explicit script invocation, records the result, and stops at hard research gates.

## Command

Run from the repository root:

```powershell
.\scripts\run-codex-next-step.ps1
```

Useful options:

```powershell
.\scripts\run-codex-next-step.ps1 -OpenBlockedMaterials
.\scripts\run-codex-next-step.ps1 -RefreshWiki
.\scripts\run-codex-next-step.ps1 -RunHealth
.\scripts\run-codex-next-step.ps1 -RefreshWiki -RunHealth -NoOpen
.\scripts\run-codex-next-step.ps1 -NoOpen
```

For a structured review without the next-step loop:

```powershell
.\scripts\run-project-review.ps1
```

## What One Cycle Does

1. Reads current Git state.
2. Checks protected VEGO behavior paths:

   ```powershell
   git diff --name-status -- VEGO-AI\eval_output VEGO-AI\framework VEGO-AI\eval
   ```

3. Checks the real EXP-005 blind label sheet.
4. If real labels are present, complete, valid, and the sheet is closed, runs:

   ```powershell
   .\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet reports\generated\exp005_label_review\exp005_label_review_blind.csv -RunDownstream
   ```

5. If the gate is blocked, records the blocker and runs the structured project review cycle.
6. Optionally refreshes wiki/dashboard output and runs health checks.
7. Writes an ignored run summary:

   - `reports/generated/next_step_loop/last-run.json`
   - `reports/generated/next_step_loop/last-run.md`
   - `reports/generated/project_review/latest-review.json`
   - `reports/generated/project_review/latest-review.md`

## Hard Stops

The loop must stop instead of continuing when:

- EXP-005 has zero supplied real labels.
- Required expert-label fields are incomplete.
- A label value is invalid.
- The real blind CSV is locked/open.
- Protected VEGO behavior paths have diffs.

## Boundaries

The loop must not:

- invent expert labels;
- treat synthetic labels as real evidence;
- modify Agent 4;
- implement M4B-1.1 or M4B-2;
- call LLM/API services;
- add embeddings;
- overwrite baseline outputs or `VEGO-AI/eval_output`;
- publish controlled artifacts.

## Review Architecture

The structured review architecture is documented in `docs/operations/project-review-architecture.md`.

The review runner:

- reads memory, Git state, EXP-005 labels, generated evidence summaries, issues, risks, dashboards, and protected path diffs;
- writes ignored review outputs under `reports/generated/project_review/`;
- uses fixed verdicts: `green`, `yellow`, `blocked`, and `unsafe`;
- keeps approved claims separate from blocked claims.

## Supervisor Role

The supervisor decides when manual input is complete, especially real EXP-005 labels and adjudication. Codex may keep reviewing, documenting, validating, and preparing evidence, but real labels and research approval remain human-controlled gates.
