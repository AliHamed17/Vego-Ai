"""
human_judgment_memory.py — store and retrieve reusable human judgments.

Milestone 3 of the Human-AI Co-Reasoning extension. Pure Python, no LLM call.

This milestone turns one-off human feedback (Milestone 2) into **reusable**
judgment: it ingests a resolved Human Review Queue, keeps only the judgments a
human marked reusable, and lets later code retrieve relevant prior judgments by
**simple, explainable** matching.

Scope guard (M3): NO AI behavior change, NO Agent 4 wiring, NO embeddings, NO
visualizer changes. Memory is only built and searched here; consuming it to
change an AI decision is a later milestone.

Flow
----
    human_review_queue_resolved.jsonl  (M2)
            |
            v  ingest_judgments  (only resolved + reusable + rationale)
            v
    human_judgment_memory.jsonl
            |
            v  search_memory(domain, diagram_type, related_guideline_id, keywords)
            v
    ranked matches, each with explainable match_reasons

Ingestion guardrails
--------------------
  * keep only items with status == "resolved" (skip "signature_mismatch",
    "pending", "dismissed" — reported, not errors);
  * require human_feedback.reusable == true  (else: skipped_non_reusable);
  * require a non-empty rationale            (else: missing_rationale);
  * preserve full provenance (source ids, setting, schema versions, commit);
  * give each judgment a deterministic memory_signature.

CLI (no API key)
----------------
    python human_judgment_memory.py --resolved <resolved.jsonl> --out <memory.jsonl>
    python human_judgment_memory.py --memory <memory.jsonl> \
        --query-domain cheers --query-diagram UCD --query-guideline G12 \
        --keywords "Marketing Department"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

try:  # reuse the git-commit helper from M1
    from human_review_queue import source_commit
except Exception:  # pragma: no cover - fallback if import path differs
    def source_commit() -> str:  # type: ignore
        return "unknown"

try:
    from hlayer_architecture import (
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
        require_cli_parity_success,
    )
except ImportError:  # pragma: no cover - package import fallback
    from .hlayer_architecture import (  # type: ignore
        add_architecture_arguments,
        apply_stage_architecture,
        publish_stage_output,
        require_cli_parity_success,
    )

logger = logging.getLogger(__name__)

JUDGMENT_SCHEMA_VERSION = "1.0.0"
REVIEW_ITEM_SCHEMA_VERSION = "1.2.0"   # default if a review item omits schema_version
FEEDBACK_SCHEMA_VERSION = "1.0.0"
SOURCE_SYSTEM = "VEGO-AI"
MEMORY_FILENAME = "human_judgment_memory.jsonl"

SIGNATURE_FIELDS = [
    "source_review_signature",
    "source_feedback_id",
    "decision_type",
    "human_classification",
    "related_guideline_id",
    "reuse_scope",
    "guideline_update.action",
]


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def _load_jsonl(path: str | Path) -> list[dict]:
    items: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_resolved_queue(path: str | Path) -> list[dict]:
    """Load a human_review_queue_resolved.jsonl (Milestone 2 output)."""
    return _load_jsonl(path)


def load_memory(path: str | Path) -> list[dict]:
    """Load a human_judgment_memory.jsonl."""
    return _load_jsonl(path)


def write_memory(memory_items: list[dict], path: str | Path) -> int:
    """
    Write memory as JSONL, deduplicated by memory_id (deterministic rebuild).
    Returns the number of items written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    with open(path, "w", encoding="utf-8") as fh:
        for item in memory_items:
            mid = item.get("memory_id")
            if mid in seen:
                continue
            seen.add(mid)
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info("Human judgment memory -> %s (%d item(s))", path, len(seen))
    return len(seen)


# ---------------------------------------------------------------------------
# Building memory items
# ---------------------------------------------------------------------------

