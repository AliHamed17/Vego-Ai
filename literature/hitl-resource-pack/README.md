# HITL Resource Pack

This pack collects Human-in-the-Loop (HITL), Human-AI collaboration, expert-feedback, and data-quality resources that are useful for the VEGO-AI thesis.

## Purpose

VEGO-AI's thesis spine is reusable human judgment in AI-assisted domain model assessment:

```text
selective review -> structured feedback -> reusable memory -> advisory evidence -> controlled comparison
```

The resources here support that spine by giving the project:

- citable sources for Chapter 2 and methodology framing,
- governance references for human oversight and risk control,
- tool references for EXP-005 labeling and future reviewer workflows,
- active-learning and data-quality references for later M4B policy discussions.

## Files

| File | Purpose |
| --- | --- |
| `source-manifest.csv` | Source register with URLs, download status, hashes, publishability, and VEGO relevance. |
| `bibliography.bib` | BibTeX entries for thesis and report writing. |
| `tool-fit-matrix.md` | Practical tool assessment for Label Studio, Argilla, modAL, and cleanlab. |
| `downloads/` | Ignored local copies of open-access PDFs or public documentation snapshots. |

## Boundaries

- Downloaded resources stay local and ignored by Git.
- Tracked files contain citations, summaries, links, and metadata only.
- Paywalled or license-unclear papers are recorded as metadata-only.
- These resources support evidence design and thesis framing; they do not prove VEGO-AI accuracy improvement.
- No annotation platform is installed by this pack.
- No Agent 4, M4B-2, LLM/API, embedding, baseline, or `VEGO-AI/eval_output` behavior is changed.

## Usage

Dry run:

```powershell
.\scripts\download-hitl-resources.ps1 -DryRun
```

Download open resources and update the manifest hashes:

```powershell
.\scripts\download-hitl-resources.ps1
```
