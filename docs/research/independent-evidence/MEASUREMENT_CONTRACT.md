# Independent Measurement Contract

## Frozen comparators

| ID | Meaning | Current use |
| --- | --- | --- |
| B0 | Original Agent 4 output | Frozen primary baseline |
| B1 | Current advisory/memory-informed comparison | Mechanism comparator; currently 0/27 changes |
| B3 | One development-derived deterministic proposal | Does not exist; requires evidence and approval |
| B4 | The frozen B3 policy on eight sealed rows | One-time pilot only |
| B5 | Frozen policy on an external education batch | Required before formal generalization |

## Classification definitions

- **Accuracy:** correct classifications divided by evaluated gold rows.
- **Macro-F1:** unweighted mean of the three class F1 values. A missing class
  receives F1 zero under this fixed-class protocol.
- **Balanced accuracy:** unweighted mean of the three class recalls.
- **Net correction:** candidate-only correct minus baseline-only correct.
- **Paired significance:** two-sided exact McNemar test on discordant rows.
- **Uncertainty:** Wilson 95% interval for accuracy; paired bootstrap is required
  in the later full evaluator for macro-F1 and net-correction deltas.

The three classes are:

1. `Substantial Variability`.
2. `Occasional Variability`.
3. `Undetermined / Needs Review`.

## Routing definitions

Each independent reviewer records:

- classification;
- whether human review is required;
- routing rationale;
- review priority;
- confidence;
- active review time.

After adjudication:

- Positive routing target = `Human review required` or `Insufficient context`.
- Negative routing target = `Automatic handling acceptable`.
- Routing measures = precision, recall, F1, workload rate, false-negative count,
  and high-priority recall.

No routing default is selected from synthetic targets.

## Comparison eligibility

Two plotted results must share:

- dataset and partition hash;
- gold-label freeze hash;
- baseline revision;
- prompt and model version;
- policy version;
- metric definition;
- evidence and leakage class.

If any item differs, the result is `Not directly comparable`. Synthetic and
empirical rows never share a headline delta.

## Claim decisions

| Evidence | Allowed wording |
| --- | --- |
| Package and validators only | Evaluation-ready |
| Development N=16 | Development result; proposal generation only |
| Sealed N=8 | Holdout pilot |
| External adjudicated N≥30, target 48 | Formal paired evaluation eligible |
| Positive net-correction CI excludes zero, McNemar p<0.05, no macro-F1 decline, no predefined subgroup harm | Positive result for that frozen cohort and protocol |

None of these gates authorize Agent 4 changes or baseline overwrites.
