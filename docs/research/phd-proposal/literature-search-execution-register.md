# Literature Search Execution Register - QL-01 through QL-05

Owner: Ali

Status: **PROTOCOL READY / NOT RUN**

Primary review window: 2015-2026; older seminal work may enter only through recorded backward/forward snowballing

This register freezes the first five literature-query concepts before
execution. It is an execution interface, not evidence that a database was
searched. Every query and database row remains `Protocol ready / not run` until
Ali records the actual platform, exact executed syntax, date/time, hit count,
export, and screening evidence.

The native literature workbook remains the row-level source of search,
screening, and synthesis records. One paper occupies one row; authors'
conclusions remain separate from Ali's synthesis.

## 1. Protocol controls

| Control | Rule |
| --- | --- |
| Databases | ACM Digital Library, IEEE Xplore, Scopus, and Web of Science for software/AI/HCI; PubMed for the medical branch |
| Date window | 2015-2026 for the primary search; older seminal work only through documented snowballing |
| Publication types | Peer-reviewed research, preprints, standards, and tool documentation are tagged separately; tools are not research evidence |
| Identity verification | DOI, title, authors, year, venue, publication type, and source URL are verified before inclusion |
| Deduplication | DOI first; then normalized title/year/first-author with manual review of ambiguous matches |
| Screening | Title/abstract first, then full text; every exclusion receives a controlled reason |
| Synthesis | Each included paper maps to taxonomy tags, SQ, study, Plan A/B, evidence, limitation, contradiction, gap, and contribution use |
| Claim rule | An unrun query, seed row, tool page, or preprint cannot establish novelty, effectiveness, or review completeness |

## 2. Exact frozen protocol queries

The text in each code block is the exact canonical Boolean expression. At
execution, copy it without silently changing concepts. Platform-required field
wrappers, escaping, and filters must be captured verbatim in the
`Exact_executed_query` field before results are interpreted.

| Query ID | Frozen concept | Status |
| --- | --- | --- |
| QL-01 | Agentic or multi-agent AI with human oversight | Protocol ready / not run |
| QL-02 | Expert feedback, knowledge capture, memory, and reusable judgment | Protocol ready / not run |
| QL-03 | Domain modeling, assessment, variability, and conformance | Protocol ready / not run |
| QL-04 | Intervention workload, governance, trust, and evaluation | Protocol ready / not run |
| QL-05 | Clinical guidelines, CDSS overrides, alert fatigue, and healthcare process mining | Protocol ready / not run |

### QL-01 - Agentic or multi-agent AI with human oversight

```text
("agentic AI" OR "AI agent" OR "AI agents" OR "multi-agent system" OR "multi-agent systems" OR "multiagent system" OR "multiagent systems") AND ("human oversight" OR "human-in-the-loop" OR "human in the loop" OR "human-on-the-loop" OR "human on the loop" OR "human intervention" OR "expert review")
```

Target databases: ACM Digital Library, IEEE Xplore, Scopus, Web of Science.

Primary mapping: SQ1, Study 1, intervention architecture and authority.

### QL-02 - Expert feedback, knowledge capture, memory, and reusable judgment

```text
("expert feedback" OR "human feedback" OR "expert judgment" OR "expert judgements" OR "human judgment" OR "human judgements") AND ("knowledge capture" OR "knowledge reuse" OR "judgment reuse" OR "judgement reuse" OR memory OR provenance OR reconciliation) AND (AI OR "artificial intelligence" OR agent OR agents)
```

Target databases: ACM Digital Library, IEEE Xplore, Scopus, Web of Science.

Primary mapping: SQ2, Study 2, governed judgment lifecycle.

### QL-03 - Domain modeling, assessment, variability, and conformance

```text
("domain model" OR "domain models" OR "conceptual model" OR "conceptual models" OR "process model" OR "process models" OR "variability model" OR "variability models" OR "software model" OR "software models") AND (assessment OR evaluation OR validation OR "conformance checking" OR "conformance check" OR comparison) AND (AI OR "artificial intelligence" OR agent OR agents OR automated)
```

