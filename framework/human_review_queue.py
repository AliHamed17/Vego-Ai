"""
human_review_queue.py — build and persist the Human Review Queue.

Milestone 1 of the Human–AI Co-Reasoning extension. Pure Python, no LLM call.

Given Agent 4's two outputs for one setting —
  * the variability classifications (skill 4-2), and
  * the deviation patterns (skill 4-1) —
this module asks the Selective Intervention Policy which classifications warrant
human judgment, joins each flagged classification with its pattern (for the
description, affected cases, and recurrence strength), and writes one
`human_review_queue.jsonl` file (one JSON object per line) conforming to
`schemas/human_review_item.schema.json`.

It is used two ways:
  1. As a thin, non-breaking hook inside orchestrator.py / evaluator.py.
  2. As a standalone CLI over the COMMITTED eval_output/ JSONs — no API key needed:

       python human_review_queue.py --from-eval-output ../eval_output/ucd_ch
       python human_review_queue.py --all-settings ../eval_output
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

try:  # allow both `import ...` (package-less sibling) and module use
    from selective_intervention_policy import should_request_human_review
except ImportError:  # pragma: no cover - fallback when imported as a package
    from .selective_intervention_policy import should_request_human_review  # type: ignore

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0.0"
PIPELINE_STAGE = "agent4_classify_variability"
QUEUE_FILENAME = "human_review_queue.jsonl"

# setting_id → (domain, diagram_type) fallback when not present in the JSON
_DOMAIN_BY_CODE = {"ch": "cheers", "pw": "parkwise"}
_DIAGRAM_BY_CODE = {"ucd": "UCD", "cd": "CD"}

_GUIDELINE_IN_EVIDENCE = re.compile(r"\b(G\d+)\b")


# ---------------------------------------------------------------------------
# Setting-id helpers
# ---------------------------------------------------------------------------

def derive_domain_and_diagram(setting_id: str) -> tuple[str, str]:
    """Map a setting_id like 'ucd_ch' → ('cheers', 'UCD'). Best-effort."""
    parts = setting_id.split("_")
    diagram = _DIAGRAM_BY_CODE.get(parts[0].lower(), "") if parts else ""
    domain = _DOMAIN_BY_CODE.get(parts[1].lower(), "") if len(parts) > 1 else ""
    return domain, diagram


# ---------------------------------------------------------------------------
# Pattern indexing / normalisation
# ---------------------------------------------------------------------------

def _normalize_strength(value) -> str | None:
    """Accept both the v1.0/1.1 string ('22.5%') and the v1.2 object form."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("percentage")
    return str(value)


def index_patterns(deviation_patterns: dict) -> dict[str, dict]:
    """
    Build pattern_id → {kind, guideline_id, description, affected_cases, pattern_strength}.

    Handles recurring_guideline_patterns (kind='guideline') and
    recurring_fragment_patterns (kind='fragment').
    """
    index: dict[str, dict] = {}
    for p in deviation_patterns.get("recurring_guideline_patterns", []) or []:
        pid = p.get("pattern_id")
        if not pid:
            continue
        index[pid] = {
            "kind": "guideline",
            "guideline_id": p.get("guideline_id"),
            "description": p.get("description", ""),
            "affected_cases": p.get("affected_cases", []) or [],
            "pattern_strength": _normalize_strength(p.get("pattern_strength")),
        }
    for p in deviation_patterns.get("recurring_fragment_patterns", []) or []:
        pid = p.get("pattern_id")
        if not pid:
            continue
        index[pid] = {
            "kind": "fragment",
            "guideline_id": p.get("guideline_id"),  # usually absent on fragment patterns
            "description": p.get("description", ""),
            "affected_cases": p.get("affected_cases", []) or [],
            "pattern_strength": _normalize_strength(p.get("pattern_strength")),
        }
    return index


def _guideline_from_evidence(evidence: str | None) -> str | None:
    """Fallback: extract a guideline id (Gj) referenced in the classification evidence."""
    if not evidence:
        return None
    m = _GUIDELINE_IN_EVIDENCE.search(evidence)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Core builder
# ---------------------------------------------------------------------------

