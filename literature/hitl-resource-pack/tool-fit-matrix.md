# HITL Tool Fit Matrix

This matrix assesses tools as support resources for VEGO-AI research. It is not approval to install or wire them into the classifier.

| Tool | Fit For VEGO-AI | Useful Now | Main Benefit | Main Risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Label Studio | External labeling UI for EXP-005 rows, reviewer rationales, and possible adjudication workflows. | Medium | Mature open-source labeling interface and export workflows. | Adds server setup, user management, export mapping, and IRB/publishability overhead. | Keep as candidate if CSV labeling becomes too slow or if 30-50+ labels are collected. |
| Argilla | Collaborative expert feedback and dataset curation for text-style records. | Medium | Strong fit for engineer/expert feedback loops and reusable labels. | Adds service state and dependency management; may duplicate current CSV gate. | Consider after EXP-005 proves the workflow needs a richer review UI. |
| modAL | Active-learning selection of high-value patterns for future expert review. | Low now / high later | Could rank uncertain or disagreement-heavy patterns for labeling. | Requires enough existing labels and a model loop; unsafe before EXP-005 has evidence. | Do not implement now; revisit after 20+ real safe labels. |
| cleanlab | Label-quality and disagreement checks after expert labels exist. | Low now / medium later | Can help detect noisy labels or review candidates when enough labeled data exists. | Not useful with 0 safe labels; could be misread as ground truth. | Record as future analysis option after EXP-005 labeling/adjudication. |

## Practical Decision

For the next supervisor session, stay with the existing EXP-005 blind CSV and adjudication sheet. The immediate bottleneck is real labels, not tooling.

If labeling scales beyond the current 24 safe candidates, the first tool to pilot should be Label Studio or Argilla, because both support human review workflows directly. modAL and cleanlab are analysis tools for later stages, after real labels exist.

