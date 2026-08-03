# Clalit Medical Research Request Template

**Template status:** blank control artifact — **not an approval**
**Default project status until signed:** **BLOCKED**
**Instructions:** complete this document without pasting patient rows, clinical notes, identifiers, screenshots, credentials, or private contact details into the repository. Sensitive contact and authorization evidence must be stored only in the institutionally approved system and referenced here by a non-secret record ID.

Use one request per distinct purpose, cohort, data source, or clinical decision. A materially changed request requires a new version and renewed approval.

## 1. Request control

| Field | Required entry |
| --- | --- |
| Request ID | `CLALIT-REQ-YYYYMMDD-NNN` |
| Version | `0.1-draft` |
| Date created | `YYYY-MM-DD` |
| Requested by | `[Name/role; private contact stored outside repo]` |
| Lead researcher | `[Name/role]` |
| Supervisor/PI | `[Name/role]` |
| Clalit clinical owner | `Unknown` |
| Clalit data owner/steward | `Unknown` |
| Methods reviewer | `Unknown` |
| Ethics/privacy record ID | `Unknown` |
| Current gate | `Gate 1 — use-case — blocked` |
| Target decision date | `Unknown` |
| Expiry/review date | `Unknown` |

## 2. Plain-language request

### Problem and decision

- Clinical/operational problem: `[Required]`
- Decision or workflow this research may inform: `[Required]`
- Intended user(s): `[Required]`
- Current workflow/baseline: `[Required]`
- Why existing evidence or tools are insufficient: `[Required]`
- Explicit non-goals: `[Required]`
- Expected benefit and who benefits: `[Required]`
- Plausible harm or misuse: `[Required]`

### Research question structure

- **Overarching PhD research question:** `[Required]`
- **Subquestion 1:** `[Required]`
  - Method:
  - Evidence/data:
  - Planned artifact:
  - Success/failure criterion:
- **Subquestion 2:** `[Required]`
  - Method:
  - Evidence/data:
  - Planned artifact:
  - Success/failure criterion:
- **Subquestion 3:** `[Required]`
  - Method:
  - Evidence/data:
  - Planned artifact:
  - Success/failure criterion:

### Plan A / Plan B

| Item | Plan A | Plan B |
| --- | --- | --- |
| Scope | `[Required]` | `[Required]` |
| Required medical dependency | `[Required]` | `[Required]` |
| Minimum evidence | `[Required]` | `[Required]` |
| Fallback trigger | `[Required, objective and dated]` | `[Required]` |
| Effect on September proposal | `[Required]` | `[Required]` |

## 3. Clinical protocol

| Element | Required definition |
| --- | --- |
| Population | `[Required]` |
| Unit of analysis | `[Patient/admission/encounter/event/other]` |
| Care setting | `[Required]` |
| Inclusion criteria | `[Required]` |
| Exclusion criteria | `[Required]` |
| Index time/event | `[Required]` |
| Observation window | `[Required]` |
| Prediction/analysis horizon | `[Required or not applicable]` |
| Primary outcome | `[Operational definition and ascertainment]` |
| Secondary outcomes | `[Required or none]` |
| Comparator/baseline | `[Required]` |
| Sample-size rationale | `[Required]` |
| Clinical relevance threshold | `[Required]` |
| Stop criteria | `[Required]` |

For process-mining work, also define:

- case identifier concept: `[Required]`
- activity concept and coding: `[Required]`
- event timestamp(s) and ordering rule: `[Required]`
- start/end events: `[Required]`
- concurrent-event rule: `[Required]`
- missing/duplicate-event rule: `[Required]`
- pathway-variant definition: `[Required]`

## 4. Minimum data request

Do not list real values. Request fields by semantic name and justify each one.

| Source system/table | Field concept | Type/granularity | Purpose | Minimum-necessary justification | Direct/quasi identifier? | Retention | Approved? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `[Required]` | `[Required]` | `[Required]` | `[Required]` | `[Required]` | `[Yes/No/Unknown]` | `[Required]` | `No` |

Additional controls:

- Requested date range: `[Required]`
- Estimated patients/encounters/events: `[Aggregate estimate only]`
- Free-text or notes requested: `[No by default; if yes, separate approval and justification required]`
- Linkage across systems: `[Required or none]`
- External reference data: `[Required or none]`
- Data minimization alternatives considered: `[Required]`
- Synthetic/demo data sufficient for initial development? `[Yes/No with rationale]`
- Fields explicitly excluded: `[Required]`

## 5. Governance and security

