# Milestone Workflow Rules (Claude ↔ Codex ↔ ChatGPT)

Standing rules for VEGO-AI human–AI co-reasoning milestone work. Set after M1/M2/M3
landed on `main` without reviewable PRs because automation fast-forwarded `main`.

## Roles
- **Claude** — primary feature/milestone implementation agent.
- **Codex** — infrastructure, review, documentation, and gap-filling agent.
- **ChatGPT** — research orchestrator and architecture reviewer (approves merges to `main`).

## Branch / PR discipline
- Milestone CODE lives on a **feature branch** (e.g. `feature/human-judgment-memory`)
  and reaches `main` only via a **reviewed PR** approved by ChatGPT.
- Preserve the official baseline: tag `official-vego-ai-baseline` + branch
  `baseline/official-vego-ai` at `2eeccb1`. Do not merge `master` into `main` with
  `--allow-unrelated-histories`.

## Codex isolation rule
For future milestone work, especially M4B and later, Codex must:
- **Stop auto-syncing / fast-forwarding `main`** with Claude's feature commits.
- **Not push milestone code directly to `main`.**
- **Not modify** `VEGO-AI/framework`, `VEGO-AI/schemas`, `VEGO-AI/tests`,
  `VEGO-AI/docs`, or other milestone files while Claude is implementing, unless
  explicitly instructed.
- Review/test/document/propose fixes on a **review/fix branch** or in **PR comments**,
  not directly on `main`.
- `main` receives milestone code only **after ChatGPT review**.

Rationale: M1–M4A did not change AI behavior, so accidental fast-forwards were low
risk. **M4B may change AI behavior**, so unreviewed merges to `main` are not acceptable.

> Note: enforcement of the Codex side is the user's/ChatGPT's responsibility; this file
> records the rule both agents should read. Claude cannot control Codex from its session.

## Milestone plan
- M1 — review-need detection (done).
- M2 — structured feedback capture (done).
- M3 — reusable judgment memory: storage + explainable retrieval (done).
- **M4A — memory advisory layer**: retrieve relevant judgments per Agent 4 pattern,
  emit an advisory report, **no classification change** (done; PR #2 reviewed by
  Codex and squash-merged to `main` as `ecd0972`).
- **M4B — controlled reclassification**: memory-informed Agent 4 re-classification with
  original-vs-informed comparison (design-only until separately reviewed).
