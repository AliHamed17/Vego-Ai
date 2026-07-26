# Thesis

Use this folder for thesis planning and chapter drafts.

Recommended flow:

1. Maintain `outline.md`.
2. Link every chapter claim to experiments or literature notes.
3. Keep reviewed thesis figure assets in `figures/evidence-ready/`. Their
   manifest binds exact PNG hashes to the canonical evidence values, and the
   DOCX builder validates the binding without re-rasterizing fonts.
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

- `output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-<package-date>.docx` is the
  combined, evidence-gated review draft.
- `../output/pdf/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-<package-date>.pdf` is the
  rendered review copy (kept local/ignored).
- `../VEGO-AI-Thesis-Baseline-Progress.html` is the self-contained interactive
  B0-B5 progress and experiment explainer.

Build and verify the review package with:

```powershell
$packageDate = "2026-07-25"
python scripts/build_thesis_review_document.py --package-date $packageDate
python scripts/validate_thesis_review_document.py `
  "thesis/output/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-$packageDate.docx" `
  --pdf "output/pdf/VEGO-AI-MSc-Thesis-Evidence-Ready-Draft-$packageDate.pdf"
python scripts/build_thesis_review_manifest.py `
  --package-date $packageDate `
  --check
```

Refresh the reviewed figure assets only when their canonical data or renderer
changes:

```powershell
python scripts/build_thesis_review_document.py --refresh-figures
```

Inspect all four refreshed images before committing them. Normal Windows and
Linux builds consume the reviewed bytes and therefore produce the same DOCX
hash.
