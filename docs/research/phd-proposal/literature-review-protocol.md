# Literature Review and Evidence-Matrix Protocol

Version: 0.1
Date: 2026-07-30
Owner: Ali
Status: **protocol and seed tranche implemented; database searches and screening not yet executed**

## Purpose

Build a reproducible critical literature review that tests the proposed gap,
identifies contradictions and boundary conditions, and connects supported gaps
to SQ1-SQ3, the three studies, and the proposal contribution. The workbook is
an evidence-control system, not a catalogue of summaries.

Operational workbook:
[VEGO-AI PhD Literature Workbook v0.1](https://docs.google.com/spreadsheets/d/1tVAM10bxlmL7_8SbgDgN5BRfAR2f5Q4pGvQmx-Ypp4A/edit).

## Sources and search roles

| Source | Role |
| --- | --- |
| ACM Digital Library | Primary software engineering, AI, agentic systems, and HCI search |
| IEEE Xplore | Primary software/modeling, AI, and systems search |
| Scopus | Multidisciplinary search, deduplication support, and citation tracking |
| Web of Science | Multidisciplinary corroboration and citation tracking |
| PubMed | Conditional Plan A medical literature only |
| Google Scholar | Backward/forward snowballing after anchor papers, not the primary systematic database |

The primary publication window is 2015-2026. Older work is admitted only when
it is seminal and reached through a documented backward/forward snowballing
chain. Peer-reviewed research, preprints, standards/official guidance, and tool
documentation remain separate publication types.

## Concept groups

1. agentic or multi-agent AI plus human oversight;
2. expert feedback, knowledge capture, memory, and reusable judgment;
3. domain modeling, model assessment, variability, and conformance;
4. intervention workload, governance, trust, and evaluation; and
5. clinical guidelines, CDSS overrides, alert fatigue, and healthcare process
   mining for the conditional Plan A branch.

Every executed query records database, exact query string, filters, date,
returned count, screened count, included count, searcher, and notes in
`Search_Log`. Prepared queries remain `Protocol ready` until actually run.

## Screening protocol

### Inclusion

A record may be included when:

- its identity and venue/publication type are verified;
- its objective, method, evidence/data, results, conclusions, and limitations
  can be extracted from the source;
- it informs at least one SQ, construct, method, metric, threat, or transfer
  boundary; and
- its access/license permits the intended reading and citation.

### Exclusion

Exclude with a recorded reason when the item is duplicate, unverifiable,
outside scope, lacks usable scholarly/official evidence, is only marketing
material, or cannot support the proposed use. Tool documentation stays in
`Resources`; it does not become research evidence.

### Two-stage decision

1. title/abstract screening;
2. full-text or authoritative-document screening.

`Needs verification` is not `Included`. Candidate medical sources require DOI,
venue, and claim verification before any substantive proposal statement uses
them.

## Workbook contract

`Papers` contains one paper per row and these three field groups:

- bibliographic identity and search provenance;
- authors' study, evidence, results, conclusions, and limitations; and
- Ali's taxonomy mapping, gap assessment, quality, transferability, synthesis,
  decision, and follow-up.

`Authors_Conclusions` and `Researcher_Synthesis` must never be merged or
silently paraphrased into one field. `Screening` records identity,
deduplication, staged decisions, reviewer, date, evidence link, and exclusion
reason. `Taxonomy_and_Gaps` records current coverage, open/blocked categories,
study/contribution mapping, and the next evidence-producing search.

## Quality and synthesis

Quality is assessed against fit-for-purpose criteria:

- verified identity and source authority;
- transparent study design and unit of analysis;
- appropriate baseline/comparator;
- data/sample suitability;
- valid metrics and analysis;
- limitations and threats;
- reproducibility/provenance; and
- transferability to the defined SQ and study.

The synthesis must compare findings, disagreements, methods, evidence strength,
limitations, and unexplained gaps. A gap remains `Preliminary` until the
relevant searches, screening, quality review, and supervisor review support it.

## Reproducibility and update cadence

- Deduplicate by DOI first, then normalized title/venue/year.
- Record every query and snowballing chain.
- Preserve excluded records and reasons.
- Review the matrix weekly while the proposal is active.
- Record the reviewer and review date for every inclusion decision.
- Version proposal claims against workbook paper IDs rather than unsupported
  prose.
- Re-run coverage checks after taxonomy or SQ wording changes.

## Current seed state

The workbook currently includes four verified academic/official resource-pack
anchors, retains the VEGO-AI baseline as `Needs verification` until final
publication metadata are available, and lists one supporting modeling paper as
a candidate pending identity/full-text verification. No search-result count,
medical-paper claim, or literature-saturation claim is made yet.

## Acceptance tests

- one paper per row;
- authors' conclusions separate from Ali's synthesis;
- every `Included` record has verified identity and rationale;
- tools are not counted as research evidence;
- every active taxonomy category has evidence or an explicit gap;
- queries, dates, deduplication, screening, and exclusion reasons are
  reproducible; and
- every proposal gap cites workbook paper IDs and maps to a study/contribution.
