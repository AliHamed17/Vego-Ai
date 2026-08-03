# MIMIC Resource Metadata Audit — 2026-07-30

**Audit type:** read-only Google Drive metadata inspection
**Patient-row access:** **none**
**Dataset readiness:** **BLOCKED — inventory is incomplete and authority/integrity are unverified**
**Gate impact:** identifies gaps relevant to G3 authorization and downstream D1 integrity; it passes none of G1–G6.

## 1. Scope and evidence boundary

The audit inspected Drive folder listings and file metadata only: file names, MIME types, sizes, timestamps, and sharing/download metadata. It did not open, sample, query, copy, download, move, or delete a raw medical CSV. No patient row or clinical value was observed or recorded.

Small analysis-file metadata and a bounded notebook/workbook feasibility check were used to identify reproducibility gaps. Workbook results were not accepted as scientific evidence.

The audited Drive root contained:

- `dataset/`
- `analysis/`
- `index.xlsx` — 11,741 bytes

Drive reported the files as shared and downloadable, while `source_visibility_status` was `access_not_verified`. Those properties do not prove that the current user is the named licensee, that the files were acquired lawfully, or that the shared-Drive location is permitted.

## 2. Dataset inventory

The `dataset/` folder contained **25 visible CSV files** totaling exactly **42,569,399,885 bytes (39.65 GiB)**.

| File | Bytes |
| --- | ---: |
| `ADMISSIONS.csv` | 12,548,562 |
| `CALLOUT.csv` | 6,339,185 |
| `CAREGIVERS.csv` | 203,492 |
| `CHARTEVENTS.csv` | 35,307,895,134 |
| `CPTEVENTS.csv` | 58,150,883 |
| `DATETIMEEVENTS.csv` | 525,785,298 |
| `DIAGNOSES_ICD.csv` | 19,137,527 |
| `DRGCODES.csv` | 10,487,132 |
| `D_CPT.csv` | 13,807 |
| `D_ICD_DIAGNOSES.csv` | 1,387,562 |
| `D_ICD_PROCEDURES.csv` | 311,466 |
| `D_ITEMS.csv` | 954,420 |
| `D_LABITEMS.csv` | 43,118 |
| `ICUSTAYS.csv` | 6,357,077 |
| `INPUTEVENTS_CV.csv` | 2,464,296,511 |
| `INPUTEVENTS_MV.csv` | 975,255,812 |
| `LABEVENTS.csv` | 1,854,245,647 |
| `MICROBIOLOGYEVENTS.csv` | 72,507,810 |
| `OUTPUTEVENTS.csv` | 396,406,750 |
| `PATIENTS.csv` | 2,628,900 |
| `PRESCRIPTIONS.csv` | 770,336,136 |
| `PROCEDUREEVENTS_MV.csv` | 48,770,424 |
| `PROCEDURES_ICD.csv` | 6,798,492 |
| `SERVICES.csv` | 3,481,645 |
| `TRANSFERS.csv` | 25,057,095 |
| **Total** | **42,569,399,885** |

The official MIMIC-III v1.4 description states that the relational database consists of **26 tables**. The observed folder has 25 CSVs; **`NOTEEVENTS.csv` is missing**.

This is an unresolved discrepancy, not an instruction to download the missing table. Possible intentional exclusion, license scope, sensitivity, an incomplete copy, and version mismatch remain `Unknown` until the data steward verifies the acquisition and purpose.

## 3. Analysis-folder inventory

The `analysis/` folder contained 12 items totaling 119,018,883 bytes:

| File | Type | Bytes | Audit observation |
| --- | --- | ---: | --- |
| `results.xlsx` | Office workbook | 10,933 | Modified 2026-03-22; result definitions and provenance unverified |
| `PROCEDUREEVENTS_MV.xes` | XML/XES | 62,023,597 | Derived process-mining artifact; source mapping and generation parameters missing |
| `PROCEDUREEVENTS_MV_IRB.xlsx` | Office workbook | 56,465,735 | Large derived workbook; authority and relationship to the XES file unverified |
| `PROCEDUREEVENTS_MV_caseCover.png` | Image | 166,212 | Derived figure; parent run and parameters missing |
| `PROCEDUREEVENTS_MV_absFreq.png` | Image | 162,610 | Derived figure; parent run and parameters missing |
| `csv_fields_summary_IRB.xlsx` | Office workbook | 18,764 | Relationship to the non-IRB summary is undocumented |
| `class.txt` | Text | 0 | Empty; editable/source class definition is absent |
| `class.png` | Image | 143,867 | Diagram image exists without a usable textual/source representation |
| `Variability2.0.ipynb` | Notebook | 5,609 | Contains hard-coded `/content/drive/...`-style Colab paths; environment-coupled |
| `csv_fields_summary.xlsx` | Office workbook | 6,855 | Authority relative to `_IRB` variant is undocumented |
| `schema_description.xlsx` | Office workbook | 14,568 | Schema source/version and reconciliation status unverified |
| `MIMIC-III Clinical Database.url` | Windows shortcut | 133 | A link is not evidence of credentialing, acquisition, checksum, or permitted use |

