# Supervisor EXP-005 Label Approval Pack

Last updated: 2026-06-29 by Codex.

Purpose: give the supervisor one compact approval page for the MSc thesis evidence gate before any external
expert labeling begins. This pack does not contain copied CSV rows. It points to the generated local sheets
that should be reviewed, approved, filled, and rerun.

## 1. Why EXP-005 Matters

The thesis artifact is complete through M4B-1, and all thesis chapters now have drafts. The remaining
empirical blocker is independent expert labeling. EXP-005 is the gate that decides whether the current
mechanism can move from "traceability and readiness demonstrated" to quantitative reporting against real
expert labels.

Current state:

| Item | Status |
| --- | --- |
| Artifact build | Complete through M4B-1 |
| Thesis chapters | 10 of 10 drafted |
| Blind label package | Generated and ready for approval |
| Generalization-safe candidates | 24 |
| Supplied real labels | 0 |
| Current evidence verdict | Accuracy improvement cannot be evaluated yet. |

Until real labels exist, the thesis may report mechanism, traceability, escalation, and evaluation readiness.
It must not report classification-accuracy improvement or generalization.

## 2. Supervisor Decisions Needed

| Decision | Supervisor approval needed |
| --- | --- |
| Protocol | Confirm that the blind labeling protocol, allowed labels, confidence field, and rationale expectations are acceptable. |
| Reviewer panel | Confirm whether to use two independent reviewers, supervisor adjudication, or reviewer 2 plus supervisor adjudication. |
| Ethics and consent | Confirm reviewer consent/anonymity handling and whether existing IRB documentation is sufficient. |
| Minimum evidence target | Confirm that at least 20 generalization-safe labels are required before quantitative reporting. |
| Immediate label set | Confirm that the current 24 generalization-safe candidates are the immediate labeling target. |
| Claim boundary | Confirm no accuracy/generalization claim before the EXP-005 downstream gate passes. |
| Future policy gate | Confirm that M4B-1.1 or M4B-2 remains blocked unless real-label error analysis justifies it. |

Recommended default: approve the protocol only for label collection, not for policy changes. Keep M4B-1.1,
M4B-2, Agent 4 behavior changes, LLM/API calls, embeddings, and baseline-output changes out of scope.

## 3. Files To Review

Generated files are ignored by Git and should be regenerated rather than hand-edited, except where the file
is explicitly a human-filled label sheet.

| File | Use |
| --- | --- |
| `reports/generated/exp003/annotation_package/README.md` | Overview of the bias/leakage-controlled annotation package. |
| `reports/generated/exp003/annotation_package/blind_sheet_reviewer1.csv` | Reviewer 1 blind sheet. |
| `reports/generated/exp003/annotation_package/blind_sheet_reviewer2.csv` | Reviewer 2 blind sheet. |
| `reports/generated/exp003/annotation_package/annotation_sheet_audit.csv` | Internal audit context; do not send as the first reviewer-facing sheet. |
| `reports/generated/exp003/annotation_package/gold_labels.csv` | Final adjudicated label target after review/adjudication. |
| `reports/generated/exp005_label_review/exp005_label_review_blind.csv` | EXP-005 first-pass blind label-review sheet. |
| `reports/generated/exp005_label_review/exp005_adjudication_sheet.csv` | Reviewer-2 or supervisor adjudication sheet after first-pass labels exist. |
| `reports/generated/exp005_label_review/labeling_instructions.md` | Reviewer-facing labeling instructions. |
| `reports/generated/exp005_label_review/evidence_verdict.md` | Current gate verdict after EXP-005 validation. |
| `reports/generated/exp005_label_review/reproducibility_manifest.json` | Machine-readable rerun and provenance manifest. |

For supervisor review, start with `labeling_instructions.md`, `exp005_label_review_blind.csv`, and
`exp005_adjudication_sheet.csv`. Use audit files only to check what is hidden from reviewers and why.

## 4. Approved Label Values

Reviewers must use exactly one of these labels per pattern:

- `Substantial Variability`
- `Occasional Variability`
- `Undetermined / Needs Review`

Required human-filled fields are:

- `expert_label`
- `expert_rationale`
- `reviewer_id`
- `review_date`
- `confidence`

Optional notes are allowed for ambiguity, uncertainty, or protocol concerns.

## 5. Intended Workflow

1. Supervisor reviews this approval pack and the generated instructions/sheets.
2. Supervisor confirms protocol, reviewer plan, ethics/consent handling, and claim boundary.
3. Reviewer 1 fills the blind sheet.
4. Reviewer 2 independently fills the second blind sheet, or the supervisor fills/adjudicates using the adjudication sheet.
5. Disagreements are adjudicated into `gold_labels.csv`.
6. The downstream gate is rerun with real labels:

```powershell
.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream
```

7. Chapter 7 is updated only after the rerun produces real-label accuracy, macro-F1, paired-correctness,
and reliability outputs.

## 6. Claim Boundary

Before EXP-005 has real labels:

- Allowed: mechanism readiness, traceability, escalation, non-destructive comparison, label-package readiness.
- Not allowed: classification-accuracy improvement, generalization, policy-change justification, M4B-2 readiness.

With 1-19 generalization-safe real labels:

- Allowed: pilot/exploratory reporting with explicit small-sample limitations.
- Not allowed: strong quantitative claims.

With at least 20 generalization-safe real labels:

- Allowed: quantitative original-vs-memory-informed-vs-expert reporting with limitations.
- Still required: leakage filtering, reliability/adjudication discussion, and evidence-consistency guard.

With reviewer-2 or supervisor adjudication:

- Allowed: stronger discussion of label reliability, including agreement/adjudication outcomes.

## 7. Acceptance Checklist

Before sending sheets to reviewers:

- [ ] Supervisor approves the label values and rationale/confidence requirements.
- [ ] Supervisor confirms reviewer anonymity/consent handling.
- [ ] Supervisor confirms whether reviewer 2 is independent or supervisor-adjudicated.
- [ ] Reviewer-facing sheets are blind; AI labels and memory-informed labels are not shown.
- [ ] Audit/context files are kept internal.
- [ ] EXP-005 remains framed as evidence collection, not a policy-change approval.
- [ ] The thesis claim boundary is understood: no accuracy/generalization claim before real labels.

After labels return:

- [ ] Filled CSV is saved and closed before rerun to avoid Windows file locks.
- [ ] `.\scripts\build-exp005-label-review.ps1 -FilledLabelsSheet <filled-sheet> -RunDownstream` is executed.
- [ ] `python scripts\check_evidence_consistency.py` passes.
- [ ] `docs/PROGRESS_TRACKER.md`, the E2E dashboard, and Chapter 7 are refreshed from the real-label outputs.
