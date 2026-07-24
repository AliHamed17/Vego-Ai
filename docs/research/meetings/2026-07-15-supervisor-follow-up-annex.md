# 2026-07-15 Supervisor Follow-up Annex

Status: **Dated provenance annex for supervisor review.** This file distinguishes the July 1 record from work produced on July 4-10 and from decisions requested on July 15.

## 1. Three chronologies

| Chronology | What belongs here | Authority |
| --- | --- | --- |
| 1. July 1 record | Local recording, raw Hebrew ASR, timestamped transcript, D1-D12 paraphrases, and attributed actions | Machine-derived record pending Iris/Arnon confirmation; raw sources remain unchanged and local |
| 2. July 4-10 working layer | Architecture options, S1-S7/E1-E15 formalization, detailed specifications, retired historical prototype scaffold, offline replay results, and MediVARIA planning | Work produced after the meeting; provisional unless explicitly accepted; retired scaffold is not evidence |
| 3. July 15 decisions | M-01 through M-06 outcomes, rationale, approver, owner, and due date | Authoritative only after meeting read-back and explicit confirmation |

The recording and raw ASR must not be rewritten. Any English rendering is a paraphrase unless a human-reviewed quotation is explicitly marked as such.

## 2. July 1 record: corrections carried into this package

| Earlier shorthand or overstatement | Correct treatment in the follow-up package |
| --- | --- |
| “Verified meeting notes” | Canonical **machine-transcript-derived** notes, not yet human-verified. Timestamps support review; they do not turn English paraphrases into quotations. |
| Stockholm and Belgium as secured evaluation resources | Candidate future evaluation sites/contacts discussed in the meeting; no commitment is evidenced in the repository. |
| March 2027 as the thesis deadline | Illustrative fast-path scenario discussed while considering direct-track timing, not an approved deadline. |
| Option B as supervisor-selected architecture | July 4 recommendation for M-02; not a July 1 decision. |
| Four-source H-Verify and a two-round bound as supervisor directives | July 4-10 design proposals for M-04; the July 1 record supports source checking and bounded convergence at the intent level only. |
| MediVARIA as endorsed supervisor scope | July 4 planning draft derived from the medical-domain direction; endorsement, partners, ethics route, and study scope remain open. |

## 3. Work produced after July 1

### July 4: framework and research working drafts

| Artifact group | Contribution | Status and limitation | Decision dependency |
| --- | --- | --- | --- |
| Redirect plan and split architecture diagrams | Translate the transcript-derived redirect into a framework-first sequence; park evaluation separately | Working synthesis. It may not be attributed to supervisors until M-01 confirms the record | M-01, M-02 |
| `h-layer/skills-map.md` | Defines E1-E15, S1-S7, H1/H2/H3 mapping, dosage modes, interfaces, and Options A/B/C | Draft deliverable. Option B is the author recommendation | M-02, M-03, M-05 |
| `h-layer/prompt-requirements.md` | Defines intent, context, inputs, outputs, guardrails, evidence, and convergence requirements; contains no final prompt text | Draft deliverable. It does not authorize prompts, runtime calls, or schema changes | M-02 through M-05 |
| PhD idea log and MediVARIA study plan | Develop the discussed medical-domain direction into possible future studies | Planning drafts only. No clinical data, partner commitment, implementation, ethics approval, or performance evidence | M-06 |

### July 5-10: offline design and mechanism evidence

