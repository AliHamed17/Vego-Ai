"""
memory_advisor.py — Human Judgment Memory Advisory Layer (Milestone 4A).

Pure Python, no LLM call, no embeddings.

For each Agent 4 variability pattern, this retrieves relevant prior human
judgments from Human Judgment Memory (M3) and emits an **advisory** report. It is
the bridge between *stored* human judgment and *future* AI-assisted assessment —
but it is strictly advisory:

    ** M4A NEVER changes an AI classification. **
    Every advice item carries advice_mode="advisory_only" and
    ai_classification_changed=false. The original Agent 4 classification is copied
    in for later comparison (M4B) but never modified. There is no Agent 4 call,
    no reclassification, and no guideline change here.

Inputs (read-only):
    agentD_deviation_patterns.json    (Agent 4 skill 4-1)
    agentD_variability_classes.json   (Agent 4 skill 4-2)
    human_judgment_memory.jsonl       (Milestone 3)

Output:
    memory_advice.json

CLI (no API key):
    python memory_advisor.py \
        --patterns ../eval_output/ucd_ch/agentD_deviation_patterns.json \
        --classes  ../eval_output/ucd_ch/agentD_variability_classes.json \
        --memory   ../human_review_output/ucd_ch/human_judgment_memory.jsonl \
        --out      ../human_review_output/ucd_ch/memory_advice.json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

try:  # reuse M3 retrieval and M1 helpers
    from human_judgment_memory import load_memory, search_memory
    from human_review_queue import derive_domain_and_diagram
except Exception:  # pragma: no cover
    from .human_judgment_memory import load_memory, search_memory  # type: ignore
    from .human_review_queue import derive_domain_and_diagram      # type: ignore

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
ADVICE_MODE = "advisory_only"
ADVICE_FILENAME = "memory_advice.json"
RECOMMENDED_USE = "Use as advisory evidence only. Do not change classification until M4B."

_GUIDELINE_RE = re.compile(r"\b(G\d+)\b")
_QUOTED_RE = re.compile(r"'([^']+)'")
_CAP_RE = re.compile(r"\b([A-Z][A-Za-z]{3,})\b")
_STOP = {"the", "this", "that", "these", "those", "each", "with", "from",
         "their", "there", "when", "will", "into", "have", "they", "system"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_memory_or_empty(path: str | Path) -> list[dict]:
    """Load Human Judgment Memory, or continue with no matches if M3 has not run yet."""
    try:
        return load_memory(path)
    except FileNotFoundError:
        logger.warning("Human Judgment Memory file not found: %s; continuing with empty memory.", path)
        return []


def _index_patterns(deviation_patterns: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for key in ("recurring_guideline_patterns", "recurring_fragment_patterns"):
        for p in deviation_patterns.get(key, []) or []:
            if p.get("pattern_id"):
                index[p["pattern_id"]] = p
    return index


def _related_guideline(class_entry: dict, pattern: dict) -> str | None:
    gid = pattern.get("guideline_id")
    if gid:
        return gid
    m = _GUIDELINE_RE.search(class_entry.get("evidence") or "")
    return m.group(1) if m else None


def _keywords_from(text: str | None) -> list[str]:
    """Deterministic keyword extraction: quoted phrases + notable capitalized words."""
    out: list[str] = []
    seen: set[str] = set()
    for k in _QUOTED_RE.findall(text or "") + _CAP_RE.findall(text or ""):
        kl = k.lower()
        if kl in _STOP or kl in seen:
            continue
        seen.add(kl)
        out.append(k)
    return out


def _is_relevant(match: dict) -> bool:
    """A match is relevant only if it shares the guideline or a keyword (domain/diagram alone is too broad)."""
    return any(r.startswith("same related guideline") or r.startswith("keyword match:")
               for r in match.get("match_reasons", []))


def _advice_strength(relevant: list[dict]) -> str:
    if not relevant:
        return "none"
    if any(m.get("match_warning") for m in relevant):
        return "conflicting"
    top = max(m["match_score"] for m in relevant)
    if top >= 4:
        return "strong"
    if top == 3:
        return "moderate"
    return "weak"


def _advice_summary(strength: str, relevant: list[dict], gid: str | None) -> str:
    if strength == "none":
        return "No relevant prior human judgment found for this pattern."
    if strength == "conflicting":
        pairs = ", ".join(f"{m['memory_id']}={m.get('human_classification')}" for m in relevant)
        return f"Relevant human judgments disagree and require adjudication ({pairs})."
    top = relevant[0]
    hc = top.get("human_classification") or "unspecified"
    dt = (top.get("human_decision") or {}).get("decision_type") or top.get("decision_type")
    return (f"Relevant human judgment ({dt}) classified a similar fragment as "
            f"{hc} for guideline {gid or 'N/A'}. Advisory only.")


def _format_match(m: dict) -> dict:
    hd = m.get("human_decision") or {}
    rs = m.get("reuse_scope") or {}
    return {
        "memory_id": m.get("memory_id"),
        "memory_signature": m.get("memory_signature"),
        "match_score": m.get("match_score", 0),
        "match_reasons": m.get("match_reasons", []),
        "match_warning": m.get("match_warning"),
        "human_decision": {
            "decision_type": hd.get("decision_type"),
            "classification": m.get("human_classification"),
            "rationale": hd.get("rationale") or m.get("rationale"),
        },
        "reuse_scope": {"domain": rs.get("domain"), "diagram_type": rs.get("diagram_type")},
    }


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def build_advice_items(
    variability_classes: dict,
    deviation_patterns: dict,
    memory: list[dict],
    setting_id: str,
    *,
    provenance: dict | None = None,
) -> list[dict]:
    """
    Produce one advisory item per Agent 4 variability pattern. Read-only; never
    alters any classification.
    """
    pattern_index = _index_patterns(deviation_patterns or {})
    domain_default, diagram = derive_domain_and_diagram(setting_id)
    domain = variability_classes.get("domain_identifier") or domain_default
    prov = provenance or {"source_memory_file": "unknown",
                          "source_agent4_files": {"deviation_patterns": None,
                                                  "variability_classes": None}}

    items: list[dict] = []
    for entry in variability_classes.get("variability_classifications", []) or []:
        pid = entry.get("pattern_id", "")
        pattern = pattern_index.get(pid, {})
        gid = _related_guideline(entry, pattern)
        keywords = _keywords_from(pattern.get("description") or entry.get("justification"))

        matches = search_memory(
            memory, domain=domain, diagram_type=diagram,
            related_guideline_id=gid, keywords=keywords, include_conflicts=True,
        )
        relevant = [m for m in matches if _is_relevant(m)]
        strength = _advice_strength(relevant)
        has_conflict = any(m.get("match_warning") for m in relevant)

        items.append({
            "schema_version": SCHEMA_VERSION,
            "advice_id": f"MADV-{setting_id}-{pid}",
            "setting_id": setting_id,
            "pattern_id": pid,
            "advice_mode": ADVICE_MODE,
            "ai_classification_changed": False,
            "original_ai_classification": {
                "classification": entry.get("classification"),
                "confidence": entry.get("confidence"),
                "requires_human_review": entry.get("requires_human_review"),
                "flag_for_guidelines_update": entry.get("flag_for_guidelines_update"),
            },
            "query": {
                "domain": domain,
                "diagram_type": diagram,
                "related_guideline_id": gid,
                "keywords": keywords,
            },
            "advice_strength": strength,
            "advice_summary": _advice_summary(strength, relevant, gid),
            "memory_matches": [_format_match(m) for m in relevant],
            "has_conflicting_memory": has_conflict,
            "conflict_note": ("Relevant human judgments disagree and require adjudication."
                              if has_conflict else None),
            "recommended_use": RECOMMENDED_USE,
            "provenance": prov,
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
        "advice_mode": ADVICE_MODE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": provenance,
        "advice": items,
    }
    return apply_stage_architecture(
        "advice",
        report,
        architecture_mode=architecture_mode,
        architecture_manifest=architecture_manifest,
    ).output


def write_advice(report: dict, path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    n = len(report.get("advice", []))
    logger.info("Memory advice -> %s (%d item(s))", path, n)
    return n


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate an advisory-only Memory Advice report (no API key, no AI change)."
    )
    parser.add_argument("--patterns", required=True, help="agentD_deviation_patterns.json")
    parser.add_argument("--classes", required=True, help="agentD_variability_classes.json")
    parser.add_argument("--memory", required=True, help="human_judgment_memory.jsonl")
    parser.add_argument("--out", required=True, help="output memory_advice.json")
    parser.add_argument("--setting", default=None, help="setting_id (default: derived from --out dir)")
    add_architecture_arguments(parser)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    setting_id = args.setting or Path(args.out).resolve().parent.name
    deviation_patterns = load_json(args.patterns)
    variability_classes = load_json(args.classes)
    memory = load_memory_or_empty(args.memory)

    provenance = {
        "source_memory_file": str(args.memory),
        "source_agent4_files": {
            "deviation_patterns": str(args.patterns),
            "variability_classes": str(args.classes),
        },
    }
    items = build_advice_items(variability_classes, deviation_patterns, memory,
                               setting_id, provenance=provenance)
    report = generate_report(
        items,
        setting_id,
        provenance,
    )
    execution = publish_stage_output(
        "advice",
        report,
        output_path=args.out,
        writer=write_advice,
        architecture_mode=args.architecture_mode,
        architecture_manifest=args.architecture_manifest,
    )
    report = execution.output

    by_strength: dict[str, int] = {}
    for it in items:
        by_strength[it["advice_strength"]] = by_strength.get(it["advice_strength"], 0) + 1
    changed = sum(1 for it in items if it["ai_classification_changed"])
    print("\n=== Memory advice summary ===")
    print(f"patterns        : {len(items)}")
    print(f"advice_strength : {by_strength}")
    print(f"ai_classification_changed (must be 0): {changed}")
    for it in items:
        if it["memory_matches"]:
            warn = "  [conflict]" if it["has_conflicting_memory"] else ""
            print(f"    {it['pattern_id']:>3}  {it['advice_strength']:<11}"
                  f" matches={len(it['memory_matches'])}{warn}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
