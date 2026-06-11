# Risk Register

| ID | Risk | Impact | Probability | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| RISK-001 | No baseline Git commit yet. | Reverts are weaker. | High | Initialize Git and create baseline commit after reviewing ignored files. | Open |
| RISK-002 | Data sensitivity is not fully audited. | Accidental disclosure. | Medium | Complete data management and IRB checklist. | Open |
| RISK-003 | LLM outputs may drift over time. | Reproducibility risk. | High | Record model/API settings and preserve outputs used in claims. | Open |
| RISK-004 | Existing outputs may be mixed with future reruns. | Analysis confusion. | Medium | Use experiment IDs and output manifests. | Open |
| RISK-005 | Code changes may alter scientific behavior. | Invalid comparisons. | Medium | Add tests and require experiment notes for behavior changes. | Open |

