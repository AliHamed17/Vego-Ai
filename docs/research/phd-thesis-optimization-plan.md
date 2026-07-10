# PhD Thesis Optimization Plan

Last updated: 2026-07-04 by Fable (Claude) - MediVARIA domain-transfer note after the roadmap; content otherwise 2026-06-29 by Codex.

Purpose: align Claude, Codex, and the local VEGO-AI workspace around a stronger PhD thesis trajectory while
preserving the current MSc thesis evidence boundary. This plan enhances the research structure and baseline
framing; it does not authorize Agent 4 changes, M4B-2, LLM/API calls, embeddings, baseline overwrites, or
accuracy claims.

## 1. Thesis Direction

Working PhD-level thesis:

> Reusable human judgment for governed human-AI co-reasoning in AI-assisted domain model assessment.

The MSc thesis is the first evidence-bearing stage: it proves the architecture, traceability, governance,
and evaluation-readiness of reusable human judgment in VEGO-AI. The PhD continuation should broaden this
into a general, evaluated framework for deciding when human judgments can be reused, when they should only
advise, and when they must trigger further expert review.

## 2. Current Baseline And Evidence Boundary

| Layer | Current state | PhD role |
| --- | --- | --- |
| Original VEGO-AI baseline | Frozen and preserved | Reference system for all comparisons. |
| M1-M4A | Implemented | Shows selective review, structured feedback, memory, and advisory retrieval. |
| M4B-1 | Implemented as non-destructive deterministic comparison | Establishes a safe experimental bridge from advice to evaluation. |
| EXP-001-EXP-005 | Tooling complete | Defines label collection, leakage control, policy screening, and claim gates. |
| EXP-005 labels | 0 real supplied labels | Binding blocker before accuracy/generalization claims. |

Allowed current claims:

- reusable human judgment can be captured, stored, retrieved, and inspected;
- memory-informed comparison can be produced without changing the baseline;
- the system is ready for supervisor-approved expert-label evaluation.

Blocked current claims:

- classification accuracy improved;
- human judgment memory generalizes across held-out settings;
- Agent 4 behavior should change;
- synthetic trials prove real improvement.

## 3. PhD Research Questions

| ID | PhD question | Evidence path |
| --- | --- | --- |
| P-RQ1 | When should AI-assisted domain-model assessment ask for human judgment? | Review queue triggers, expert disagreement, uncertainty, guideline-sensitive cases. |
| P-RQ2 | How can human modeling judgments be represented so they remain reusable, auditable, and conflict-aware? | M2/M3 schemas, provenance, conflict handling, adjudication records. |
| P-RQ3 | When does reusable human judgment improve, clarify, or safely escalate AI variability decisions? | EXP-005 labels, paired comparison, escalation precision/recall, error analysis. |
| P-RQ4 | How should a governed system decide between advisory evidence, deterministic policy refinement, and blocked automation? | M4A/M4B-1/M4B-1.1 gates, sealed holdout, reviewer approval. |
| P-RQ5 | How well does the approach transfer across domains, diagram types, reviewer panels, and future datasets? | Additional annotated runs, cross-domain/diagram validation, reliability analysis. |

## 4. Research Program Roadmap

| Phase | Name | Goal | Gate |
| --- | --- | --- | --- |
| P0 | MSc evidence gate | Complete supervisor-approved EXP-005 labels and Chapter 7 quantitative sections. | At least 20 safe labels, preferably reviewer-2/adjudication. |
| P1 | Baseline characterization | Build a stronger empirical profile of original VEGO-AI errors and review needs. | Real labels plus error taxonomy. |
| P2 | Reuse validity | Test where Human Judgment Memory helps, conflicts, or only escalates. | Leakage-aware comparison across safe rows. |
| P3 | Policy refinement | Design M4B-1.1 only if real labels show safe opportunities. | 16 dev / 8 sealed holdout, explicit supervisor approval. |
| P4 | Broader validation | Add more runs, domains, diagrams, and reviewers. | Publishability and IRB clearance. |
| P5 | General framework | Extract reusable design principles and tooling patterns beyond VEGO-AI. | Cross-case evidence and thesis synthesis. |

Domain-transfer note (2026-07-04): P4/P5 now have a concrete vehicle - **MediVARIA**, the medical-domain
transfer of VEGO-AI + H-layer to clinical guideline adherence (IIA Applied Research proposal, TRL 3 -> 5,
3 years, partner TBD). Study plan, research questions MV-RQ1-6, phase alignment with this roadmap, and the
clinical claim boundaries live in `docs/research/medivaria/medivaria-study-plan.md`. P-RQ5 (transfer) is
its governing PhD question.

