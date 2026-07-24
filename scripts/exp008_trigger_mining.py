"""EXP-008: deterministic early-trigger mining from baseline guideline churn."""

from __future__ import annotations

import csv
import glob
import json
import math
import re
import sys
from pathlib import Path

from hlayer_harness import (
    REPO,
    exp005_gate_sentence,
    experiment_output_dir,
    load_exp005_gate,
    write_experiment_manifest,
    write_json,
)

EVAL = REPO / "VEGO-AI" / "eval_output"
RUN = REPO / "VEGO-AI" / "runs" / "20260614-122150" / "human"
OUT = experiment_output_dir("exp008")
SETTINGS = ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw")
UNIFORM_CAPS = (10, 20, 30, 35, 40)
CLAIM_BASE = "Mechanism/observability evidence for trigger calibration only."


def natural_key(value: str) -> tuple:
    parts = re.split(r"(\d+)", str(value))
    return tuple((0, int(part)) if part.isdigit() else (1, part.lower()) for part in parts)


def find_one(directory: Path, pattern: str) -> Path | None:
    hits = sorted(
        (Path(path) for path in glob.glob(str(directory / pattern))),
        key=lambda path: natural_key(path.name),
    )
    return hits[0] if hits else None


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def guideline_index(document: dict) -> dict[str, dict]:
    return {
        str(item.get("id")): {
            "name": item.get("guideline_name"),
            "description": item.get("description"),
            "certainty": item.get("mapping_certainty"),
        }
        for item in document.get("reference_guidelines", []) or []
    }


def rank_key(guideline_id: str, record: dict) -> tuple:
    return (
        -int(record["instability"]),
        -int(record["revisions"]),
        -int(record["added_late"]),
        -int(record["removed"]),
        natural_key(guideline_id),
    )


