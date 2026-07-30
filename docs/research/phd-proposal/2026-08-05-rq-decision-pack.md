# Research-Question Decision Pack

Prepared for: Iris Reinhartz-Berger and Arnon Sturm
Provisional checkpoint: 5 August 2026
Prepared by: Ali
Status: **decision request; no option in this file is recorded as supervisor-approved**

## 1. Decision purpose

The 29 July meeting requires one umbrella PhD research question, exactly three subquestions, and a concrete study/method/artifact mapping. It also requires domain-neutral wording, a software engineering/modeling baseline, a conditional medical route, and both Plan A and Plan B.

This pack asks the supervisors to:

1. select or correct the umbrella-question wording;
2. confirm the intent and boundaries of the three subquestions;
3. confirm the three-study mapping;
4. confirm the interpretation of Plan A and Plan B; and
5. identify any terminology that must be changed before the literature review and proposal are expanded.

Requirement sources:

- [`../meetings/2026-07-29-iris-requirements-register.md`](../meetings/2026-07-29-iris-requirements-register.md), especially R-01, R-02, R-07, R-08, R-10, R-11, and R-14
- [`../meetings/2026-07-29-iris-supervisor-action-register.md`](../meetings/2026-07-29-iris-supervisor-action-register.md), especially A-01, A-02, A-08, and A-10

## 2. Recommended canonical wording

### Umbrella research question

**U-RQ:** How can reusable human judgment be captured, governed, and reused in agentic AI assessment of domain-specific artifacts and processes to support auditable, reliable, and transferable human–AI co-reasoning?

### Exactly three subquestions

**SQ1 — Selective intervention:** When and how should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden?

**SQ2 — Governed knowledge reuse:** How should expert judgments be represented, validated, reconciled, and stored so they can be reused transparently without unsafe generalization or loss of human authority?

**SQ3 — Evaluation and transfer:** To what extent does the resulting framework improve assessment quality, consistency, traceability, and expert effort across domains, first in software/modeling and, when governance and access permit, in healthcare?

### Why this set is recommended

| Criterion | Assessment |
| --- | --- |
| One coherent doctorate | The questions follow one lifecycle: decide when to request judgment, govern it as reusable knowledge, then evaluate the resulting framework and its transfer. |
| Exactly three studies | SQ1, SQ2, and SQ3 each map to one primary study while sharing a common artifact and constructs. |
| Domain-resilient | SQ3 requires software/modeling first and makes healthcare conditional on governance and access; Plan B preserves a viable second non-medical transfer setting. |
| Evidence-honest | SQ1 and SQ2 can use current mechanism/specification evidence; SQ3 explicitly carries the missing independent-label gate and treats healthcare as conditional. |
| Doctoral scale | The program combines intervention design, knowledge-lifecycle governance, controlled empirical evaluation, and comparative transfer rather than presenting one implementation as the doctorate. |
| Novelty focus | The novelty candidate is the linked selective-intervention, governed-reuse, and evidence-controlled evaluation lifecycle—not storage, HITL, or medical application alone. |
| Feasibility | Plan B evaluates the complete framework in software/modeling and a second non-medical setting if healthcare access does not permit the conditional extension. |

## 3. Two alternate wording variants

These are alternate phrasings of the same four conceptual slots. They are **not additional research questions**. Whichever wording is selected must remain one umbrella RQ plus the same three SQ roles.

| Slot | Recommended | Variant A — mechanism-centered | Variant B — evidence-centered |
| --- | --- | --- | --- |
| U-RQ | How can reusable human judgment be captured, governed, and reused in agentic AI assessment of domain-specific artifacts and processes to support auditable, reliable, and transferable human–AI co-reasoning? | How should agentic AI assessment systems selectively elicit and safely reuse expert judgment to achieve reliable and transferable human–AI co-reasoning across domain-specific artifacts and processes? | Under what design, governance, and evidence conditions can reusable expert judgment improve agentic assessment across domains? |
| SQ1 | When and how should an agentic assessment system request human judgment so that important uncertainties are addressed without unnecessary expert burden? | Which uncertainty, priority, timing, and dosage mechanisms should trigger expert review while controlling burden? | Under which observable conditions is requesting human judgment more valuable than proceeding without review? |
| SQ2 | How should expert judgments be represented, validated, reconciled, and stored so they can be reused transparently without unsafe generalization or loss of human authority? | What representations and governance controls allow expert judgments to be validated, reconciled, preserved, and reused with provenance and human authority? | Under which validation, reconciliation, scope, and authority rules can prior judgments be reused transparently without unsafe generalization? |
| SQ3 | To what extent does the resulting framework improve assessment quality, consistency, traceability, and expert effort across domains, first in software/modeling and, when governance and access permit, in healthcare? | How does the full framework affect quality, consistency, traceability, and effort in software/modeling, and which effects transfer to an approved healthcare setting? | What empirical gains, costs, and transfer limits are observed in software/modeling and, if access and governance permit, healthcare? |

