# VEGO-AI Extension Plan - July 2026 Supervisor Redirect

Last updated: 2026-07-10.

Status: **ACTIVE PROVISIONAL PLAN.** Read this file first for the July 2026 supervisor redirect, then use the July 15 decision register for current approval state. M-02 through M-05 are not recorded; no detailed architecture, dosage, H-Verify, authority, timeout, or live-hook choice is approved.

Sources: `docs/research/meetings/2026-07-01-supervisor-meeting-iris.md` (canonical machine-derived notes awaiting participant confirmation), `docs/video1832857678.transcript.he.md` (machine transcript, primary source).

Scope: documentation, architecture, thesis framing, and research planning only. No VEGO-AI source-code behavior changes.

## 1. Context And Scope

Historical commits/tags contain M1-M4B-1 evaluation infrastructure, but the current `main` worktree is intentionally dirty and must not be described as clean or fully finalized. The binding evaluation constraint remains EXP-005: 0 of 24 generalization-safe expert labels in the latest validated status, so accuracy, generalization, and clinical-performance claims remain blocked.

The machine-derived record of the 2026-07-01 supervisor meeting supports a framework-first redirect pending participant confirmation. It records a proposal for the human-judgment layer to become a first-class listener across both inter-agent communication circles, with early intervention, H-terms, and M4 deferred to a separate parked evaluation track. Continuous observation across all events remains an open design choice, not an approved implementation requirement.

## 2. Transcript-Derived Directives

Each directive traces to the machine ASR (timestamps refer to `docs/video1832857678.transcript.he.txt`). Independent extraction passes improved consistency but did not human-verify the transcript, English paraphrases, or speaker attribution.