def mine_setting(setting: str) -> tuple[list[dict], dict, set[Path]]:
    setting_dir = EVAL / setting
    paths = [find_one(setting_dir, f"agentB_run{i}_guidelines*.json") for i in (1, 2, 3)]
    paths.append(find_one(setting_dir, "agentB_best_guidelines*.json"))
    source_paths = {path.resolve() for path in paths if path is not None}
    versions = [guideline_index(load_json(path)) for path in paths if path is not None]
    if not versions:
        raise RuntimeError(f"No guideline versions found for {setting}")

    churn: dict[str, dict] = {}
    for previous, current in zip(versions, versions[1:]):
        for guideline_id in sorted(set(current) - set(previous), key=natural_key):
            churn.setdefault(guideline_id, {"revisions": 0, "added_late": 0, "removed": 0})[
                "added_late"
            ] += 1
        for guideline_id in sorted(set(previous) - set(current), key=natural_key):
            churn.setdefault(guideline_id, {"revisions": 0, "added_late": 0, "removed": 0})[
                "removed"
            ] += 1
        for guideline_id in sorted(set(previous) & set(current), key=natural_key):
            if previous[guideline_id] != current[guideline_id]:
                churn.setdefault(guideline_id, {"revisions": 0, "added_late": 0, "removed": 0})[
                    "revisions"
                ] += 1

    final = versions[-1]
    for guideline_id in sorted(churn, key=natural_key):
        record = churn[guideline_id]
        info = final.get(guideline_id) or next(
            (version[guideline_id] for version in reversed(versions) if guideline_id in version), {}
        )
        record["name"] = info.get("name")
        record["final_certainty"] = info.get("certainty")
        record["instability"] = record["revisions"] + record["added_late"] + record["removed"]

    reviewed: set[str] = set()
    queue_path = RUN / setting / "human_review_queue.jsonl"
    if queue_path.is_file():
        source_paths.add(queue_path.resolve())
        with queue_path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                if item.get("related_guideline_id") is not None:
                    reviewed.add(str(item["related_guideline_id"]))

    unstable = {
        guideline_id: record for guideline_id, record in churn.items() if record["instability"] > 0
    }
    overlap = set(unstable).intersection(reviewed)
    never_reviewed = sorted(
        set(unstable) - reviewed,
        key=lambda guideline_id: rank_key(guideline_id, unstable[guideline_id]),
    )
    denominator = len(never_reviewed)
    threshold_sweep = {}
    for threshold in (1, 2, 3):
        surfaced = [
            guideline_id
            for guideline_id in never_reviewed
            if unstable[guideline_id]["instability"] >= threshold
        ]
        threshold_sweep[str(threshold)] = {
            "surfaced_never_reviewed": len(surfaced),
            "never_reviewed_denominator": denominator,
            "capture_share": round(len(surfaced) / denominator, 3) if denominator else 1.0,
            "added_review_transactions": len(surfaced),
            "added_load_items": len(surfaced),
        }

    rank_cap = {}
    for cap in UNIFORM_CAPS:
        selected = never_reviewed[:cap]
        rank_cap[str(cap)] = {
            "surfaced_never_reviewed": len(selected),
            "never_reviewed_denominator": denominator,
            "capture_share": round(len(selected) / denominator, 3) if denominator else 1.0,
            "added_review_transactions": len(selected),
            "added_load_items": len(selected),
        }
    adaptive_cap = min(40, max(30, math.ceil(0.8 * denominator))) if denominator else 30
    adaptive_selected = never_reviewed[:adaptive_cap]
    adaptive = {
        "candidate_cap": adaptive_cap,
        "selection_rule": "min(40, max(30, ceil(0.8 * never_reviewed)))",
        "status": "comparison parameter; not an approved default",
        "surfaced_never_reviewed": len(adaptive_selected),
        "never_reviewed_denominator": denominator,
        "capture_share": round(len(adaptive_selected) / denominator, 3) if denominator else 1.0,
        "added_review_transactions": len(adaptive_selected),
    }
    rows = [
        {
            "setting": setting,
            "guideline_id": guideline_id,
            **unstable[guideline_id],
            "reached_review_queue": int(guideline_id in reviewed),
        }
        for guideline_id in sorted(unstable, key=lambda value: rank_key(value, unstable[value]))
    ]
    summary = {
        "setting": setting,
        "guidelines_final": len(final),
        "unstable_guidelines": len(unstable),
        "instability_rate": round(len(unstable) / len(final), 3) if final else 0,
        "reviewed_guideline_ids": len(reviewed),
        "unstable_and_reviewed": len(overlap),
        "unstable_never_reviewed": denominator,
        "top_candidate_triggers": never_reviewed[:5],
        "ranking_tie_breakers": "instability, revisions, added_late, removed (descending), then natural guideline ID",
        "churn_trigger_sweep": threshold_sweep,
        "rank_and_cap_sweep": rank_cap,
        "adaptive_cap_comparison": adaptive,
    }
    return rows, summary, source_paths


