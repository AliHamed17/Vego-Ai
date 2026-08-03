# Medical Derived Artifact Provenance Template

**Template status:** blank control artifact — **not export approval**
**Default classification:** **P3 restricted medical**
**Instruction:** complete one record per artifact without pasting patient rows, notes, identifiers, screenshots, credentials, or row-level examples. Metadata, hashes, aggregate counts, and non-sensitive evidence references only.

An artifact remains P3 and inside the restricted VDI until all six entry gates pass and downstream control D3 approves the exact file, version, claim, destination, and audience.

## 1. Artifact identity

| Field | Required entry |
| --- | --- |
| Artifact ID | `MED-ART-YYYYMMDD-NNN` |
| Artifact title | `[Required]` |
| Version | `[Required]` |
| Created UTC | `YYYY-MM-DDThh:mm:ssZ` |
| Created by | `[Named authorized researcher]` |
| Study/request ID | `[Approved protocol/request ID]` |
| D2 pilot/run ID | `[Required]` |
| Artifact type | `[table/metric/figure/model/report/notebook/other]` |
| Current VDI path/reference | `[Non-secret approved-system reference]` |
| Current classification | `P3 restricted medical` |
| Proposed destination | `[Repository/shared Drive/publication/other/none]` |
| Proposed audience | `[Required]` |
| Status | `DRAFT — NOT APPROVED FOR EXPORT OR CLAIMS` |

## 2. Authorization chain

| Requirement | Evidence record ID | Verified by | Verified date | Expiry | Status |
| --- | --- | --- | --- | --- | --- |
| G1 — use-case | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| G2 — people | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| G3 — authorization | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| G4 — ethics/privacy | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| G5 — environment | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| G6 — protocol | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| D1 — data integrity/provenance | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| D2 — bounded pilot/scientific validation | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| D3 — disclosure/export/claim | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |

All rows must be `Passed` and current before release.

## 3. Source lineage

Do not include source rows or patient identifiers.

| Source/parent ID | Source type and version | Approved-system location/reference | SHA-256 or immutable version | Aggregate row/file count | Purpose in transformation | Authorization record |
| --- | --- | --- | --- | ---: | --- | --- |
| `[Required]` | `[Required]` | `[Required]` | `[Required]` | `[Aggregate only]` | `[Required]` | `[Required]` |

Required declarations:

- Source dataset release/version: `[Required]`
- Acquisition method and date: `[Required]`
- Named licensee/data recipient: `[Required; evidence outside repository]`
- Data-use purpose: `[Required]`
- Cohort specification version: `[Required]`
- Schema/data-dictionary version: `[Required]`
- Source checksum reconciliation: `[Pass/Fail with evidence ID]`
- Parent-artifact provenance verified: `[Yes/No/Not applicable]`
- Any missing or substituted inputs: `[Required; "none" or explanation]`

## 4. Code, environment, and parameters

| Item | Required value |
| --- | --- |
| Code repository and commit/tag | `[Required; code must contain no P3]` |
| Entry point | `[Required]` |
| Environment lock identifier/hash | `[Required]` |
| Operating environment | `[Approved VDI image/version]` |
| Runtime and package versions | `[Evidence file ID]` |
| Random seed(s) | `[Required or not applicable]` |
| Parameter/config file hash | `[Required]` |
| Approved local model identifier/version | `[Required or "no LLM used"]` |
| Model weights hash and source | `[Required if applicable]` |
| External network access during run | `No; attach control evidence` |
| Run log ID and start/end UTC | `[Required]` |
| Hardware relevant to reproducibility | `[Required]` |

List every non-default parameter that materially affects cohorting, transformations, training, evaluation, suppression, or rendering:

| Parameter | Value/reference | Rationale | Approved protocol mapping |
| --- | --- | --- | --- |
| `[Required]` | `[Required]` | `[Required]` | `[Required]` |

## 5. Transformation record

- Plain-language transformation summary: `[Required]`
- Unit of analysis: `[Required]`
- Inclusion/exclusion implementation: `[Required]`
- Time-window and ordering rules: `[Required]`
- Missing/duplicate handling: `[Required]`
- Terminology/code mappings: `[Required]`
- Feature/label definitions: `[Required]`
- Aggregation level: `[Required]`
- Suppression/generalization rules: `[Required]`
- Model/training procedure: `[Required or not applicable]`
- Post-processing: `[Required]`
- Known irreversible information loss: `[Required]`
- Known residual disclosure risk: `[Required]`

