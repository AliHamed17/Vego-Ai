"""
human_review_queue.py — build and persist the Human Review Queue.

Milestone 1 of the Human-AI Co-Reasoning extension. Pure Python, no LLM call.

Given Agent 4's two outputs for one setting —
  * the variability classifications (skill 4-2), and
  * the deviation patterns (skill 4-1) —
this module asks the Selective Intervention Policy which classifications warrant
human judgment, joins each flagged classification with its pattern (for the
description, affected cases, and recurrence strength), and writes one
`human_review_queue.jsonl` file (one JSON object per line) conforming to
`schemas/human_review_item.schema.json`.

It is used two ways:
  1. As a thin, non-breaking hook inside orchestrator.py / evaluator.py
     (writes into the pipeline's own output_dir).
  2. As a standalone CLI over the COMMITTED eval_output/ JSONs — no API key:

       python human_review_queue.py --from-eval-output ../eval_output/ucd_ch
       python human_review_queue.py --all-settings ../eval_output

     By default the CLI writes to a SEPARATE folder (../human_review_output/)
     so the official baseline eval_output/ stays pristine. Use --in-place to
     write next to the source instead.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:  # allow both flat-module use and package use
    from selective_intervention_policy import (
        should_request_human_review,
        POLICY_VERSION,
    )
except ImportError:  # pragma: no cover - fallback when imported as a package
    from .selective_intervention_policy import (  # type: ignore
        should_request_human_review,
        POLICY_VERSION,
    )

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.2.0"
SOURCE_SYSTEM = "VEGO-AI"
PIPELINE_STAGE = "agent4_classify_variability"
QUEUE_FILENAME = "human_review_queue.jsonl"
DEFAULT_OUT_DIRNAME = "human_review_output"

# Stable fields hashed into review_signature. review_id (HRQ-<setting>-<pid>) is
# human-readable but depends on Agent 4's pattern ordering; review_signature is
# order-independent and lets a later feedback join detect that an item drifted
# (i.e. the same review_id now describes a different pattern).
SIGNATURE_FIELDS = [
    "source_setting",
    "pattern_description",
    "related_guideline_id",
    "affected_cases",
    "classification",
]

# setting_id → (domain, diagram_type) fallback when not present in the JSON
_DOMAIN_BY_CODE = {"ch": "cheers", "pw": "parkwise"}
_DIAGRAM_BY_CODE = {"ucd": "UCD", "cd": "CD"}

_GUIDELINE_RE = re.compile(r"\b(G\d+)\b")
_PERCENT_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*%")


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def source_commit() -> str:
    """Best-effort short git commit of the code that generated the item."""
    try:
        repo = Path(__file__).resolve().parents[1]
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo), capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:  # noqa: BLE001 - provenance must never break generation
        pass
    return "unknown"


def derive_domain_and_diagram(setting_id: str) -> tuple[str, str]:
    """Map a setting_id like 'ucd_ch' → ('cheers', 'UCD'). Best-effort."""
    parts = setting_id.split("_")
    diagram = _DIAGRAM_BY_CODE.get(parts[0].lower(), "") if parts else ""
    domain = _DOMAIN_BY_CODE.get(parts[1].lower(), "") if len(parts) > 1 else ""
    return domain, diagram


# ---------------------------------------------------------------------------
# Pattern indexing / normalisation
# ---------------------------------------------------------------------------

def strength_object(value) -> dict:
    """
    Normalise pattern_strength into {"value": float|None, "display": str|None}.

    Accepts the v1.0/1.1 string form ('22.5%') and the v1.2 object form
    ({"count": int, "total": int, "percentage": "XX.X%"}).
    """
    display: str | None = None
    num: float | None = None
    if isinstance(value, str):
        display = value
        m = _PERCENT_RE.search(value)
        if m:
            num = round(float(m.group(1)) / 100.0, 4)
    elif isinstance(value, dict):
        display = value.get("percentage")
        count, total = value.get("count"), value.get("total")
        if isinstance(count, (int, float)) and isinstance(total, (int, float)) and total:
            num = round(count / total, 4)
        elif display:
            m = _PERCENT_RE.search(str(display))
            if m:
                num = round(float(m.group(1)) / 100.0, 4)
    return {"value": num, "display": display}


def index_patterns(deviation_patterns: dict) -> dict[str, dict]:
    """
    Build pattern_id → {kind, guideline_id, description, affected_cases, strength_raw}.

    Handles recurring_guideline_patterns (kind='guideline') and
    recurring_fragment_patterns (kind='fragment').
    """
    index: dict[str, dict] = {}
    for kind, key in (("guideline", "recurring_guideline_patterns"),
                      ("fragment", "recurring_fragment_patterns")):
        for p in deviation_patterns.get(key, []) or []:
            pid = p.get("pattern_id")
            if not pid:
                continue
            index[pid] = {
                "kind": kind,
                "guideline_id": p.get("guideline_id"),  # usually absent on fragments
                "description": p.get("description", ""),
                "affected_cases": p.get("affected_cases", []) or [],
                "strength_raw": p.get("pattern_strength"),
            }
    return index


def resolve_guideline(pattern: dict, evidence: str | None) -> dict:
    """
    Resolve the related guideline id transparently.

    Returns {"related_guideline_id", "related_guideline_resolution"} where the
    resolution records how the id was found, a confidence, and all candidates.
    """
    from_pattern = pattern.get("guideline_id")
    if from_pattern:
        return {
            "related_guideline_id": from_pattern,
            "related_guideline_resolution": {
                "method": "from_pattern",
                "confidence": "high",
                "candidate_guidelines": [from_pattern],
            },
        }
    candidates = _GUIDELINE_RE.findall(evidence or "")
    if candidates:
        return {
            "related_guideline_id": candidates[0],
            "related_guideline_resolution": {
                "method": "parsed_from_evidence",
                "confidence": "medium",
                "candidate_guidelines": candidates,
            },
        }
    return {
        "related_guideline_id": None,
        "related_guideline_resolution": {
            "method": "none",
            "confidence": None,
            "candidate_guidelines": [],
        },
    }


def review_signature(
    *,
    setting_id: str,
    pattern_description: str | None,
    related_guideline_id: str | None,
    affected_cases: list[str] | None,
    classification: str | None,
) -> str:
    """
    Deterministic, order-independent signature over the SIGNATURE_FIELDS.

    affected_cases are sorted and de-duplicated so that re-ordering or duplicate
    case ids (both occur in the committed Agent 4 outputs) do not change the
    signature. Returns a 16-hex-char (64-bit) sha256 prefix.
    """
    canonical = {
        "source_setting": setting_id,
        "pattern_description": (pattern_description or "").strip(),
        "related_guideline_id": related_guideline_id,
        "affected_cases": sorted(set(affected_cases or [])),
        "classification": classification or "",
    }
    blob = json.dumps(
        canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


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
    Produce schema-valid review items for classifications that need human review.

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
    domain_default, diagram = derive_domain_and_diagram(setting_id)
    domain = variability_classes.get("domain_identifier") or domain_default
    created_at = datetime.now(timezone.utc).isoformat()
    provenance = {
        "source_system": SOURCE_SYSTEM,
        "policy_version": POLICY_VERSION,
        "source_commit": source_commit(),
        "source_setting": setting_id,
        "policy_config": {"include_medium": include_medium},
    }

    items: list[dict] = []
    for entry in variability_classes.get("variability_classifications", []) or []:
        needs_review, reasons = should_request_human_review(
            entry, include_medium=include_medium
        )
        if not needs_review:
            continue

        pid = entry.get("pattern_id", "")
        pattern = pattern_index.get(pid, {})
        guideline = resolve_guideline(pattern, entry.get("evidence"))
        signature = review_signature(
            setting_id=setting_id,
            pattern_description=pattern.get("description", ""),
            related_guideline_id=guideline["related_guideline_id"],
            affected_cases=pattern.get("affected_cases", []),
            classification=entry.get("classification", ""),
        )

        items.append(
            {
                "review_id": f"HRQ-{setting_id}-{pid}",
                "review_signature": signature,
                "signature_fields": SIGNATURE_FIELDS,
                "schema_version": SCHEMA_VERSION,
                "created_at": created_at,
                "provenance": provenance,
                "setting_id": setting_id,
                "domain": domain,
                "diagram_type": diagram,
                "pipeline_stage": PIPELINE_STAGE,
                "pattern_id": pid,
                "source_pattern_id": pid,
                "pattern_kind": pattern.get("kind", "unknown"),
                "target_fragment": pattern.get("description", ""),
                "related_guideline_id": guideline["related_guideline_id"],
                "related_guideline_resolution": guideline["related_guideline_resolution"],
                "affected_cases": pattern.get("affected_cases", []),
                "pattern_strength": strength_object(pattern.get("strength_raw")),
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


def write_queue(items: list[dict], path: Path) -> int:
    """
    Write items as JSONL (one object per line), deduplicated by review_id.

    Deterministic rebuild: the file is overwritten from the current items, so
    re-running on the same outputs yields the same queue (idempotent — no
    accumulation, no duplicates). Returns the number of items written.
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
    return len(seen)


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