Target databases: ACM Digital Library, IEEE Xplore, Scopus, Web of Science.

Primary mapping: software/modeling baseline, Studies 1-3, Plan B transfer.

### QL-04 - Intervention workload, governance, trust, and evaluation

```text
("human intervention" OR "expert review" OR "human-AI collaboration" OR "human AI collaboration" OR "human-in-the-loop" OR "human in the loop") AND (workload OR burden OR dosage OR timing OR uncertainty OR trust OR governance) AND (evaluation OR experiment OR experiments OR "controlled study" OR "controlled studies" OR usability)
```

Target databases: ACM Digital Library, IEEE Xplore, Scopus, Web of Science.

Primary mapping: SQ1 and SQ3, expert effort, usability, validity, and governance.

### QL-05 - Clinical guidelines, CDSS overrides, alert fatigue, and healthcare process mining

```text
(("clinical decision support"[Title/Abstract] OR CDSS[Title/Abstract] OR "clinical guideline"[Title/Abstract] OR "clinical guidelines"[Title/Abstract] OR "healthcare process mining"[Title/Abstract]) AND (override*[Title/Abstract] OR "alert fatigue"[Title/Abstract] OR "human oversight"[Title/Abstract] OR "expert feedback"[Title/Abstract] OR conformance[Title/Abstract])) AND ("2015/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
```

Target database: PubMed.

Primary mapping: conditional Plan A literature only; this query does not select
a medical use case, dataset, or partner.

## 3. Planned database execution matrix

Every row is deliberately unexecuted.

| Query ID | Database | Planned field/filter handling | Status | Run date/time | Runner | Exact executed query | Hits | Export/evidence |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| QL-01 | ACM Digital Library | Title/abstract/keywords where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-01 | IEEE Xplore | Metadata/abstract/index terms where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-01 | Scopus | `TITLE-ABS-KEY`; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-01 | Web of Science | Topic field; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-02 | ACM Digital Library | Title/abstract/keywords where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-02 | IEEE Xplore | Metadata/abstract/index terms where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-02 | Scopus | `TITLE-ABS-KEY`; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-02 | Web of Science | Topic field; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-03 | ACM Digital Library | Title/abstract/keywords where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-03 | IEEE Xplore | Metadata/abstract/index terms where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-03 | Scopus | `TITLE-ABS-KEY`; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-03 | Web of Science | Topic field; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-04 | ACM Digital Library | Title/abstract/keywords where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-04 | IEEE Xplore | Metadata/abstract/index terms where supported; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-04 | Scopus | `TITLE-ABS-KEY`; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-04 | Web of Science | Topic field; 2015-2026 | Protocol ready / not run | Not run | Ali | Pending execution | - | None |
| QL-05 | PubMed | Title/Abstract terms plus explicit publication-date range in the query | Protocol ready / not run | Not run | Ali | Pending execution | - | None |

## 4. Execution record required for each run

For every database row, record all fields before screening begins:

- query ID, database, database URL/interface, and access route;
- date/time and timezone;
- runner;
- exact executed query copied from the platform;
- filters, field restrictions, sort order, and pagination/result cap;
- total hits returned;
- export format, filename/path, row count, and SHA-256;
- errors, warnings, or platform transformations;
- deduplication batch ID and method;
- title/abstract screening counts and exclusion reasons;
- full-text screening counts and exclusion reasons; and
- workbook import/reconciliation evidence.

## 5. Search-level acceptance

A QL item moves from `Protocol ready / not run` only when all planned database
rows for that item have an execution record or an approved, explained
not-applicable disposition. A completed query is not a completed literature
review. Review completion additionally requires deduplication, screening,
identity and claim verification, quality appraisal, critical synthesis,
gap-to-contribution mapping, and supervisor review.