def main() -> int:
    missing = [setting for setting in SETTINGS if not (EVAL / setting).is_dir()]
    if missing:
        print(f"EXP-008 missing setting directories: {missing}", file=sys.stderr)
        return 2
    gate = load_exp005_gate()
    claim = f"{CLAIM_BASE} {exp005_gate_sentence(gate)}"
    all_rows: list[dict] = []
    summaries: list[dict] = []
    inputs: set[Path] = set()
    try:
        for setting in SETTINGS:
            rows, summary, source_paths = mine_setting(setting)
            all_rows.extend(rows)
            summaries.append(summary)
            inputs.update(source_paths)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"EXP-008 input error: {exc}", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "unstable_guidelines.csv"
    if not all_rows:
        print("EXP-008 produced no unstable-guideline rows", file=sys.stderr)
        return 2
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)

    total_denominator = sum(item["unstable_never_reviewed"] for item in summaries)
    totals = {
        "unstable_guidelines": sum(item["unstable_guidelines"] for item in summaries),
        "unstable_and_reviewed": sum(item["unstable_and_reviewed"] for item in summaries),
        "unstable_never_reviewed": total_denominator,
        "churn_trigger_sweep": {},
        "rank_and_cap_sweep": {},
    }
    for threshold in ("1", "2", "3"):
        surfaced = sum(
            item["churn_trigger_sweep"][threshold]["surfaced_never_reviewed"] for item in summaries
        )
        totals["churn_trigger_sweep"][threshold] = {
            "surfaced_never_reviewed": surfaced,
            "never_reviewed_denominator": total_denominator,
            "capture_share": round(surfaced / total_denominator, 3) if total_denominator else 1.0,
            "max_added_load_per_setting": max(
                item["churn_trigger_sweep"][threshold]["added_review_transactions"]
                for item in summaries
            ),
        }
    for cap in map(str, UNIFORM_CAPS):
        surfaced = sum(
            item["rank_and_cap_sweep"][cap]["surfaced_never_reviewed"] for item in summaries
        )
        totals["rank_and_cap_sweep"][cap] = {
            "surfaced_never_reviewed": surfaced,
            "never_reviewed_denominator": total_denominator,
            "capture_share": round(surfaced / total_denominator, 3) if total_denominator else 1.0,
            "max_added_load_per_setting": max(
                item["rank_and_cap_sweep"][cap]["added_review_transactions"] for item in summaries
            ),
        }

    summary = {
        "experiment": "EXP-008 early-trigger mining",
        "claim_scope": claim,
        "uniform_caps": list(UNIFORM_CAPS),
        "settings": summaries,
        "totals": totals,
    }
    summary_path = OUT / "summary.json"
    write_json(summary_path, summary)
    lines = [
        "# EXP-008 Early-Trigger Mining - Summary",
        "",
        f"Claim scope: {claim}",
        "",
        "All capture shares use the fixed count of unstable, never-reviewed guidelines as their denominator.",
        "Uniform and adaptive caps are comparison parameters; no default is selected.",
        "",
        "| Setting | Final guidelines | Unstable | Unstable+reviewed | Unstable never reviewed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in summaries:
        lines.append(
            f"| {item['setting']} | {item['guidelines_final']} | {item['unstable_guidelines']} | "
            f"{item['unstable_and_reviewed']} | {item['unstable_never_reviewed']} |"
        )
    lines.extend(
        [
            f"| TOTAL | - | {totals['unstable_guidelines']} | {totals['unstable_and_reviewed']} | {total_denominator} |",
            "",
            "## Uniform cap sweep",
            "",
            "| K | Captured | Fixed denominator | Capture share | Max transactions/setting |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for cap in map(str, UNIFORM_CAPS):
        item = totals["rank_and_cap_sweep"][cap]
        lines.append(
            f"| {cap} | {item['surfaced_never_reviewed']} | {item['never_reviewed_denominator']} | "
            f"{item['capture_share']} | {item['max_added_load_per_setting']} |"
        )
    lines.extend(["", "## Adaptive comparison", ""])
    for item in summaries:
        adaptive = item["adaptive_cap_comparison"]
        lines.append(
            f"- {item['setting']}: K={adaptive['candidate_cap']}, capture={adaptive['capture_share']}, "
            f"transactions={adaptive['added_review_transactions']} (comparison only)."
        )
    summary_md = OUT / "summary.md"
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_experiment_manifest(
        OUT,
        experiment_id="EXP-008",
        experiment_version="2.0",
        config_version="trigger-ranking-and-caps-1.0",
        claim_scope=claim,
        script_path=Path(__file__),
        inputs=inputs,
        outputs=[csv_path, summary_path, summary_md],
        config={
            "settings": list(SETTINGS),
            "uniform_caps": list(UNIFORM_CAPS),
            "adaptive_cap_status": "comparison only",
        },
        metric_schema={
            "capture_share": "surfaced unstable never-reviewed guidelines / fixed unstable never-reviewed count",
            "added_review_transactions": "unique guideline review transactions per setting",
        },
    )
    print(
        f"EXP-008 done: {totals['unstable_guidelines']} unstable; {total_denominator} never reviewed -> {OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