def _memory_signature(*, review_signature, feedback_id, decision_type,
                      human_classification, related_guideline_id,
                      reuse_scope, guideline_update) -> str:
    canonical = {
        "source_review_signature": review_signature,
        "source_feedback_id": feedback_id,
        "decision_type": decision_type,
        "human_classification": human_classification,
        "related_guideline_id": related_guideline_id,
        "reuse_scope": reuse_scope or {},
        "guideline_update.action": (guideline_update or {}).get("action"),
    }
    blob = json.dumps(canonical, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def build_memory_item(resolved_item: dict) -> dict:
    """Build one memory item from a *resolved* review item (assumes it passed ingest filters)."""
    fb = resolved_item.get("human_feedback") or {}
    hd = fb.get("human_decision") or {}

    setting = resolved_item.get("setting_id", "")
    pid = resolved_item.get("pattern_id") or resolved_item.get("source_pattern_id", "")
    domain = resolved_item.get("domain", "")
    diagram_type = resolved_item.get("diagram_type", "")
    decision_type = hd.get("decision_type")
    human_classification = hd.get("corrected_classification")
    related_guideline_id = resolved_item.get("related_guideline_id")
    guideline_update = fb.get("guideline_update")

    reuse_scope = fb.get("reuse_scope") or {
        "domain": domain,
        "diagram_type": diagram_type,
        "applies_to_future_models": False,
        "limitations": "",
    }

    review_schema = resolved_item.get("schema_version", REVIEW_ITEM_SCHEMA_VERSION)
    sig = _memory_signature(
        review_signature=resolved_item.get("review_signature"),
        feedback_id=fb.get("feedback_id"),
        decision_type=decision_type,
        human_classification=human_classification,
        related_guideline_id=related_guideline_id,
        reuse_scope=reuse_scope,
        guideline_update=guideline_update,
    )

    return {
        "memory_id": f"HJM-{setting}-{pid}",
        "memory_signature": sig,
        "signature_fields": SIGNATURE_FIELDS,
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "conflict_status": "none",
        "source_review_id": resolved_item.get("review_id", ""),
        "source_review_signature": resolved_item.get("review_signature", ""),
        "source_feedback_id": fb.get("feedback_id", ""),
        "domain": domain,
        "diagram_type": diagram_type,
        "related_guideline_id": related_guideline_id,
        "target_fragment": resolved_item.get("target_fragment", ""),
        "decision_type": decision_type,
        "human_classification": human_classification,
        "confidence": hd.get("confidence", ""),
        "human_decision": hd,
        "rationale": hd.get("rationale", ""),
        "expert_id": fb.get("expert_id", ""),
        "reuse_scope": reuse_scope,
        "guideline_update": guideline_update,
        "provenance": {
            "source_system": SOURCE_SYSTEM,
            "source_setting": setting,
            "source_pattern_id": pid,
            "source_commit": source_commit(),
            "source_schema_versions": {
                "review_item_schema": review_schema,
                "feedback_schema": FEEDBACK_SCHEMA_VERSION,
                "judgment_schema": JUDGMENT_SCHEMA_VERSION,
            },
        },
    }


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def ingest_judgments(
    resolved_items: list[dict],
    *,
    architecture_mode: str = "legacy",
    architecture_manifest: str | Path | None = None,
) -> tuple[list[dict], dict]:
    """
    Build memory items from a resolved queue, applying the ingest guardrails.

    Returns (memory_items, report). Skipped items are reported with reasons,
    never raised as errors. After building, conflicts are detected and each
    memory item's conflict_status is annotated.
    """
    memory: list[dict] = []
    skipped: list[dict] = []

    for item in resolved_items:
        rid = item.get("review_id", "<no-id>")
        status = item.get("status")
        if status == "signature_mismatch":
            skipped.append({"review_id": rid, "reason": "signature_mismatch"})
            continue
        if status != "resolved":
            skipped.append({"review_id": rid, "reason": "not_resolved"})
            continue
        fb = item.get("human_feedback")
        if not fb:
            skipped.append({"review_id": rid, "reason": "no_feedback"})
            continue
        if fb.get("reusable") is not True:
            skipped.append({"review_id": rid, "reason": "skipped_non_reusable"})
            continue
        if not str((fb.get("human_decision") or {}).get("rationale") or "").strip():
            skipped.append({"review_id": rid, "reason": "missing_rationale"})
            continue
        memory.append(build_memory_item(item))

    detect_conflicts(memory)  # annotate conflict_status in place

    by_reason: dict[str, int] = {}
    for s in skipped:
        by_reason[s["reason"]] = by_reason.get(s["reason"], 0) + 1

    report = {
        "total_items": len(resolved_items),
        "ingested": len(memory),
        "skipped": skipped,
        "skipped_by_reason": by_reason,
        "conflicts": sum(1 for m in memory if m["conflict_status"] == "needs_adjudication"),
    }
    memory = apply_stage_architecture(
        "memory",
        memory,
        architecture_mode=architecture_mode,
        architecture_manifest=architecture_manifest,
    ).output
    return memory, report


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def detect_conflicts(memory_items: list[dict]) -> list[dict]:
    """
    Flag judgments that apply to the same (domain, diagram_type, related_guideline_id,
    target_fragment) but disagree on human_classification.

    Annotates each affected item in place (conflict_status="needs_adjudication" and
    conflicting_memory_ids). Returns the list of conflict groups.
    """
    groups: dict[tuple, list[dict]] = {}
    for m in memory_items:
        key = (
            (m.get("domain") or "").lower(),
            (m.get("diagram_type") or "").lower(),
            m.get("related_guideline_id"),
            (m.get("target_fragment") or "").strip().lower(),
        )
        groups.setdefault(key, []).append(m)

    conflicts: list[dict] = []
    for key, members in groups.items():
        classes = {m.get("human_classification") for m in members
                   if m.get("human_classification")}
        if len(members) > 1 and len(classes) > 1:
            ids = [m["memory_id"] for m in members]
            for m in members:
                m["conflict_status"] = "needs_adjudication"
                m["conflicting_memory_ids"] = [i for i in ids if i != m["memory_id"]]
            conflicts.append({
                "key": {"domain": key[0], "diagram_type": key[1],
                        "related_guideline_id": key[2], "target_fragment": key[3]},
                "memory_ids": ids,
                "classifications": sorted(classes),
            })
    return conflicts


# ---------------------------------------------------------------------------
# Retrieval (explainable; no embeddings)
# ---------------------------------------------------------------------------

def _as_keyword_list(keywords) -> list[str]:
    if not keywords:
        return []
    if isinstance(keywords, str):
        return [k.strip() for k in keywords.split(",") if k.strip()]
    return [str(k).strip() for k in keywords if str(k).strip()]


def search_memory(
    memory_items: list[dict],
    *,
    domain: str | None = None,
    diagram_type: str | None = None,
    related_guideline_id: str | None = None,
    keywords=None,
    include_conflicts: bool = False,
) -> list[dict]:
    """
    Return memory items matching the given facets, each annotated with an
    explainable `match_reasons` list and a `match_score`. No embeddings — only
    transparent facet + keyword matching.

    Conflicted judgments are still returned but carry
    `match_warning="conflicting_human_judgments"`; with include_conflicts=True the
    result also lists `conflicting_memory_ids`.
    """
    kw_list = _as_keyword_list(keywords)
    any_filter = any([domain, diagram_type, related_guideline_id, kw_list])
    results: list[dict] = []

    for m in memory_items:
        reasons: list[str] = []
        if domain and (m.get("domain") or "").lower() == domain.lower():
            reasons.append("same domain")
        if diagram_type and (m.get("diagram_type") or "").lower() == diagram_type.lower():
            reasons.append("same diagram type")
        if related_guideline_id and m.get("related_guideline_id") == related_guideline_id:
            reasons.append(f"same related guideline {related_guideline_id}")
        if kw_list:
            haystack = ((m.get("target_fragment") or "") + " " +
                        (m.get("rationale") or "")).lower()
            for kw in kw_list:
                if kw.lower() in haystack:
                    reasons.append(f"keyword match: {kw}")

        if any_filter and not reasons:
            continue

        result = dict(m)
        result["match_reasons"] = reasons
        result["match_score"] = len(reasons)
        if m.get("conflict_status") == "needs_adjudication":
            result["match_warning"] = "conflicting_human_judgments"
            if include_conflicts:
                result["conflicting_memory_ids"] = m.get("conflicting_memory_ids", [])
        results.append(result)

    results.sort(key=lambda r: (-r["match_score"], r.get("memory_id", "")))
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build/query the VEGO-AI Human Judgment Memory (no API key)."
    )
    parser.add_argument("--resolved", help="ingest mode: human_review_queue_resolved.jsonl")
    parser.add_argument("--out", help="ingest mode: output human_judgment_memory.jsonl")
    parser.add_argument("--memory", help="query mode: human_judgment_memory.jsonl")
    parser.add_argument("--query-domain", default=None)
    parser.add_argument("--query-diagram", default=None)
    parser.add_argument("--query-guideline", default=None)
    parser.add_argument("--keywords", default=None)
    parser.add_argument("--include-conflicts", action="store_true")
    add_architecture_arguments(parser)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    if args.resolved:
        if not args.out:
            parser.error("--resolved requires --out")
        resolved = load_resolved_queue(args.resolved)
        memory, report = ingest_judgments(
            resolved,
        )
        execution = publish_stage_output(
            "memory",
            memory,
            output_path=args.out,
            writer=write_memory,
            architecture_mode=args.architecture_mode,
            architecture_manifest=args.architecture_manifest,
        )
        require_cli_parity_success(execution)
        memory = execution.output
        print("\n=== Ingest summary ===")
        print(f"resolved items : {report['total_items']}")
        print(f"ingested       : {report['ingested']}")
        print(f"conflicts      : {report['conflicts']}")
        print(f"skipped        : {len(report['skipped'])}  {report['skipped_by_reason']}")
        for s in report["skipped"]:
            print(f"    - {s['review_id']}: {s['reason']}")
        print(f"-> {args.out}")
    elif args.memory:
        memory = load_memory(args.memory)
        hits = search_memory(
            memory,
            domain=args.query_domain,
            diagram_type=args.query_diagram,
            related_guideline_id=args.query_guideline,
            keywords=args.keywords,
            include_conflicts=args.include_conflicts,
        )
        print(f"\n=== Query results: {len(hits)} match(es) ===")
        for h in hits:
            warn = f"  [{h['match_warning']}]" if h.get("match_warning") else ""
            print(f"{h['memory_id']}  score={h['match_score']}{warn}")
            print(f"    classification: {h.get('human_classification')}")
            print(f"    reasons       : {h['match_reasons']}")
    else:
        parser.error("provide either --resolved/--out (ingest) or --memory (query)")


if __name__ == "__main__":
    main()