Recommended editorial choice: use the recommended wording for the August working draft. Variant A is stronger if the doctorate is framed primarily as a design-science architecture contribution. Variant B is stronger if supervisors want the proposal to foreground empirical conditions and evidence.

## 4. Study mapping

| Study | Primary SQ | Research aim | Proposed method | Evidence/data | Expected artifact | Current state |
| --- | --- | --- | --- | --- | --- | --- |
| Study 1 — Intervention architecture | SQ1 | Define when, how, and with what dosage an agentic assessment system requests human judgment | Design science; requirements traceability; controlled event, uncertainty, priority, timing, dosage, routing, escalation, and burden scenarios | Existing VEGO-AI/H-layer event and review-queue artifacts, tests, controlled fixtures, and supervisor decisions | Domain-neutral listener/triage/routing architecture, intervention taxonomy, dosage/escalation policy, burden model, traceability package | Intervention mechanisms/specifications exist; full Study 1 validation is incomplete and no workload benefit is established |
| Study 2 — Judgment lifecycle | SQ2 | Define how expert judgments are represented, source-validated, reconciled, governed, stored, retrieved, and safely reused | Design science; schema/contract validation; controlled provenance, conflict, adjudication, authority, scope, retrieval, and unsafe-reuse scenarios | Existing feedback/memory specifications, schemas, tests, controlled fixtures, and supervisor decisions | Judgment schema, validation/reconciliation protocol, provenance/authority model, bounded verification, safe storage/retrieval/reuse policy | Mechanism/specification evidence exists; transparent or safe reuse has not been empirically shown to improve assessment |
| Study 3 — Evaluation and transfer | SQ3 | Estimate the complete framework’s effects and transfer limits first in software/modeling, then under Plan A or Plan B | Blinded two-reviewer labeling, human adjudication, paired comparison, workload/usability study, error/validity analysis, and comparative second-setting study | Frozen software/modeling baseline; 24 candidate rows; later reviewer/adjudicator returns; Plan A approved healthcare material or Plan B second software/modeling setting | Preregistered protocol, gold set, empirical results, transfer taxonomy, adaptation/governance profile, validity and stopping analysis | Evaluation infrastructure is ready; 0/2 reviewer returns and 0/24 adjudicated safe labels; healthcare setting remains unresolved |

### Study integrity checks

- Study 1 cannot claim reduced expert burden from intervention-architecture readiness.
- Study 2 cannot claim beneficial reuse from judgment-lifecycle readiness.
- Study 3 cannot report quantitative performance until the existing independent-evidence gates are satisfied or claim healthcare feasibility/performance from MIMIC familiarization, MediVARIA planning, or education-domain results.
- A negative or null Study 3 result remains a valid doctoral result if the method is sound.
- Study 3 under Plan B must test genuine transfer across a second setting rather than merely rename the original setting.

## 5. Plan A and Plan B for confirmation

### Proposed Plan A

Construct Studies 1 and 2, evaluate the complete framework first in software/modeling, and extend Study 3 into healthcare only after all six entry gates pass:

1. **Use-case:** precise workflow, problem owner, unit, intended input/output, baseline, non-goals, and success/failure criteria.
2. **People:** named clinician/domain expert, data custodian, privacy/ethics owner, VDI administrator, supervisor, and methods reviewer.
3. **Authorization:** individual project-specific data permission, purpose, training/DUA or partner authority, least privilege, and expiry.
4. **Ethics/privacy:** written determination covering data use, derivatives, retention, publication, disclosure, and incidents.
5. **Environment:** approved VDI, storage, compute, logging, egress controls, and offline/no-telemetry tools or explicit no-LLM decision.
6. **Protocol:** approved cohort, outcomes, process mapping, missingness, leakage controls, statistics, stop rules, and reviewers.

