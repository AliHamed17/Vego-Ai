# Risk and Validity Register — Thesis Evidence Phase

Status: active from 2026-07-24.

| ID | Risk or threat | Likelihood | Impact | Trigger | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-E01 | No independent labels | High | Critical | Supplied safe labels remain 0 | Stop performance analysis; escalate protocol approval and reviewer scheduling | Supervisor | Open |
| R-E02 | Fewer than 20 safe labels | Medium | High | Adjudicated safe N is 1-19 | Report pilot-only findings; do not select a policy or make a strong claim | Researcher | Open |
| R-E03 | Same-pattern leakage | High | Critical | Same-pattern row enters a primary metric | Schema rejection and per-row leakage filtering | Researcher | Controlled |
| R-E04 | Single-reviewer bias | Medium | High | Only one return exists | Require reviewer 2 and adjudication before gold-label freeze | Supervisor | Open |
| R-E05 | Low inter-rater agreement | Medium | High | Kappa or disagreement pattern indicates unstable construct | Analyze disagreements, revise definitions, rerun calibration before evaluation | Adjudicator | Open |
| R-E06 | No candidate-policy changes | High | Medium | M4B-1 remains 0/27 changes | Report mechanism value; do not imply accuracy benefit | Researcher | Current |
| R-E07 | Candidate harms correct baseline rows | Medium | Critical | changed-and-wrong exceeds changed-and-correct | Reject or defer policy; preserve baseline | Supervisor | Open |
| R-E08 | Overfitting to 16 development rows | High | High | Policy complexity grows or rules reference row-specific details | One simple deterministic candidate, frozen before holdout | Researcher | Open |
| R-E09 | Holdout leakage | Medium | Critical | Holdout membership or outcomes inspected before freeze | Private manifest, hash checks, one-time run, deviation log | Researcher | Open |
| R-E10 | Class prevalence distortion | High | High | Undetermined remains absent or a class is sparse | Report per-class metrics, macro-F1, Wilson intervals, and prevalence | Researcher | Open |
| R-E11 | Small sealed holdout | Certain | High | Holdout N=8 | Treat as pilot only; require EXP-025 for formal claim | Researcher | Controlled |
| R-E12 | Limited education domains/settings | High | High | Results cover only Cheers/ParkWise or current settings | Restrict scope and collect external education batch | Supervisor | Open |
| R-E13 | Human-effort claim inferred from queue counts | Medium | High | Review count is described as time saved | Keep EXP-026 separate; require timestamped controlled sessions | Researcher | Controlled |
| R-E14 | Synthetic evidence misrepresented | Medium | Critical | EXP-004/009/010 result enters empirical performance text | Label `SYNTHETIC_NOT_HUMAN`; claim-language guard | Researcher | Controlled |
| R-E15 | Baseline drift | Low | Critical | Baseline hash differs | Stop run; restore accepted baseline through reviewed Git workflow | Researcher | Controlled |
| R-E16 | Protected runtime drift | Low | Critical | Protected-path check fails | Stop run; no staging or publication | Researcher | Controlled |
| R-E17 | Report inconsistency | Medium | High | Chapter, dashboard, and snapshot counts differ | Generate from ThesisEvidenceSnapshot-v1 and validate freshness | Researcher | Mitigated |
| R-E18 | Reviewer privacy or consent gap | Medium | High | Reviewer records lack approved handling | Do not collect; resolve ethics/consent decision first | Supervisor | Open |
| R-E19 | Multiple unregistered analyses | Medium | High | New metric or subgroup appears after outcome inspection | Record deviation; label exploratory; keep primary analysis unchanged | Researcher | Open |
| R-E20 | Positive-result pressure | Medium | Critical | Request to guarantee or tune for improvement | Preserve preregistration, null results, and gate language | Researcher and supervisors | Controlled |

## Release blockers

Any of the following stops quantitative publication:

- Missing reviewer provenance.
- Missing or unknown leakage status.
- Non-frozen policy or partition.
- Baseline or protected-path hash mismatch.
- Zero safe labels.
- Unadjudicated disagreements treated as gold labels.
- Synthetic labels mixed with human records.
- Outcome-dependent protocol changes without a dated deviation.
