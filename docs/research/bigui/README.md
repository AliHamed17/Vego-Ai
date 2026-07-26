# VEGO-AI BigUI Research Observatory

`VEGO-AI-Research-Hub.html` is the canonical tracked entry point for the
experiment program. It is a self-contained, offline, bilingual view generated
from `ExperimentCatalogSnapshot-v1`; it is not a place to edit research
outcomes.

## What the catalog controls

The catalog covers `EXP-000` through `EXP-040` and binds each experiment to:

- its MSc, PhD, or cross-program space;
- research question, evidence class, status, architecture targets, and gates;
- baseline, comparator, metrics, accepted runs, limitations, and next action;
- source paths and SHA-256 hashes;
- the current label, decision, baseline, and claim boundaries.

Every rendered BigUI number, experiment card, result panel, dependency, and
comparison option is derived from the catalog. Hand-maintained metric constants
are not allowed in the HTML.

## Publication tiers

The tracked catalog and HTML contain sanitized, publishable aggregates only.
Reviewer sheets, raw expert labels, transcripts, private feedback, and detailed
controlled outputs stay ignored and local. The local controlled view is written
only beneath `VEGO-AI/reports/results_dashboard/`.

## Refresh and validation

From the repository root:

```powershell
uv run python scripts/build_bigui_architecture_snapshot.py
uv run python scripts/run_bigui_comparison_experiments.py --refresh
uv run python scripts/build_bigui_run_store.py --refresh
uv run python scripts/build_bigui_catalog.py
uv run python scripts/build_bigui.py
uv run python visualizations-gallery/build_gallery.py
```

Read-only freshness checks:

```powershell
uv run python scripts/build_bigui_architecture_snapshot.py --check
uv run python scripts/run_bigui_comparison_experiments.py --check
uv run python scripts/build_bigui_run_store.py --check
uv run python scripts/build_bigui_catalog.py --check
uv run python scripts/build_bigui.py --check
uv run python scripts/run_bigui_architecture_experiments.py --check
node scripts/tests/bigui_browser_smoke.mjs
```

Controlled local checks:

```powershell
uv run python scripts/run_bigui_architecture_experiments.py --check --controlled
uv run python scripts/build_bigui_catalog.py `
  --controlled-output reports/generated/bigui/experiment-catalog-controlled.json
uv run python scripts/build_bigui.py --controlled `
  --output VEGO-AI/reports/results_dashboard/index.html
```

An accepted run becomes visible by adding a schema-valid accepted manifest to
an approved collector source, then refreshing the catalog and BigUI. Invalid,
stale, private, duplicate, or dangling data aborts the refresh and leaves the
last accepted tracked output unchanged.

## Evidence boundaries

- EXP-005 currently has 24 candidate rows and zero supplied independent safe
  labels.
- Accuracy and macro-F1 therefore remain `null` and appear as not computable.
- M4B-1 currently changes zero of 27 comparison rows.
- Iteration 15 is `NEUTRAL` and reliability-only.
- EXP-033–EXP-035 tracked results are clone-safe offline fixture evidence.
- EXP-036 tracked values are engineering targets, not an accepted performance
  result; machine-specific measurements remain local.
- EXP-037 reconciles the paper draft (178 models, 26 patterns) with the frozen
  repository snapshot (179 models, 27 patterns). The differences are version
  context, not evidence of higher quality.
- EXP-038 demonstrates H-layer capability and reliability dimensions without
  combining them into an arbitrary global score.
- EXP-039 produces metric-specific routing, topology, and runtime deltas only
  for compatible observations and refuses paper-to-current accuracy deltas.
- EXP-040 keeps thesis claims aligned with present evidence: mechanism claims
  are traceable, while empirical hypotheses remain unconfirmed.
- EXP-031 and EXP-032 require consented human studies before any BigUI value
  claim.
- Agent 4, the official baseline, and the GPT-4o default remain frozen.

## Comparison safety

The comparison workbench fails closed. Dataset, partition, baseline, policy,
prompt, model, metric schema, label eligibility, leakage class, and evidence
class must all match. Synthetic and empirical results can never share one
headline series.