| Question | Required answer/evidence reference |
| --- | --- |
| Lawful and institutional research purpose | `[Required]` |
| Data-owner approval record | `Unknown` |
| Ethics/IRB/privacy determination | `Unknown` |
| Consent or waiver basis | `Unknown` |
| Named authorized users | `Unknown` |
| Approved restricted VDI | `Unknown` |
| Storage owner/location | `Unknown` |
| Access start and expiry | `Unknown` |
| Retention and deletion method | `Unknown` |
| Incident contact/process | `Unknown` |
| Export/disclosure reviewer | `Unknown` |
| Publication/reuse constraints | `Unknown` |
| Cross-border or third-party processing | `No by default; otherwise separate written approval` |
| Online LLM/API use | `Prohibited` |
| Local/offline LLM | `Not approved until Gate 5 explicitly approves the environment/toolchain` |

The request must confirm:

- [ ] No patient rows will enter the repository or shared Drive.
- [ ] No medical data will be sent to an online LLM/API or hosted notebook.
- [ ] Each user has individual, purpose-bound access.
- [ ] Raw and intermediate data stay in the approved VDI.
- [ ] Only D3-approved aggregates/synthetic artifacts may leave the VDI after all six entry gates and the required downstream controls pass.
- [ ] A separate provenance record will accompany every proposed export.

## 6. Methods and validation

- Study/design type: `[Required]`
- Data-quality checks: `[Required]`
- Missing-data strategy: `[Required]`
- Temporal leakage controls: `[Required]`
- Label leakage controls: `[Required]`
- Confounding/censoring strategy: `[Required]`
- Subgroup/fairness analysis: `[Required]`
- Baseline(s): `[Required]`
- Primary metric and uncertainty method: `[Required]`
- Secondary metrics: `[Required]`
- Sensitivity/robustness analyses: `[Required]`
- External or temporal validation: `[Required or explicitly unavailable]`
- Clinical review method: `[Required]`
- Reproducibility package: `[Code, environment, parameters, source hashes, run ID]`
- Failure interpretation and stop rule: `[Required]`

## 7. Deliverables and evidence boundary

| Deliverable | Audience/destination | Contains medical data? | Required control | Acceptance criterion | Owner |
| --- | --- | --- | --- | --- | --- |
| Approved protocol | Supervisors/clinical owner | No patient rows | G6 — protocol | Signed and versioned after G1–G5 pass | `[Required]` |
| Metadata/integrity report | Restricted VDI; approved summary only | Metadata | D1 — integrity/provenance | Reconciled manifest/checksums after G1–G6 pass | `[Required]` |
| Bounded pilot | Restricted VDI | Yes, restricted | D2 — pilot/scientific validation | Reproducible and reviewed after D1 passes | `[Required]` |
| Aggregate findings | Explicitly approved destination | Controlled derived | D3 — disclosure/export | Disclosure and claim approval after D2 passes | `[Required]` |

Evidence language must classify each statement as one of:

- verified result;
- preliminary result;
- proposal/hypothesis;
- open question;
- unavailable evidence.

## 8. Dependencies, risks, and open issues

| ID | Dependency/risk/open issue | Impact | Mitigation or fallback | Owner | Due date | Status |
| --- | --- | --- | --- | --- | --- | --- |
| C-01 | `[Required]` | `[Required]` | `[Required]` | `[Required]` | `YYYY-MM-DD` | Open |

At minimum address:

- clinical owner and medical-expert availability;
- data access, field definitions, and extraction lead time;
- ethics/privacy review;
- restricted VDI and tool approval;
- label/outcome reliability;
- cohort size and missingness;
- publication/export constraints;
- September proposal fallback trigger.

## 9. RACI

| Work item | Lead researcher | Supervisor/PI | Clinical owner | Data steward/privacy | IT/security | Methods reviewer |
| --- | --- | --- | --- | --- | --- | --- |
| Purpose and questions | R | A | C | C | I | C |
| Minimum data request | R | A | A/C | C | I | C |
| Access and environment | I | C | C | A | R/A | I |
| Pilot protocol | R | A | A/C | C | I | C |
| Analysis validation | R | A | C | I | I | A/C |
| Export and claims | R | A | C | A | C | C |

`R` = responsible, `A` = accountable, `C` = consulted, `I` = informed. Replace provisional assignments where institutional ownership differs.

## 10. Approval decision

| Gate/decision | Decision (`approve`, `reject`, `revise`) | Approver name/role | Evidence record ID | Date | Conditions/expiry |
| --- | --- | --- | --- | --- | --- |
| G1 — use-case | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| G2 — people | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| G3 — authorization | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| G4 — ethics/privacy | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| G5 — environment | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| G6 — protocol | `Blocked` | `Unknown` | `Unknown` | `Unknown` | `Unknown` |
| D1 — integrity/provenance | `Not authorized` | `Unknown` | `Unknown` | `Unknown` | `Blocked until G1–G6 pass` |
| D2 — bounded pilot | `Not authorized` | `Unknown` | `Unknown` | `Unknown` | `Blocked until D1 passes` |
| D3 — disclosure/export | `Not authorized` | `Unknown` | `Unknown` | `Unknown` | `Blocked until D2 passes` |

**Final request state:** `DRAFT / BLOCKED`
**Next evidence-producing action:** `[Required]`