### Proposed Plan B

Complete the identical U-RQ and SQ1–SQ3 program through:

- Study 1 intervention architecture in the current software/modeling setting;
- Study 2 governed judgment lifecycle in the current software/modeling setting; and
- Study 3 evaluation in the current setting plus a second software/modeling dataset, diagram family, task, institution, reviewer panel, or longitudinal setting.

### Proposed fallback rule

If any G1–G6 gate lacks a documented owner, evidence path, or feasible completion date by 26 August 2026, write the September proposal with Plan B as the committed path and Plan A as a contingent extension.

This date and rule are proposed controls; they were not approved in the July 29 call.

## 6. Evidence boundary to approve as proposal language

The working proposal will state:

- Existing work supports architecture, provenance, controlled comparison, and evaluation-readiness claims in software engineering/modeling.
- The independent-evidence program currently has 0 of 2 reviewer returns and 0 of 24 adjudicated generalization-safe labels.
- Accuracy, macro-F1, effort reduction, generalization, and superiority are not yet computable.
- There are no clinical results.
- The documented MIMIC work is a bounded metadata/schema audit only; it inspected no patient rows and does not select or validate a study dataset. Four elapsed hours are not claimed because no start/end record exists.
- MediVARIA is a candidate medical transfer vehicle, not an approved or completed PhD study.

Related evidence:

- [`../independent-evidence/README.md`](../independent-evidence/README.md)
- [`../phd-thesis-optimization-plan.md`](../phd-thesis-optimization-plan.md)
- [`../medivaria/medivaria-study-plan.md`](../medivaria/medivaria-study-plan.md)

## 7. Decisions requested

Please record one outcome per row: **Approve**, **Approve with correction**, **Defer**, or **Reject**.

| ID | Decision | Recommended outcome | Supervisor outcome/correction |
| --- | --- | --- | --- |
| D-RQ-01 | Use the recommended U-RQ wording as the next working baseline | Approve with wording refinement allowed | Pending |
| D-RQ-02 | Use SQ1 selective intervention, SQ2 governed knowledge reuse, and SQ3 evaluation/transfer as the exactly-three structure | Approve | Pending |
| D-RQ-03 | Use the three-study mapping in section 4 | Approve with method refinement later | Pending |
| D-RQ-04 | Define Plan A as conditional medical transfer and Plan B as non-medical transfer | Approve | Pending |
| D-RQ-05 | Keep all questions answerable under Plan B | Approve | Pending |
| D-RQ-06 | Use 26 August as the proposed medical-route decision gate | Approve or replace with a date | Pending |
| D-RQ-07 | Accept the evidence-boundary wording in section 6 | Approve | Pending |
| D-RQ-08 | Treat the existing literature taxonomy as the seed scope and refine its exact review method next | Approve with correction | Pending |
| D-RQ-09 | Confirm the bounded metadata/schema-only MIMIC boundary and continued prohibition on patient-row inspection; require timing evidence for future time-box claims | Approve, narrow, or defer | Pending |
| D-RQ-10 | Assign an owner to verify university candidacy rules and dates | Name owner and source | Pending |

## 8. Read-back checklist

The decision is usable only when the meeting record confirms:

- [ ] one U-RQ wording;
- [ ] exactly three SQs;
- [ ] one primary study per SQ;
- [ ] Plan A and Plan B definitions;
- [ ] fallback trigger or replacement;
- [ ] immediate literature scope;
- [ ] medical-familiarization limit;
- [ ] owner for partner/data/expert feasibility;
- [ ] owner for university-process verification; and
- [ ] next confirmed checkpoint.

## 9. Record-quality caveat

The July 29 bilingual transcript is a complete machine-derived working record, but human bilingual review and full speaker diarization remain pending. This pack relies on the evidence-linked requirements and action registers and uses no direct quotation from the transcript. Any disputed requirement should be corrected through supervisor read-back rather than by silently rewriting the source record.
