# Thesis

Use this folder for thesis planning and chapter drafts.

Recommended flow:

1. Maintain `outline.md`.
2. Link every chapter claim to experiments or literature notes.
3. Keep generated figures in `outputs/` or `reports/`, then reference them here.
4. Record supervisor feedback in meeting notes.

## Evidence package

The canonical thesis evidence state is:

`docs/research/thesis-evidence/thesis-evidence-snapshot-v1.json`

Build and validate it before generating review documents:

```powershell
python scripts/build_thesis_evidence_package.py
python scripts/validate_thesis_evidence_package.py
```

At the current gate, every accuracy, macro-F1, net-correction, and p-value field
must remain null / `NOT YET COMPUTABLE` because no generalization-safe expert
labels have been supplied.

## Supervisor-review outputs

- `output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-24.docx` is the
  combined, evidence-gated review draft.
- `../output/pdf/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-24.pdf` is the
  rendered review copy (kept local/ignored).
- `../VEGO-AI-Thesis-Baseline-Progress.html` is the self-contained interactive
  B0-B5 progress and experiment explainer.

Build and verify the review package with:

```powershell
python scripts/build_thesis_review_document.py
python scripts/validate_thesis_review_document.py `
  thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-24.docx `
  --pdf output/pdf/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-2026-07-24.pdf
python scripts/build_thesis_review_manifest.py --check
```
