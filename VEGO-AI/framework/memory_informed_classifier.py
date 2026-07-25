"""
memory_informed_classifier.py — Milestone 4B-1 (deterministic, experimental).

Pure Python. NO LLM, NO API key, NO embeddings, NO Agent 4 call.

For each Agent 4 variability pattern, this produces a **parallel** memory-informed
classification next to the original, using only a transparent deterministic policy
over Memory Advice (M4A) + Human Judgment Memory (M3).

    ** M4B-1 NEVER modifies the baseline. **
    - Baseline `agentD_variability_classes.json` / `eval_output` are read-only.
    - Output is a separate `memory_informed_comparison.json`.
    - Every record carries mode="experimental" and ai_behavior_changed_in_baseline=false.
    - The original Agent 4 classification is copied verbatim and never changed.
    - The memory-informed result only DIFFERS from the original in the single
      "strong disagreement" case, and even then it is a *parallel proposal*, flagged
      for human review — never written back into the baseline.

Deterministic policy table (advice_strength x agreement, plus decision-type cases):
    no memory / weak                      -> keep original
    moderate, agrees                      -> keep original (+support)
    moderate, disagrees                   -> keep original, REQUIRE human review
    strong, agrees                        -> keep original (+stronger support)
    strong, disagrees                     -> PROPOSE memory-supported alternative (parallel), REQUIRE review
    conflicting advice                    -> keep original, REQUIRE human review
    ambiguous human decision              -> keep original, REQUIRE human review
    guideline-update memory (no class)    -> keep original, flag guideline review

Inputs (read-only):
    agentD_variability_classes.json   (Agent 4 skill 4-2 — authoritative original)
    memory_advice.json                (M4A — advice_strength + memory matches)
    human_judgment_memory.jsonl       (M3 — for provenance / leakage status)
Output:
    memory_informed_comparison.json

CLI (no API key):
    python memory_informed_classifier.py \
        --classes ../eval_output/ucd_ch/agentD_variability_classes.json \
        --advice  ../human_review_output/ucd_ch/memory_advice.json \
        --memory  ../human_review_output/ucd_ch/human_judgment_memory.jsonl \
        --out     ../human_review_output/ucd_ch/memory_informed_comparison.json
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

try:
    from hlayer_architecture import (
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
    )
except ImportError:  # pragma: no cover - package import fallback
    from .hlayer_architecture import (  # type: ignore
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
    )

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0.0"
POLICY_VERSION = "memory-informed-classifier-v1"
MODE = "experimental"
CHANGED_MEANING = (
    "The parallel memory-informed classification differs from the original Agent 4 "
    "classification; the baseline Agent 4 output was NOT modified."
)

# decision types that always escalate to a human regardless of strength
_AMBIGUOUS = "ambiguous"
_GUIDELINE_UPDATE = "needs_guideline_update"


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_memory(path: str | Path) -> list[dict]:
    items: list[dict] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    except FileNotFoundError:
        logger.warning("Memory file not found: %s; leakage status will be 'unknown'.", path)
    return items


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _index_advice(memory_advice: dict) -> dict[str, dict]:
    return {a.get("pattern_id"): a for a in memory_advice.get("advice", []) or []
            if a.get("pattern_id")}


def _index_memory(memory: list[dict]) -> dict[str, dict]:
    return {m.get("memory_id"): m for m in memory or [] if m.get("memory_id")}


def _evaluation_leakage_status(used_ids: list[str], memory_index: dict[str, dict],
                               setting_id: str, pattern_id: str) -> str:
    if not used_ids:
        return "none"
    saw_same_setting = saw_cross = saw_known = False
    for mid in used_ids:
        mem = memory_index.get(mid)
        if not mem:
            continue
        prov = mem.get("provenance") or {}
        s, p = prov.get("source_setting"), prov.get("source_pattern_id")
        if s is None:
            continue
        saw_known = True
        if s == setting_id and p == pattern_id:
            return "same_pattern_memory_used"
        if s == setting_id:
            saw_same_setting = True
        else:
            saw_cross = True
    if saw_same_setting:
        return "same_setting_memory_used"
    if saw_cross:
        return "cross_setting_memory_used"
    return "unknown"


def _decide(strength: str, matches: list[dict], original_class: str | None,
            has_conflict: bool) -> dict:
    """
    Apply the deterministic policy. Returns dict with rule, memory_informed
    classification source/class, differs, requires_review, human_class.
    """
    human_classes = [(m.get("human_decision") or {}).get("classification")
                     for m in matches]
    human_classes = [c for c in human_classes if c]
    distinct = set(human_classes)
    top = matches[0] if matches else {}
    top_decision = (top.get("human_decision") or {}).get("decision_type")
    human_class = next(iter(distinct)) if len(distinct) == 1 else None

    keep = {"source": "original_agent4", "class": original_class,
            "differs": False, "human_class": human_class}

    if not matches or strength == "none":
        return {**keep, "rule": "no_memory_keep_original", "requires_review": False}
    if strength == "conflicting" or has_conflict or len(distinct) > 1:
        return {**keep, "rule": "conflicting_keep_original_require_review",
                "requires_review": True}
    if top_decision == _AMBIGUOUS:
        return {**keep, "rule": "ambiguous_keep_original_require_review",
                "requires_review": True}
    if top_decision == _GUIDELINE_UPDATE and human_class is None:
        return {**keep, "rule": "guideline_update_keep_original_flag_review",
                "requires_review": True}
    if human_class is None:
        return {**keep, "rule": "no_explicit_human_class_keep_original",
                "requires_review": True}

    agree = (human_class == original_class)
    if strength == "weak":
        return {**keep, "rule": "weak_keep_original", "requires_review": False}
    if strength == "moderate":
        if agree:
            return {**keep, "rule": "moderate_agreement_keep_original",
                    "requires_review": False}
        return {**keep, "rule": "moderate_disagreement_keep_original_require_review",
                "requires_review": True}
    if strength == "strong":
        if agree:
            return {**keep, "rule": "strong_agreement_keep_original",
                    "requires_review": False}
        # the only case that produces a parallel alternative
        return {"source": "human_memory", "class": human_class, "differs": True,
                "human_class": human_class,
                "rule": "strong_disagreement_propose_memory_supported_alternative",
                "requires_review": True}
    return {**keep, "rule": "unknown_strength_keep_original", "requires_review": True}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def build_comparison_items(variability_classes: dict, memory_advice: dict,
                           memory: list[dict], setting_id: str) -> list[dict]:
    """Produce one parallel, experimental comparison item per Agent 4 pattern."""
    advice_index = _index_advice(memory_advice or {})
    memory_index = _index_memory(memory or [])

    items: list[dict] = []
    for entry in variability_classes.get("variability_classifications", []) or []:
        pid = entry.get("pattern_id", "")
        original = {
            "classification": entry.get("classification"),
            "confidence": entry.get("confidence"),
            "requires_human_review": entry.get("requires_human_review"),
            "flag_for_guidelines_update": entry.get("flag_for_guidelines_update"),
        }
        advice = advice_index.get(pid, {})
        strength = advice.get("advice_strength", "none")
        matches = advice.get("memory_matches", []) or []
        has_conflict = bool(advice.get("has_conflicting_memory", False))
        used_ids = [m.get("memory_id") for m in matches if m.get("memory_id")]

        d = _decide(strength, matches, original["classification"], has_conflict)

        # confidence of a proposed alternative comes from the memory item (if known)
        mic_conf = None
        if d["source"] == "human_memory" and used_ids:
            mem = memory_index.get(used_ids[0]) or {}
            mic_conf = mem.get("confidence")
        memory_informed = {
            "classification": d["class"] if d["source"] == "human_memory" else original["classification"],
            "confidence": mic_conf if d["source"] == "human_memory" else original["confidence"],
            "source": d["source"],
        }

        leakage = _evaluation_leakage_status(used_ids, memory_index, setting_id, pid)
        decision_trace = [
            f"advice_strength={strength}",
            f"original_classification={original['classification']}",
            f"human_memory_classification={d['human_class'] or 'none'}",
            f"rule={d['rule']}",
            f"evaluation_leakage_status={leakage}",
            "baseline_output_not_modified",
        ]

        items.append({
            "comparison_id": f"MINF-{setting_id}-{pid}",
            "setting_id": setting_id,
            "pattern_id": pid,
            "mode": MODE,
            "policy_version": POLICY_VERSION,
            "ai_behavior_changed_in_baseline": False,
            "original_agent4_classification": original,
            "memory_advice": {
                "advice_strength": strength,
                "advice_summary": advice.get("advice_summary"),
                "memory_match_ids": used_ids,
                "has_conflicting_memory": has_conflict,
            },
            "memory_informed_classification": memory_informed,
            "memory_informed_differs_from_original": bool(d["differs"]),
            "classification_changed_meaning": CHANGED_MEANING,
            "requires_human_review_after_memory": bool(d["requires_review"]),
            "human_memory_used": used_ids,
            "evaluation_leakage_status": leakage,
            "rule_applied": d["rule"],
            "decision_trace": decision_trace,
        })
    return items


def generate_report(
    items: list[dict],
    setting_id: str,
    provenance: dict,
    *,
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> dict:
    report = {
        "schema_version": SCHEMA_VERSION,
        "setting_id": setting_id,
        "mode": MODE,
        "policy_version": POLICY_VERSION,
        "ai_behavior_changed_in_baseline": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": provenance,
        "comparisons": items,
    }
    return apply_stage_architecture(
        "comparison",
        report,
        architecture_mode=architecture_mode,
        architecture_manifest=architecture_manifest,
    ).output


def write_report(report: dict, path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    n = len(report.get("comparisons", []))
    logger.info("Memory-informed comparison -> %s (%d item(s))", path, n)
    return n


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic memory-informed comparison (M4B-1; experimental; no API key)."
    )
    parser.add_argument("--classes", required=True, help="agentD_variability_classes.json")
    parser.add_argument("--advice", required=True, help="memory_advice.json (M4A)")
    parser.add_argument("--memory", required=True, help="human_judgment_memory.jsonl (M3)")
    parser.add_argument("--out", required=True, help="output memory_informed_comparison.json")
    parser.add_argument("--setting", default=None, help="setting_id (default: from --out dir)")
    add_architecture_arguments(parser)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    setting_id = args.setting or Path(args.out).resolve().parent.name

    variability_classes = load_json(args.classes)
    memory_advice = load_json(args.advice)
    memory = load_memory(args.memory)

    provenance = {
        "source_variability_classes": str(args.classes),
        "source_memory_advice": str(args.advice),
        "source_memory": str(args.memory),
    }
    items = build_comparison_items(variability_classes, memory_advice, memory, setting_id)
    report = generate_report(
        items,
        setting_id,
        provenance,
    )
    execution = publish_stage_output(
        "comparison",
        report,
        output_path=args.out,
        writer=write_report,
        architecture_mode=args.architecture_mode,
        architecture_manifest=args.architecture_manifest,
    )
    report = execution.output

    by_rule: dict[str, int] = {}
    differs = sum(1 for it in items if it["memory_informed_differs_from_original"])
    review = sum(1 for it in items if it["requires_human_review_after_memory"])
    changed_baseline = sum(1 for it in items if it["ai_behavior_changed_in_baseline"])
    for it in items:
        by_rule[it["rule_applied"]] = by_rule.get(it["rule_applied"], 0) + 1
    print("\n=== Memory-informed comparison (experimental) ===")
    print(f"patterns                              : {len(items)}")
    print(f"memory_informed_differs_from_original : {differs}")
    print(f"requires_human_review_after_memory    : {review}")
    print(f"ai_behavior_changed_in_baseline (must be 0): {changed_baseline}")
    print(f"rules                                 : {by_rule}")
    for it in items:
        if it["human_memory_used"]:
            flag = " [DIFFERS]" if it["memory_informed_differs_from_original"] else ""
            print(f"    {it['pattern_id']:>3}  {it['rule_applied']}"
                  f"  leakage={it['evaluation_leakage_status']}{flag}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