def build_review_items(
    variability_classes: dict,
    deviation_patterns: dict,
    setting_id: str,
    *,
    include_medium: bool = True,
) -> list[dict]:
    """
    Produce schema-valid review items for the classifications that need human review.

    Parameters
    ----------
    variability_classes : Agent 4 skill 4-2 output (has 'variability_classifications').
    deviation_patterns  : Agent 4 skill 4-1 output (has recurring_*_patterns).
    setting_id          : e.g. 'ucd_ch'.
    include_medium      : passed through to the Selective Intervention Policy.

    Returns
    -------
    list of review-item dicts (possibly empty), in pattern order.
    """
    pattern_index = index_patterns(deviation_patterns or {})
    domain_default, diagram_default = derive_domain_and_diagram(setting_id)
    domain = variability_classes.get("domain_identifier") or domain_default
    created_at = datetime.now(timezone.utc).isoformat()

    items: list[dict] = []
    for entry in variability_classes.get("variability_classifications", []) or []:
        needs_review, reasons = should_request_human_review(
            entry, include_medium=include_medium
        )
        if not needs_review:
            continue

        pid = entry.get("pattern_id", "")
        pattern = pattern_index.get(pid, {})
        related_guideline = pattern.get("guideline_id") or _guideline_from_evidence(
            entry.get("evidence")
        )

        items.append(
            {
                "review_id": f"HRQ-{setting_id}-{pid}",
                "schema_version": SCHEMA_VERSION,
                "created_at": created_at,
                "setting_id": setting_id,
                "domain": domain,
                "diagram_type": diagram_default,
                "pipeline_stage": PIPELINE_STAGE,
                "pattern_id": pid,
                "pattern_kind": pattern.get("kind", "unknown"),
                "target_fragment": pattern.get("description", ""),
                "related_guideline_id": related_guideline,
                "affected_cases": pattern.get("affected_cases", []),
                "pattern_strength": pattern.get("pattern_strength"),
                "ai_decision": {
                    "classification": entry.get("classification", ""),
                    "confidence": entry.get("confidence", ""),
                    "justification": entry.get("justification", ""),
                    "evidence": entry.get("evidence", ""),
                    "flag_for_guidelines_update": bool(
                        entry.get("flag_for_guidelines_update", False)
                    ),
                    "requires_human_review": bool(
                        entry.get("requires_human_review", False)
                    ),
                },
                "trigger_reasons": reasons,
                "status": "pending",
                "feedback_id": None,
            }
        )
    return items


def write_queue(items: list[dict], path: Path) -> None:
    """
    Write items as JSONL (one object per line), deduplicated by review_id.

    Deterministic rebuild: the file is overwritten from the current items, so
    re-running on the same outputs yields the same queue (no accumulation).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    with open(path, "w", encoding="utf-8") as fh:
        for item in items:
            rid = item.get("review_id")
            if rid in seen:
                continue
            seen.add(rid)
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info("Human review queue -> %s (%d item(s))", path, len(seen))


def build_and_write_for_setting(
    variability_classes: dict,
    deviation_patterns: dict,
    setting_id: str,
    output_dir: Path,
    *,
    include_medium: bool = True,
) -> list[dict]:
    """Convenience used by the pipeline hooks: build + write in one call."""
    items = build_review_items(
        variability_classes, deviation_patterns, setting_id,
        include_medium=include_medium,
    )
    write_queue(items, Path(output_dir) / QUEUE_FILENAME)
    return items


# ---------------------------------------------------------------------------
# Standalone CLI — runs over committed eval_output/ JSONs (no API key)
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _first_match(eval_dir: Path, prefix: str) -> Path | None:
    """Find agentD output files allowing committed suffix variants.

    Standard:  agentD_variability_classes.json
    Variant :  agentD_variability_classes__cd_ch.json  (committed cd_ch naming)
    """
    exact = eval_dir / f"{prefix}.json"
    if exact.exists():
        return exact
    matches = sorted(eval_dir.glob(f"{prefix}*.json"))
    return matches[0] if matches else None


def _run_for_eval_dir(eval_dir: Path, include_medium: bool) -> int:
    """Read agentD_*.json from one eval_output/<setting> dir and write the queue."""
    setting_id = eval_dir.name
    vc_path = _first_match(eval_dir, "agentD_variability_classes")
    dp_path = _first_match(eval_dir, "agentD_deviation_patterns")
    if vc_path is None:
        logger.warning("Skip %s - no agentD_variability_classes*.json", setting_id)
        return 0
    variability_classes = _load_json(vc_path)
    deviation_patterns = _load_json(dp_path) if dp_path else {}
    items = build_and_write_for_setting(
        variability_classes, deviation_patterns, setting_id, eval_dir,
        include_medium=include_medium,
    )
    print(f"{setting_id}: {len(items)} review item(s) -> {eval_dir / QUEUE_FILENAME}")
    for it in items:
        print(f"    {it['pattern_id']:>3}  "
              f"{it['ai_decision']['classification']:<24} "
              f"conf={it['ai_decision']['confidence']:<6} "
              f"triggers={','.join(it['trigger_reasons'])}")
    return len(items)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build the VEGO-AI Human Review Queue from Agent 4 outputs (no API key)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-eval-output", metavar="DIR",
                       help="One eval_output/<setting> directory.")
    group.add_argument("--all-settings", metavar="ROOT",
                       help="An eval_output root; processes every subdirectory with agentD outputs.")
    parser.add_argument("--no-include-medium", action="store_true",
                        help="Escalate only Low-confidence / Undetermined / guideline-update cases.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    include_medium = not args.no_include_medium

    total = 0
    if args.from_eval_output:
        total = _run_for_eval_dir(Path(args.from_eval_output), include_medium)
    else:
        root = Path(args.all_settings)
        for sub in sorted(p for p in root.iterdir() if p.is_dir()):
            total += _run_for_eval_dir(sub, include_medium)
    print(f"\nTotal review items: {total}")


if __name__ == "__main__":
    main()