For process-mining artifacts:

- case ID concept and hashing/pseudonymization rule: `[Required]`
- activity mapping version: `[Required]`
- timestamp and concurrency rule: `[Required]`
- trace inclusion rule: `[Required]`
- variant/frequency threshold: `[Required]`

## 6. Data-quality and scientific validation

| Check | Method/evidence ID | Result | Reviewer | Status |
| --- | --- | --- | --- | --- |
| Source/schema/checksum reconciliation | `[Required]` | `[Required]` | `[Required]` | Blocked |
| Cohort count reconciliation | `[Required]` | `[Aggregate result]` | `[Required]` | Blocked |
| Missingness and duplicate assessment | `[Required]` | `[Aggregate result]` | `[Required]` | Blocked |
| Temporal and label leakage | `[Required]` | `[Required]` | `[Required]` | Blocked |
| Bias/subgroup assessment | `[Required]` | `[Aggregate result]` | `[Required]` | Blocked |
| Baseline comparison and uncertainty | `[Required]` | `[Aggregate result]` | `[Required]` | Blocked |
| Sensitivity/robustness analysis | `[Required]` | `[Aggregate result]` | `[Required]` | Blocked |
| Reproduction from locked inputs | `[Required]` | `[Required]` | `[Independent reviewer]` | Blocked |
| Clinical interpretation | `[Required]` | `[Required]` | `[Clinical expert]` | Blocked |
| Methods review | `[Required]` | `[Required]` | `[Methods reviewer]` | Blocked |

Record failures and limitations; do not omit a failed check:

- Failed checks: `[Required; "none" only if verified]`
- Deviations from approved protocol: `[Required]`
- Known limitations: `[Required]`
- Conditions under which result must not be used: `[Required]`

## 7. Disclosure-control and export review

| Control | Required evidence |
| --- | --- |
| No patient/encounter/event rows | `[Reviewer confirmation]` |
| No identifiers or quasi-identifying combinations | `[Reviewer confirmation]` |
| No clinical-note or free-text excerpts | `[Reviewer confirmation]` |
| No screenshots/copied cells/rare-case examples | `[Reviewer confirmation]` |
| No reversible encodings, embeddings, or model memorization artifact | `[Assessment ID]` |
| Aggregation threshold | `[Approved rule and result]` |
| Small-cell suppression | `[Approved rule and result]` |
| Outlier/rare-trajectory handling | `[Approved rule and result]` |
| Metadata and labels reviewed | `[Reviewer confirmation]` |
| Output file SHA-256 | `[Required after final rendering]` |
| Exact destination and access group | `[Required]` |
| Retention and disposal date | `[Required]` |

If any control is unknown or failed, export remains prohibited.

## 8. Evidence-claim registration

| Claim ID | Exact proposed wording | Classification | Supporting artifact element | Limitations included | Supervisor decision |
| --- | --- | --- | --- | --- | --- |
| `[Required]` | `[Exact sentence]` | `[verified/preliminary/proposal/open question]` | `[Table/figure/metric ID]` | `[Required]` | `Blocked` |

Do not infer clinical benefit, causal effect, generalizability, or readiness from a technical metric unless the approved protocol and clinical review explicitly support that statement.

## 9. Approval and release

| Decision | Approver | Evidence/signature record | Date | Expiry/conditions | Status |
| --- | --- | --- | --- | --- | --- |
| Clinical interpretation | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| Methods/reproducibility | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| Privacy/disclosure | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| Data-owner/export | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| Supervisor claim approval | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |
| Lead release attestation | `Unknown` | `Unknown` | `Unknown` | `Unknown` | Blocked |

**Final classification:** `P3 restricted medical`
**Export decision:** `NOT APPROVED`
**Approved destination:** `None`
**Approved claims:** `None`

## 10. Change, retention, and revocation history

| Version/date | Change | Reason | Prior hash | New hash | Approval impact |
| --- | --- | --- | --- | --- | --- |
| `0.1 / YYYY-MM-DD` | `Initial record` | `[Required]` | `Not applicable` | `[Required]` | `All approvals blocked` |

Any change to inputs, cohort, code, environment, parameters, aggregation, figure rendering, wording, destination, or audience creates a new artifact version and requires D3 review again; material upstream changes can also reopen G1–G6, D1, or D2.
