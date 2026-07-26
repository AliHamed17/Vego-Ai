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
- the seven-dimension experiment evaluation record and B0–B5 benchmark stage.
- the non-null measurement state, progress assessment, visualization
  specification, paper mapping, and deployable API projection.

Every rendered BigUI number, experiment card, result panel, dependency, and
comparison option is derived from the catalog. Hand-maintained metric constants
are not allowed in the HTML.

`ExperimentResultView-v1` is the presentation contract for each experiment.
It keeps declared metrics, null observations, non-null measurements,
comparison eligibility, and claim eligibility separate. A null placeholder is
therefore never presented as a measured result. `ProgressAssessment-v1` permits
a delta only after all cohort, baseline, policy, prompt, model, metric, evidence,
label, and leakage invariants match.

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
uv run python scripts/build_experiment_benchmark.py --refresh
uv run python scripts/build_bigui_catalog.py
uv run python scripts/build_bigui_result_views.py --refresh
uv run python scripts/build_bigui_deployment_snapshot.py --refresh
uv run python scripts/build_bigui.py
uv run python scripts/build_ai_studio_package.py --refresh
uv run python visualizations-gallery/build_gallery.py
```

Read-only freshness checks:

```powershell
uv run python scripts/build_bigui_architecture_snapshot.py --check
uv run python scripts/run_bigui_comparison_experiments.py --check
uv run python scripts/build_bigui_run_store.py --check
uv run python scripts/build_experiment_benchmark.py --check
uv run python scripts/build_bigui_catalog.py --check
uv run python scripts/build_bigui_result_views.py --check
uv run python scripts/build_bigui_deployment_snapshot.py --check
uv run python scripts/build_bigui.py --check
uv run python scripts/build_ai_studio_package.py --check
uv run python scripts/run_bigui_architecture_experiments.py --check
node scripts/tests/bigui_browser_smoke.mjs
node scripts/tests/ai_studio_api_smoke.mjs
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

## Read-only deployment adapter

`deploy/ai-studio/` packages the same HTML, catalog, result views, paper
snapshot, and deployment snapshot served by the repository. The adapter adds
only read-only endpoints:

- `/api/health`
- `/api/v1/program`
- `/api/v1/experiments`
- `/api/v1/experiments/:id`
- `/api/v1/experiments/:id/runs`
- `/api/v1/paper-baseline`
- `/api/v1/comparisons/eligibility`
- `/api/v1/deployment`

The immutable JSON package remains authoritative. The API refuses a comparison
when any required invariant differs, returns no delta for the rejected pair,
and exposes the mismatch reasons. The tracked deployment snapshot describes a
candidate until the merged-main package is actually deployed and its live hash
is verified.

## Evidence boundaries

- EXP-005 currently has 24 candidate rows and zero supplied independent safe
  labels.
- Accuracy and macro-F1 therefore remain `null` and appear as not computable.
- M4B-1 currently changes zero of 27 comparison rows.
- Iteration 15 is `NEUTRAL` and reliability-only.
- EXP-033–EXP-035 have accepted clone-safe offline parity, topology, and fault
  evidence. Their finite fixtures do not establish classification validity.
- EXP-036 has accepted deterministic operational measurements, but at least
  one older accepted run missed the unified p95 limit. The latest accepted run
  meets the declared ratio limits; machine-specific variability remains
  visible and requires replication.
- EXP-037 reconciles the paper draft (178 models, 26 patterns) with the frozen
  repository snapshot (179 models, 27 patterns). The differences are version
  context, not evidence of higher quality.
- EXP-038 demonstrates H-layer capability and reliability dimensions without
  combining them into an arbitrary global score.
- EXP-039 produces metric-specific routing, topology, and runtime deltas only
  for compatible observations and refuses paper-to-current accuracy deltas.
- EXP-040 keeps thesis claims aligned with present evidence: mechanism claims
  are traceable, while empirical hypotheses remain unconfirmed.
- `ExperimentEvaluationStandard-v1` defines protocol, data, execution,
  reproducibility, safety, comparability, and empirical-validity criteria.
- `ExperimentBenchmarkSnapshot-v1` evaluates all 41 experiments: 26 executed,
  15 protocol/gated/parked, 22 measured passes, four measured partials,
  13 gated non-runs, and two parked records.
- `CurrentRunIndex-v1` selects one deterministic current projection for each
  of the 26 executed experiments while preserving every accepted bundle and
  source-linked metric observation as immutable history. The generated catalog
  and deployment API report the current counts; this durable instruction does
  not duplicate those changing values.
- The 41 result views currently expose 97 distinct non-null metric families.
  EXP-003 remains `observed_null`; EXP-012 remains partially measured because
  its engineering gate fields are non-null while its classification metrics
  remain null.
- The latest-run guardrail view assesses 62 target-bearing or required-null
  observations: 41 met, 11 routing targets missed, and 10 empirical fields
  remained intentionally not computable. Historical misses remain visible
  separately and are never mixed into the current verdict.
- `VEGO-AI-Experiment-Benchmark-Report.html` is the offline technical analytics
  report generated from that benchmark snapshot.
- EXP-031 and EXP-032 require consented human studies before any BigUI value
  claim.
- Agent 4, the official baseline, and the GPT-4o default remain frozen.

## Comparison safety

The comparison workbench fails closed. Dataset, partition, baseline, policy,
prompt, model, metric schema, label eligibility, leakage class, and evidence
class must all match. Synthetic and empirical results can never share one
headline series.