## 5. Doctoral Capability Stack

The project should grow through explicit capabilities, not ad hoc feature expansion.

| Capability | Current strength | PhD extension |
| --- | --- | --- |
| Baseline preservation | Frozen Agent 4 baseline, tags, generated-output discipline | Multi-baseline comparison across future model/prompt versions without overwriting historical outputs. |
| Human judgment capture | Review queue, feedback manager, reusable memory | Richer expert decision records, disagreement analysis, adjudication history, and reviewer reliability. |
| Governed reuse | M4A advisory and M4B-1 non-destructive comparison | Evidence-based transition rules from advice to deterministic proposals, using sealed holdout validation. |
| Evaluation gates | EXP-001..EXP-005, evidence-consistency guard, dashboard health | Larger label studies, cross-domain validation, and formal stopping rules for unsupported claims. |
| Thesis/research operations | Memory, progress tracker, dashboards, Confluence outbox, Claude/Codex prompts | Repeatable doctoral research operating system: every claim maps to data, code, labels, limitations, and provenance. |
| Literature and framing | HITL resource pack and verified thesis references | Broader theory-building around human-AI co-reasoning, expert knowledge reuse, XAI, and governance. |

Capability maturity target:

| Level | Meaning | Current status |
| --- | --- | --- |
| L1 Prototype | Mechanism exists and is inspectable. | Achieved through M1-M4B-1. |
| L2 Evidence-ready | Label protocol, dashboards, and guards exist. | Achieved, but human labels pending. |
| L3 Empirically evaluated | Real labels support quantitative reporting. | Blocked on EXP-005. |
| L4 Generalized | Evidence spans additional settings, reviewers, and runs. | PhD extension. |
| L5 Framework contribution | Principles transfer beyond this VEGO-AI instance. | PhD target. |

## 6. Baseline Enhancement Strategy

Enhancing the baseline means improving the research framing and evidence around the frozen baseline, not
rewriting it. The baseline should be strengthened through:

- a clearer baseline characterization chapter/table: original Agent 4 outputs, 179 cases, 27 patterns, four settings;
- an explicit "not ground truth" warning for copied analysis files;
- a repeatable label-driven error taxonomy after EXP-005;
- dashboard figures that separate mechanism metrics from accuracy metrics;
- a frozen-tag and generated-output provenance table for every reported result.

No baseline output should be overwritten. Any future policy variant must write separate comparison artifacts.

## 7. Claude And Codex Collaboration Model

Use Claude and Codex as complementary agents:

| Agent | Primary role | Must not do |
| --- | --- | --- |
| Claude | Thesis prose, literature synthesis, argument structure, supervisor-facing explanation, chapter polish. | Invent citations, claim accuracy, ignore evidence gates. |
| Codex | Repo edits, scripts, dashboards, guards, generated reports, reproducibility checks, implementation safety. | Mutate baseline behavior without approval, skip tests/guards. |

Shared operating rules:

1. Start from `docs/agent-memory/compiled-memory.md` and `docs/PROGRESS_TRACKER.md`.
2. Use `docs/research/phd-thesis-optimization-plan.md` as the PhD direction control page.
3. Use `docs/operations/alignment-control.md` before changing claims or structure.
4. Use `docs/research/supervisor-label-approval-pack.md` as the next human-facing gate.
5. Run `python scripts\check_evidence_consistency.py` before any evidence or claim update.
6. Keep generated CSV contents out of tracked docs; reference generated files instead.
7. When planning PhD extension work, classify it against the capability stack above before proposing files or code.

## 8. Immediate Next Work

The next useful work is not more feature building. It is:

1. Supervisor review of `docs/research/supervisor-label-approval-pack.md`.
2. Approval of reviewer plan, consent/anonymity handling, and claim boundary.
3. Expert labeling of the 24 generalization-safe rows.
4. EXP-005 downstream rerun.
5. Chapter 7 quantitative completion.
6. PhD expansion plan based on real errors and adjudicated labels.

## 9. Success Criteria

The research structure is PhD-ready when:

- the MSc thesis is complete without unsupported claims;
- the frozen VEGO-AI baseline and M4B-1 comparison are reproducible;
- EXP-005 contains real, leakage-safe labels;
- error analysis identifies which future policy/refinement questions are justified;
- every future automation step is gated by supervisor approval, holdout discipline, and evidence consistency.