def _run_for_eval_dir(
    eval_dir: Path,
    include_medium: bool,
    out_dir: Path,
    in_place: bool,
) -> int:
    """Read agentD_*.json from one eval_output/<setting> dir and write the queue."""
    setting_id = eval_dir.name
    vc_path = _first_match(eval_dir, "agentD_variability_classes")
    dp_path = _first_match(eval_dir, "agentD_deviation_patterns")
    if vc_path is None:
        logger.warning("Skip %s - no agentD_variability_classes*.json", setting_id)
        return 0
    variability_classes = _load_json(vc_path)
    deviation_patterns = _load_json(dp_path) if dp_path else {}
    items = build_review_items(
        variability_classes, deviation_patterns, setting_id,
        include_medium=include_medium,
    )
    target_dir = eval_dir if in_place else (out_dir / setting_id)
    write_queue(items, target_dir / QUEUE_FILENAME)
    print(f"{setting_id}: {len(items)} review item(s) -> "
          f"{target_dir / QUEUE_FILENAME}")
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
                       help="An eval_output root; processes every subdirectory.")
    parser.add_argument("--out-dir", metavar="DIR", default=None,
                        help="Where to write queues (default: ../human_review_output "
                             "next to the repo root). Ignored with --in-place.")
    parser.add_argument("--in-place", action="store_true",
                        help="Write the queue next to the source agentD files "
                             "(into eval_output/<setting>) instead of --out-dir.")
    parser.add_argument("--no-include-medium", action="store_true",
                        help="Strict policy: escalate only Low / Undetermined / "
                             "guideline-update / explicit human-review cases.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    include_medium = not args.no_include_medium

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir) if args.out_dir else (repo_root / DEFAULT_OUT_DIRNAME)

    total = 0
    if args.from_eval_output:
        total = _run_for_eval_dir(
            Path(args.from_eval_output), include_medium, out_dir, args.in_place
        )
    else:
        root = Path(args.all_settings)
        for sub in sorted(p for p in root.iterdir() if p.is_dir()):
            total += _run_for_eval_dir(sub, include_medium, out_dir, args.in_place)

    policy = "broad (include_medium)" if include_medium else "strict"
    print(f"\nPolicy: {policy}   Total review items: {total}")


if __name__ == "__main__":
    main()
