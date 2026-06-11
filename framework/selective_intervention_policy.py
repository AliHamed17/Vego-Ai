"""
selective_intervention_policy.py — decide WHEN a human should be asked.

Milestone 1 of the Human–AI Co-Reasoning extension. Pure Python, no LLM call.

VEGO-AI is fully automated: Agent 4 (Variability Explorer) emits a classification
for every recurring deviation pattern, including the fields `confidence`,
`flag_for_guidelines_update`, and `requires_human_review` — but nothing in the
pipeline ever acts on them. This module reads ONE such classification entry and
decides whether it warrants human judgment, returning the concrete reasons.

The goal is *selective* intervention: ask the human only where a decision is
uncertain or would change the assessment rubric, not for every pattern.

Trigger reasons (all that apply are collected)
----------------------------------------------
  agent_requested_human_review  : Agent 4 set requires_human_review = true.
  undetermined_classification   : classification == "Undetermined".
  low_confidence                : confidence == "Low".
  medium_confidence             : confidence == "Medium" (only if include_medium).
  guideline_update_proposed     : flag_for_guidelines_update == true
                                  (a proposed change to the reference guidelines /
                                  rubric — the human owns the rubric, so this is
                                  always surfaced for validation).

Note: in the committed VEGO-AI outputs, `requires_human_review` is always false
and there are no "Undetermined" patterns, so the confidence- and guideline-update
triggers are what make the queue non-empty on the existing experimental data.
"""

from __future__ import annotations

# Bump whenever the trigger logic below changes, so review items remain
# comparable across experiments and policy revisions.
POLICY_VERSION = "human-review-policy-v1"

# Exact strings emitted by agent4_variability_explorer.py
CLASSIFICATION_UNDETERMINED = "undetermined"
CONFIDENCE_LOW = "low"
CONFIDENCE_MEDIUM = "medium"

TRIGGER_AGENT_REQUESTED = "agent_requested_human_review"
TRIGGER_UNDETERMINED = "undetermined_classification"
TRIGGER_LOW_CONFIDENCE = "low_confidence"
TRIGGER_MEDIUM_CONFIDENCE = "medium_confidence"
TRIGGER_GUIDELINE_UPDATE = "guideline_update_proposed"


def should_request_human_review(
    entry: dict,
    *,
    include_medium: bool = True,
) -> tuple[bool, list[str]]:
    """
    Decide whether a single Agent 4 variability classification needs human review.

    Parameters
    ----------
    entry          : One element of variability_classifications (Agent 4 output),
                     e.g. {"pattern_id": "P4", "classification": "Substantial Variability",
                           "confidence": "Medium", "flag_for_guidelines_update": true,
                           "requires_human_review": false, ...}.
    include_medium : Treat Medium confidence as a trigger (default True). Set False
                     to escalate only Low-confidence / Undetermined / flagged cases.

    Returns
    -------
    (needs_review, trigger_reasons)
        needs_review   : True if at least one trigger fired.
        trigger_reasons: list of trigger-reason codes (see module docstring).
    """
    reasons: list[str] = []

    if entry.get("requires_human_review") is True:
        reasons.append(TRIGGER_AGENT_REQUESTED)

    classification = str(entry.get("classification", "")).strip().lower()
    if classification == CLASSIFICATION_UNDETERMINED:
        reasons.append(TRIGGER_UNDETERMINED)

    confidence = str(entry.get("confidence", "")).strip().lower()
    if confidence == CONFIDENCE_LOW:
        reasons.append(TRIGGER_LOW_CONFIDENCE)
    elif confidence == CONFIDENCE_MEDIUM and include_medium:
        reasons.append(TRIGGER_MEDIUM_CONFIDENCE)

    if entry.get("flag_for_guidelines_update") is True:
        reasons.append(TRIGGER_GUIDELINE_UPDATE)

    return (len(reasons) > 0, reasons)
