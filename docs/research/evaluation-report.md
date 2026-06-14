# Evaluation Of Reusable Human Judgment In VEGO-AI

Last curated update: 2026-06-14 18:52 +03:00 by Codex.

Status: initial EXP-001 mechanism/readiness evaluation run completed. Generalization-safe expert-label evaluation is still pending.

## Evaluation Position

VEGO-AI is now past the core implementation phase through M4B-1. The implemented artifact supports the claim that VEGO-AI can be extended with a reusable human-judgment layer that enables human-AI co-reasoning in domain model assessment without replacing the original AI decision pipeline.

The next work is empirical evaluation, not additional feature building.

## Frozen Implementation Anchors

| State | Anchor | Use |
| --- | --- | --- |
| Official baseline | `official-vego-ai-baseline` / `baseline/official-vego-ai` | Original VEGO-AI preservation. |
| M4B-1 implementation baseline | `research-state-m4b1-deterministic-comparison` / `944c922` | Primary implementation freeze for M1-M4A + dashboard + M4B-1. |
| Visualizer UX validated state | `research-state-visualizer-ux-clean` / `78b261e` | Model/result mismatch fix and read-only analysis UI. |
| Current coordination state | `main` / latest pushed commit | Memory, dashboard, and documentation sync. |

Do not move stable tags. Any future implementation work should use a new branch/PR and must not overwrite baseline outputs.

## Artifact Bundle

GitHub release:

- Tag: `research-state-m4b1-deterministic-comparison`
- Release title: `M1-M4A + Dashboard + M4B-1 (944c922)`
- ZIP asset: `vego-ai-M1-M4A-dashboard-M4B1-changes.zip`
- Manifest asset: `M1-M4A-dashboard-M4B1-manifest.md`

These assets are suitable for external technical review of the implemented prototype. They are not a substitute for empirical evaluation.

## Implemented Mechanism

```text
AI detects where human review is needed
  -> human feedback is captured structurally
  -> feedback becomes reusable Human Judgment Memory
  -> memory is retrieved as advisory evidence
  -> memory-informed comparison is generated in parallel
  -> original VEGO-AI output remains untouched
```

## Evaluation Questions And Measures

| Evaluation Question | What To Measure | Evidence Source |
| --- | --- | --- |
| Where does VEGO-AI need human review? | Number of review items, trigger reasons, review coverage. | M1 review queue outputs, dashboard counts. |
| How much feedback becomes reusable? | Resolved feedback count, `reusable=true` count, rationale completeness. | M2 resolved queue and feedback records. |
| Does memory retrieve relevant judgments? | Top-k relevance, match reasons, conflict status, human relevance rating. | M3 retrieval traces and M4A memory matches. |
| Does M4A advice help? | `advice_strength` distribution, reviewer usefulness rating, conflict warnings. | `memory_advice.json`, expert review notes. |
| Does M4B-1 differ from original? | `memory_informed_differs_from_original`, classification change meaning. | `memory_informed_comparison.json`. |
| Where is human still needed after memory? | `requires_human_review_after_memory`, conflict or moderate disagreement cases. | M4B-1 comparison records. |
| Does memory improve expert alignment? | Original vs memory-informed vs expert labels. | Expert label table and comparison outputs. |
| Does it generalize? | Leave-one-pattern-out, cross-setting, cross-domain, cross-diagram, or expert holdout results. | EXP-001 evaluation protocol and held-out outputs. |

## Initial EXP-001 Run

Command:

```powershell
.\scripts\build-exp001-evaluation.ps1
```

Input run:

- `VEGO-AI/runs/20260614-122150/human/`

Generated local outputs, ignored by Git:

- `reports/generated/exp001/exp001_evaluation_dataset.csv`
- `reports/generated/exp001/exp001_evaluation_table.md`
- `reports/generated/exp001/exp001_summary.json`
- `reports/generated/exp001/exp001_summary.md`

### Available Label Sources

| Source | Availability | Evaluation Role |
| --- | --- | --- |
| Agent D baseline classifications | Available for four settings | Original AI classification baseline, not expert truth. |
| M4B-1 memory-informed comparison | Available for four settings | Parallel comparison output. |
| Human Judgment Memory labels | Available for three `ucd_ch` patterns | Mechanism validation labels only; all are same-pattern. |
| Independent held-out expert labels | Not available yet | Required before accuracy/generalization claims. |

### Dataset Summary