| # | Directive | Transcript basis |
| --- | --- | --- |
| D1 | Human layer listens across the artifact circle and the Q&A circle; the extent of continuous observation remains open | 02:38-04:24 (machine-derived paraphrase: the layer is described as sitting on the connections and usually listening quietly) |
| D2 | Intervene early, not only post-Agent-4 | 03:10-03:20 (raised and mutually confirmed) |
| D3 | Rename M1/M2/M3 -> H1/H2/H3; decide agents vs. skills | 13:25-14:08 |
| D4 | Defer M4; framework and evaluation in separate diagrams | 13:03-13:09 (defer M4); 22:36-22:59 (separate diagram, park it) |
| D5 | Human expert is a real person, never simulated | 05:35-08:15 ("do not replace the human expert") |
| D6 | Configurable intervention dosage (every-decision / threshold / first-N-then-auto) | 19:51-20:35 (Arnon); 15:03-15:19 and 16:45-17:13 (Iris's dosage caution) |
| D7 | Bidirectional interfaces; human interface is thesis scope | 15:26-15:59 |
| D8 | Learning beyond save/retrieve, including correcting Agents 1-4 knowledge | 15:59-17:29 |
| D9 | Anti-sycophancy: verify expert input against sources, raise questions | 17:58-19:46 |
| D10 | Convergence: interaction must not become infinite back-and-forth | 18:38-18:57; 05:22-05:34 (no infinite mutual triggering) |
| D11 | July 15 deliverables: skills map + prompt requirements (not prompts) | 21:19-22:21 |
| D12 | Literature survey for Pnina's course; PhD idea log with medical-domain preference | 23:03-27:30 (survey); 33:05-33:57 (idea log, medical domain) |

## 3. Gap Analysis Against Current Repo State

| Area | Current repo | Required by redirect |
| --- | --- | --- |
| Human-layer framing | M1/M2/M3/M4A/M4B-1 memory-and-evaluation chain, triggered by late-stage Agent 3/4 signals | H-layer framework with listener (S1), triage (S2), routing (S3), capture (S4), verifier (S5), integrator (S6), learner (S7); early-stage event coverage; bidirectional interfaces |
| Naming | M-milestones everywhere (docs, code, tags, tracker) | H1/H2/H3 in new research docs and diagrams; code/schemas/tags keep M-names until a dedicated rename PR is approved |
| M4A/M4B-1 | Treated as the top of the framework chain | Repositioned as evaluation instruments in the parked evaluation track; frozen at tags |
| Diagrams | Combined workspace/topology views | Separate `docs/architecture/framework-diagram.md` and `docs/architecture/evaluation-diagram.md` |
| EXP-005 | The blocking next step (0 real labels) | Parked as the future evaluation track's entry gate - NOT deleted, NOT bypassed; label collection remains welcome when supervisor time appears |
| Memory semantics | Save/retrieve with provenance and conflict detection (inert) | Design for reasoning/learning and knowledge correction (S7) - specification now, implementation later and gated |
| Expert model | Correctly real-human in EXP tooling | Preserved; add roles (supervisor/TA/external) and dosage configuration to the framework spec |
| Sycophancy defense | None | S5 H-Verify: source-grounded challenge with bounded convergence |

## 4. Target Architecture

The provisional H-layer design passively observes framework/lifecycle events E1-E14 across Agents 1-4; whether full continuous observation is approved remains an M-03 choice. E15 is evaluation-only and is routed out without framework action. Full event catalog, integration matrix, and interface-direction inventory: `docs/research/h-layer/skills-map.md`. Diagram: `docs/architecture/framework-diagram.md`.

H-layer skills:

| Skill | Function |
| --- | --- |
| S1 Listen | Continuous, quiet observation of artifact and Q&A events across every agent interaction |
| S2 Classify intervention opportunity (triage) | Decide what merits human attention under the configured dosage |
| S3 Route to human | Turn promoted observations into self-contained review items for the real expert |
| S4 Capture structured feedback | Structured decision + rationale + confidence + scope + provenance |
| S5 H-Verify | Anti-sycophancy, source-grounded challenge of expert input BEFORE it is trusted |
| S6 Integrate feedback back to agents/artifacts | Deliver verified judgments as correction proposals / context, approval-gated |
| S7 Percolate / learn / update knowledge | Maintain judgment memory, generalize, correct Agent 1-4 knowledge over time - more than save/retrieve |

H1/H2/H3 mapping (Iris's renaming of the M-milestone intents):

| H | Meaning | Covers skills |
| --- | --- | --- |
| H1 | Human review / intervention detection | S1, S2, S3 |
| H2 | Human feedback interface and capture | S4, S5 |
| H3 | Human-judgment memory / learning / reuse | S6, S7 |

M4 (advisory retrieval and memory-informed comparison) stays evaluation-only, in the parked track (`docs/architecture/evaluation-diagram.md`).

## 5. Phased Plan With Dates

| Phase | Window | Content | Outputs |
| --- | --- | --- | --- |
| P0 Realignment and source capture | 2026-07-03 .. 2026-07-06 | Transcript captured in `docs/`; meeting notes; this plan; diagram split; index/memory updates | Meeting notes, this file, both diagrams, updated indexes and memory |
| P1 July 15 package | 2026-07-04 .. 2026-07-14 | Deliverable A (skills map) and B (prompt requirements) drafted; collect M-01..M-06 outcomes and participant corrections | `docs/research/h-layer/skills-map.md`, `docs/research/h-layer/prompt-requirements.md`, decision register |
| P2 Detail specs and offline harness | 2026-07-10 .. 2026-08-15 | Provisional detail specs exist and are being reconciled against real code symbols; offline contracts/harness may advance, but accepted defaults must trace to M-02..M-05 | `docs/research/h-layer/` specs and offline experiment tooling |
| P3 Literature survey (Pnina's course) | 2026-07-04 .. mid-August presentation; submission end-Sep/Oct | Survey per extended taxonomy; corpus log; gap statement | Course slides + written survey (doubles as thesis Chapter 2 input) |
| P4 Framework + survey paper | 2026-09-01 .. 2026-10-31 | Assemble framework + survey into a paper draft; refresh claim/evidence table with H-layer framing; keep accuracy claims blocked | Paper skeleton + draft |
| P5 Parked evaluation track | On Iris's go-ahead only | Version 0 vs. Version 1 design, criteria, usability questionnaire; EXP-005 real-label gate unchanged as entry; local pilots then Stockholm/Belgium | See `docs/architecture/evaluation-diagram.md` |
| P6 PhD trajectory | Ongoing, low intensity | Idea log upkeep; medical-domain transfer via **MediVARIA** (`docs/research/medivaria/medivaria-study-plan.md`, added 2026-07-04: clinical instantiation of the H-layer, MV-P0..MV-P5 aligned to the IIA TRL 3->5 track); direct-track admin (Sigal) | `docs/research/phd-extension-ideas.md`, `docs/research/medivaria/medivaria-study-plan.md` |

## 6. Governance Reconciliation

Unchanged and still authoritative:

- EXP-005 real-label gate: >=20 generalization-safe labels before any quantitative claim; currently 0; no invented, synthetic, or same-pattern labels count as real evidence.
- No source behavior changes on `main`: no edits under `VEGO-AI/framework/`, `VEGO-AI/schemas/`, `VEGO-AI/tests/`, `VEGO-AI/eval/`, `VEGO-AI/inputs/`; no Agent 4 changes; no M4B-1.1/M4B-2; no LLM/API calls; no embeddings; no baseline or `VEGO-AI/eval_output` overwrites.
- No accuracy-improvement claims; allowed claims remain those in `docs/operations/alignment-control.md`.
- Frozen tags stay frozen.

Changed by this redirect (sequencing only):

- The EXP-005 blocker now gates the PARKED evaluation track, not framework-track documentation/specification work; the `blocked` review verdict should be read as evaluation-track status.
- New H-naming applies to new research docs and diagrams; code, schemas, tags, and history keep M-names until a dedicated, separately-approved rename PR.
- Offline documentation, contracts, scripts, and generated/ignored experiment outputs may advance without changing baseline behavior. Live listener work remains blocked until M-05 and a separate implementation authorization approve `docs/research/h-layer/allowed-touch-proposal.md`.

## 7. Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Human availability bottleneck (Iris's explicit concern) | Configurable dosage (D6); default modes never block pipeline progress on missing expert input |
| Human sycophancy risk - AI swept along by wrong expert input | S5 H-Verify: source-grounded challenge before trust; questions, not compliance |
| Infinite human-AI interaction loops | Convergence policy (D10): bounded question rounds, bounded integration iterations, escalation to adjudication |
| Evaluation done prematurely | Separate, parked evaluation diagram; framework-first sequencing; EXP-005 gate intact |
| Scope creep into source code | Hard documentation-only boundary in this phase; protected paths listed in section 6 |
| Transcript misreading (machine ASR) | Meeting notes remain marked machine-derived; independent extraction is only a consistency check; open questions are scheduled for participant confirmation on 2026-07-15 |
| Naming drift (M vs. H) | H-names in new docs only; single mapping table (section 4); code rename deferred to one reviewed PR |

## 8. Acceptance Checklist

- [x] All 12 machine-derived directives are covered by at least one provisional deliverable (see traceability in `docs/research/h-layer/prompt-requirements.md`); participant confirmation remains pending.
- [x] Protected runtime paths have no tracked diff for this offline reconciliation; the wider worktree is dirty and is not claimed clean.
- [x] Framework and evaluation diagrams are separate files; M4/EXP/usability appear as COMPONENTS only in the evaluation diagram (the framework diagram names them solely in explicit exclusion and governance notes).
- [x] New docs linked from `docs/research/README.md`, `docs/architecture/README.md`, and `docs/architecture/project-map.md`.
- [x] Memory and progress surfaces distinguish nine accepted iterations (iteration 009 metric/contract repair), provisional synthetic prototypes, and pending M-decisions.
- [ ] Re-run current validations only after all offline harness and documentation edits are complete; do not reuse historical PASS labels as current verification.
