# Risk Register

| ID | Risk | Impact | Probability | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| RISK-001 | No baseline Git commit yet. | Reverts are weaker. | High | Baseline GitHub history exists on `main`; keep committing safe changes and avoid force pushes. | Resolved |
| RISK-002 | Data sensitivity is not fully audited. | Accidental disclosure. | Medium | Complete data management and IRB checklist. | Open |
| RISK-003 | LLM outputs may drift over time. | Reproducibility risk. | High | Record model/API settings and preserve outputs used in claims. | Open |
| RISK-004 | Existing outputs may be mixed with future reruns. | Analysis confusion. | Medium | Use experiment IDs and output manifests. | Open |
| RISK-005 | Code changes may alter scientific behavior. | Invalid comparisons. | Medium | Add tests and require experiment notes for behavior changes. | Open |
| RISK-006 | Confluence can drift from repository memory. | External wiki becomes misleading. | Medium | Generate curated wiki pages after memory updates at the end of every meaningful prompt. | Open |
| RISK-007 | Confluence target IDs are not configured yet. | Live wiki sync is pending. | Medium | Use `docs/confluence/wiki-sync-config.local.json` when available; otherwise generate ignored outbox pages. | Open |