| Measure | Value |
| --- | ---: |
| M4B-1 comparison rows | 27 |
| Settings covered | 4 |
| Expert-labeled rows available from reusable memory | 3 |
| Generalization-safe expert-labeled rows | 0 |
| Memory-informed classifications differing from original | 0 |
| Human-review-after-memory flags | 2 |
| Conflicting memory flags | 0 |

### Distributions

| Distribution | Values |
| --- | --- |
| Settings | `cd_ch=4`, `cd_pw=7`, `ucd_ch=8`, `ucd_pw=8` |
| Advice strength | `none=19`, `weak=4`, `moderate=2`, `strong=2` |
| Leakage status | `none=19`, `cross_setting_memory_used=5`, `same_pattern_memory_used=3` |
| Rules applied | `no_memory_keep_original=19`, `weak_keep_original=4`, `moderate_disagreement_keep_original_require_review=2`, `strong_agreement_keep_original=2` |

### Expert Alignment

| Subset | Expert Labels | Original Matches | Memory-Informed Matches | Original Agreement | Memory-Informed Agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mechanism validation, includes same-pattern memory | 3 | 2 | 2 | 0.6667 | 0.6667 |
| Generalization-safe, excludes same-pattern memory | 0 | 0 | 0 | Not evaluable | Not evaluable |

### Initial Interpretation

This run shows that M4B-1 can aggregate the comparison table, preserve the original AI output, apply deterministic rules, track leakage, and flag cases requiring further human review. It does not show an accuracy improvement.

In this run, M4B-1 clarified review needs rather than changing classifications:

- No memory-informed classification differed from the original Agent 4 classification.
- Two moderate-disagreement cases were flagged for human review after memory.
- The only expert-labeled rows came from same-pattern Human Judgment Memory, so they are mechanism-validation evidence only.

Generalization is not evaluable yet because there are zero held-out or cross-setting expert labels.

## Dashboard Figures To Produce

Use the local results dashboard to prepare thesis tables and figures for:

- review queue counts,
- trigger reason distribution,
- feedback resolution counts,
- reusable feedback counts,
- memory item counts,
- advice strength distribution,
- memory match reasons,
- M4B-1 comparison differences,
- evaluation leakage status,
- human-review-after-memory cases.

Generated dashboard/evaluation files remain ignored under `VEGO-AI/reports/results_dashboard/` and `reports/generated/` until publishability is approved.

## Leakage Policy

Separate mechanism validation from generalization evaluation.

Same-pattern memory may demonstrate that the mechanism works, but it cannot prove generalization. If a memory item derived from the same pattern is used to evaluate that pattern, label the result:

```text
same_pattern_memory_used
```

Use the following for stronger evidence:

- leave-one-pattern-out,
- cross-setting,
- cross-domain,
- cross-diagram,
- expert-only holdout.

## Allowed Claims After Initial EXP-001 Run

The project can claim:

- VEGO-AI now has a staged reusable human-judgment layer.
- Human review can be selectively triggered and persisted.
- Human feedback can be captured structurally.
- Reusable Human Judgment Memory can be stored with provenance.
- Memory can be retrieved as advisory evidence without changing AI output.
- M4B-1 can produce a non-destructive memory-informed comparison artifact.
- M4B-1 can identify memory-related cases that still require human review.
- The current local EXP-001 run supports mechanism/readiness evaluation, not accuracy improvement.

## Claims Not Yet Allowed

Do not claim yet:

- memory improves VEGO-AI accuracy,
- memory-informed classification is better,
- reusable judgment generalizes across domains/settings,
- M4B-1 should replace Agent 4 output.

Those require EXP-001/C4B evidence with leakage status and expert-label comparison.
The first EXP-001 run does not provide that evidence because it has zero generalization-safe expert-labeled rows.

## Evaluation Execution Checklist

1. Select audited inputs and confirm publishability status.
2. Define expert label fields and adjudication process.
3. Generate or collect review queue, feedback, memory, advice, and comparison artifacts.
4. Record exact code tag/commit, settings, commands, and output paths.
5. Label every M4B-1 comparison with `evaluation_leakage_status`.
6. Compare original Agent 4, memory-informed comparison, and expert labels.
7. Produce dashboard tables/figures.
8. Write limitations and validity threats before making claims.

## Current Verdict

Engineering state: strong.

Research prototype: strong.

MSc potential: strong.

Empirical evidence: incomplete.

Best next move: collect or define held-out expert labels, rerun EXP-001 with leakage-aware partitions, and then produce thesis tables/figures.