Most analysis artifacts date from December 2025; `results.xlsx` dates from March 2026. Their current relevance to the July 2026 research direction is unverified. They are therefore classified as **historical/unverified**, not as validated preliminary results.

## 4. Technical and reproducibility inconsistencies

1. **Office files are not native Google Sheets.** The Drive URLs resemble Sheets URLs, but the files have `.xlsx` MIME type. A bounded Sheets API metadata attempt returned a precondition error stating that Office files are unsupported. Live range inspection must not be assumed.
2. **No release integrity evidence.** No official checksum manifest, local SHA-256 manifest, or exact release/acquisition record was visible. PhysioNet specifically instructs users to validate checksums.
3. **No row-count reconciliation.** Row counts were not computed because patient files were not opened and no approved VDI was evidenced.
4. **Missing table.** `NOTEEVENTS.csv` is absent relative to the official 26-table description.
5. **Environment coupling.** `Variability2.0.ipynb` contains hard-coded Colab/Drive paths and no locked local environment.
6. **Timestamp inconsistency.** The notebook's Drive metadata shows a created timestamp later than its modified timestamp, consistent with a copied/uploaded artifact whose source history is not established.
7. **Ambiguous variants.** `_IRB` and non-`_IRB` workbook variants lack a documented authority, transformation, version, or supersession decision.
8. **Missing model source.** `class.txt` is empty while `class.png` exists.
9. **Missing project controls.** No analysis README, parameter file, environment lock, run identifier, input hashes, code version, parent-artifact chain, reviewer record, or export approval was visible.
10. **Stale evidence risk.** Existing figures/results predate the current supervisor direction and have not been rerun or reviewed under the current questions.
11. **Location nonconformance.** Apparent patient-level MIMIC CSVs are in the shared-Drive zone, which this governance baseline prohibits.

## 5. Required remediation register

No remediation below authorizes row-level access. All six entry gates G1–G6 must pass before an authorized person performs dataset checks inside the VDI.

| ID | Gap | Required evidence-producing action | Owner/approver | Status |
| --- | --- | --- | --- | --- |
| MA-01 | Source authority unknown | Record named licensee, individual access, training/DUA, acquisition mechanism, purpose, and expiry without storing credentials | Data steward + lead researcher | Blocked/open |
| MA-02 | Shared-Drive location | Obtain written disposition; data steward performs any approved quarantine, relocation, retention, or deletion | Data owner + data steward + security | Blocked/open |
| MA-03 | 25 vs official 26 tables | Reconcile expected manifest and document the `NOTEEVENTS` decision; do not silently reacquire it | Data steward + supervisor/PI | Blocked/open |
| MA-04 | Integrity unverified | Inside the approved VDI, compare exact release, official checksums, local SHA-256 hashes, bytes, and row counts | Authorized data engineer + data steward | Blocked/open |
| MA-05 | Analysis authority unknown | Classify each workbook, XES, image, notebook, and index as authoritative, superseded, historical, or invalid | Lead researcher + methods reviewer | Blocked/open |
| MA-06 | Notebook not portable | Replace hard-coded paths with approved VDI-relative configuration; lock dependencies and parameters in a future gated implementation | Authorized analyst + security | Blocked/open |
| MA-07 | Reproducibility absent | Add run IDs, code version, input hashes, environment, parameters, validation, and parent-artifact provenance | Lead researcher + methods reviewer | Blocked/open |
| MA-08 | Result claims unvalidated | Rerun only a pre-approved bounded pilot and obtain clinical/methods review before citing a result | Clinical expert + methods reviewer + supervisor | Blocked/open |

## 6. Go/no-go conclusion

**No-go for medical analysis.** The current resources support only planning, public literature work, and metadata reconciliation. The presence of files does not establish permission, completeness, integrity, reproducibility, clinical validity, or exportability.

The first executable medical step is not a model run. It is documentary closure of G1–G6 and the controlled resolution of the shared-Drive data location. Only after all six pass may D1 checksum/schema/row-count reconciliation run in the VDI, followed by a separately approved D2 bounded pilot.

## 7. Official references

- [MIMIC-III Clinical Database v1.4 — description, access requirements, 26-table model, release notes](https://physionet.org/content/mimiciii/1.4/)
- [PhysioNet credentialing and reuse FAQ](https://physionet.org/about/faqs/)
- [PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/)
- [Use of MIMIC Data with Large Language Models and Online Services](https://physionet.org/news/post/llm-responsible-use/)