| Evidence | Bounded result | What it cannot establish | Decision use |
| --- | --- | --- | --- |
| EXP-006 event replay | 481 captured + 20 explicit gaps = 501 ObservationRecords. `11 queue items / 481 heterogeneous reconstructed lifecycle events` is a count ratio only, with no event-level visibility inference or linkage | Does not show complete live coverage, errors, improved results, or hook safety | Supports reconstruction/gap analysis under M-03/M-05 |
| EXP-007 dosage replay | `threshold_sev2`: event load 0.799, transaction load 0.796, weighted coverage 0.981, high-severity coverage 1.0; aggregate coverage/load target remains unmet | Replay-defined mechanism metrics, not expert-validated quality metrics | Supplies a Pareto point under M-03, not a default |
| EXP-008 churn mining | K30/K35 captured 0.75/0.85 of replay-defined candidates | Instability is not evidence that a guideline is wrong; cap/capture target remains a policy choice | Frames the cap trade-off in M-03 |
| Rank-and-cap replay | Uniform K30 and K35 sit on different workload/capture points | Does not prove either cap, an adaptive alternative, or the target is operationally correct | Report Pareto/trade-off only |
| Subject-level bundling | In the cited `cd_ch` setting, absolute items changed 67 to 60 under `every_decision` and 54 to 53 under `threshold_sev2` | Does not support an “up to 45%” workload claim; bundled-load ratios use a changed denominator | Supports only a modest workload-reduction statement under M-03 |
| EXP-009 seeded rule fixtures | Ten `SYNTHETIC_NOT_HUMAN` fixtures contain five expected conflicts and five non-conflicts; the encoded rules produce TP=5, TN=5, FP=0, and FN=0 | Assumption-driven synthetic rule test; no real expert mistakes, behavioral validation, semantic verification, or generalization evidence | Helps inspect the proposed M-04 protocol |
| EXP-010 round-bound sweep | At B=2 the synthetic suite records two resolved, five passed without conflict, two needing adjudication, and one timed out/parked; B=3 and B=4 are unchanged | Escalation is not resolution, and the fixture plateau does not establish the best bound with real experts or real dialogue costs | Helps compare M-04 round-bound options |

All numbers above are historical recorded outputs unless a generation manifest explicitly says they were rerun for this package.

### July 10-11: detailed specifications, generalization engines, and prototype scaffolds

The listener-hook catalog, dosage/triage spec, elicitation interface, H-Verify spec, integration/feedback spec, percolation/generalization spec, and reasoning tables are **provisional drafts**. The new conforming `scripts/feedback_generalizer.py` script is an offline generalization proposal generator enforcing companion manifest checks. The prototype script under `scripts/hlayer_prototype/` is retained only as retired historical scaffolding; current offline evidence comes from EXP-006..018 and the hardened harness; none authorizes runtime changes.

Specific reconciliation required after M-05: the provisional dosage draft contains a timeout option that applies H3 advice automatically. The package recommendation is instead baseline preservation plus parking the item; the draft must be revised if that recommendation is accepted.

## 4. Evidence kept outside the main decision story

- EXP-005 remains the real-label gate for evaluation. Zero supplied real labels means no generalization-safe quantitative evaluation is available. No labels may be invented or auto-filled.
- EXP-012's same-pattern pilot (`N=3`, recorded value `0.6667`) is excluded from the main narrative. It only exercises a computation path and is neither a generalization-safe baseline nor evidence of improvement.
- EXP-001 through EXP-005 and the older evaluation-first diagrams remain in the parked evaluation track. They are not deleted, but they do not determine the framework architecture.
- Historical test counts, if displayed elsewhere, must be labeled historical unless rerun and recorded in the package manifest.

## 5. Decision-to-evidence traceability

| Decision | July 1 intent | Later material used for comparison | Required output |
| --- | --- | --- | --- |
| M-01 | Confirm the record | Enhanced D1-D12 evidence matrix and provenance | Accepted/corrected/qualified rows and actions |
| M-02 | Decide agents versus skills | Options A/B/C and S1-S7/H1-H3 map | Selected decomposition and diagram convention |
| M-03 | Configure observation, routing, and dosage | EXP-006/007/008, bundling, cap replay, provisional S1-S3 specs | Passive scope, active triggers, pilot mode, and cap policy |
| M-04 | Check expert input and converge | Four-source proposal, deterministic/semantic ordering, synthetic EXP-009/010 | Source set, check order, round bound, adjudication path |
| M-05 | Preserve real-human authority and interfaces | Provisional S4/S6/S7 specs and protected-path governance | Approval rule, reviewer roles, timeout rule, allowed-touch process |
| M-06 | Develop survey/PhD direction | Thesis framing drafts, domain-parameterized-spec proposal, MediVARIA plan | RQ timing, education scope, future-work boundary |

## 6. Package boundary

- Runtime APIs remain unchanged.
- This documentation package does not change Agents 1-4, Agent 4 classifications, frozen baselines, schemas, protected framework paths, or EXP-005 labels.
- Detailed specifications and prototype code stay provisional until the corresponding decision is accepted and a separate implementation authorization exists.
- No statement in this annex supports accuracy, generalization, or clinical-performance claims.
- Raw audio and full ASR remain local; tracked/shareable materials contain approved notes, selected reviewed excerpts when available, provenance metadata, and hashes.
