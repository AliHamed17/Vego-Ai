# Project Charter

## Working Title

VEGO-AI: Agentic AI for Variability Exploration of Domain Models.

## Research Purpose

Develop, evaluate, and document an agentic AI workflow that supports variability exploration in domain models, with careful attention to reproducibility, validity, expert comparison, and research traceability.

## Primary Outcomes

- A reproducible research pipeline for VEGO-AI experiments.
- A documented evaluation methodology.
- Evidence tables, figures, and analysis artifacts for papers and thesis chapters.
- A maintainable codebase that can evolve from prototype to reusable research software.
- A prompt and decision history that helps Codex and Claude continue work with context.

## Boundaries

In scope:

- Multi-agent pipeline implementation and evaluation.
- Experimental protocols and reproducibility records.
- Research documentation, thesis material, and publication planning.
- Data, model, and output governance.

Out of scope unless explicitly requested:

- Publishing private or sensitive data.
- Hardcoding API keys or credentials.
- Large binary versioning without Git LFS, DVC, or a deliberate storage decision.
- Major code refactors that change scientific behavior without an experiment record.

## Current State

- The original VEGO-AI package is preserved in `VEGO-AI/`.
- Research/project scaffolding is managed at the repository root.
- Agent memory is stored in `docs/agent-memory/`.

## Quality Bar

- Reproducible commands.
- Traceable experiments.
- Explicit assumptions.
- Clear separation between raw inputs, source code, generated outputs, and interpretation.
- No secrets in tracked files.
- Research notes are written so a future examiner, collaborator, or agent can understand why a result exists.

