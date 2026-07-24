# Thesis Evidence Advancement Package

Status: **Evaluation-ready documentation; human evidence pending.**

This folder is the canonical thesis-facing interface between the accepted VEGO-AI
program state and the next empirical evaluation phase. It adds no labels, changes
no Agent 4 behavior, and authorizes no runtime or policy implementation.

## Canonical files

| File | Role |
| --- | --- |
| `thesis-evidence-snapshot-v1.json` | Machine-readable B0-B5 baseline ladder, evidence counts, label gate, EXP-019-027 roadmap, statistical protocol, claim gates, and chapter traceability. |
| `THESIS_EVIDENCE_BASELINE.md` | Generated human-readable baseline and current stop/go state. |
| `CLAIM_AND_CHAPTER_TRACEABILITY.md` | Generated chapter-to-evidence and claim-boundary register. |
| `THESIS_ACCURACY_EVIDENCE_ADVANCEMENT_PLAN.md` | Full execution plan from calibration to external replication. |
| `PREREGISTRATION_EXP019_027.md` | Frozen questions, partitions, metrics, analysis rules, and stopping rules. |
| `REVIEWER_CALIBRATION_PROTOCOL.md` | Leakage-safe reviewer calibration using the three excluded same-pattern rows. |
| `SUPERVISOR_EVIDENCE_DECISIONS.md` | Exact human decisions required before each gate opens. |
| `RISK_AND_VALIDITY_REGISTER.md` | Evidence, statistical, governance, and execution risks. |
| `THESIS_REVIEW_PACKAGE_MANIFEST.json` | SHA-256 hashes, source state, render QA, primary outputs, and shareable-copy equality for the current DOCX/PDF/HTML package. |

## Document-level interfaces

The package introduces four research-document interfaces under `schemas/`:

- `ThesisEvidenceSnapshot-v1`
- `GoldLabelRecord-v2`
- `PolicyCandidateRecord-v1`
- `EvaluationRunManifest-v2`

They are documentation and evaluation-governance interfaces. They do not change
the VEGO-AI runtime API.

## Build and validate

```powershell
python scripts/build_thesis_evidence_package.py
python scripts/validate_thesis_evidence_package.py
```

`--check` verifies that the generated files are fresh without rewriting them:

```powershell
python scripts/build_thesis_evidence_package.py --check
python scripts/build_thesis_review_manifest.py --check
```

## Current stop state

- Generalization-safe candidates: **24**.
- Supplied real labels: **0**.
- Quantitative MSc minimum: **20**.
- Development/holdout split: **16 / 8**, fixed before policy development.
- External formal-claim minimum/target: **30 / 48**.
- Accuracy, macro-F1, paired net correction, and p-values: **NOT YET COMPUTABLE**.

The next action is human: approve the protocol, complete two independent reviews,
adjudicate disagreements, and freeze the gold-label manifest.
