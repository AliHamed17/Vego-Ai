"""Compare two H-layer experiment iterations and emit a delta report.

Usage: python scripts/hlayer_iteration_compare.py <prev_iter_dir> <cur_iter_dir>
Writes <cur_iter_dir>/iteration_report.md. Robust to schema drift between
iterations (missing metrics are reported as n/a, never guessed).
"""
from __future__ import annotations

import json
import os
import sys


def load(d, name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def get(d, *path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def fmt(v):
    return "n/a" if v is None else v


def delta_row(name, prev, cur, better="higher"):
    arrow = ""
    if isinstance(prev, (int, float)) and isinstance(cur, (int, float)) and prev != cur:
        improved = (cur > prev) if better == "higher" else (cur < prev)
        arrow = " (BETTER)" if improved else " (worse)"
    elif prev is None and cur is not None:
        arrow = " (new metric)"
    return f"| {name} | {fmt(prev)} | {fmt(cur)}{arrow} |"


def mode_metrics(summary, mode):
    for r in get(summary, "results", "ALL") or []:
        if r.get("mode") == mode:
            return r
    return {}


def exp010_bound(summary, bound):
    for row in get(summary, "results") or []:
        if row.get("round_bound") == bound:
            return row
    return {}


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    prev_dir, cur_dir = sys.argv[1], sys.argv[2]
    rows = ["# H-Layer Iteration Comparison", "",
            f"Previous: `{os.path.basename(prev_dir)}`  Current: `{os.path.basename(cur_dir)}`", "",
            "Claim scope: design/mechanism metrics only - no accuracy claims until the EXP-005 gate passes.",
            "", "| Metric | Previous | Current |", "| --- | ---: | ---: |"]

    p6, c6 = load(prev_dir, "exp006-summary.json"), load(cur_dir, "exp006-summary.json")
    rows.append(delta_row("M-A1 total events", get(p6, "totals", "total_events"), get(c6, "totals", "total_events")))
    rows.append(delta_row("M-A2 early-stage share", get(p6, "totals", "early_stage_share"), get(c6, "totals", "early_stage_share")))
    rows.append(delta_row("severity mass (new in v2)", get(p6, "totals", "severity_mass"), get(c6, "totals", "severity_mass")))
    rows.append(delta_row("sev>=2 events", get(p6, "totals", "sev2plus_events"), get(c6, "totals", "sev2plus_events")))

    p7, c7 = load(prev_dir, "exp007-summary.json"), load(cur_dir, "exp007-summary.json")
    for mode in ("threshold_sev1", "threshold_sev2", "threshold_sev3", "first_n_then_auto", "threshold"):
        pm, cm = mode_metrics(p7, mode), mode_metrics(c7, mode)
        if not pm and not cm:
            continue
        rows.append(delta_row(f"M-B1 load [{mode}]", pm.get("load_vs_every_decision"), cm.get("load_vs_every_decision"), better="lower"))
        rows.append(delta_row(f"M-B5 bundled case load [{mode}]", pm.get("bundled_load"), cm.get("bundled_load"), better="lower"))
        rows.append(delta_row(f"M-B2 weighted coverage [{mode}]", pm.get("weighted_severity_coverage"), cm.get("weighted_severity_coverage")))
        rows.append(delta_row(f"M-B4 high-sev coverage [{mode}]", pm.get("high_severity_coverage"), cm.get("high_severity_coverage")))
        rows.append(delta_row(f"M-B3 efficiency [{mode}]", pm.get("efficiency"), cm.get("efficiency")))
        rows.append(delta_row(f"M-B6 bundled efficiency [{mode}]", pm.get("bundled_efficiency"), cm.get("bundled_efficiency")))

    p8, c8 = load(prev_dir, "exp008-summary.json"), load(cur_dir, "exp008-summary.json")
    rows.append(delta_row("unstable never reviewed", get(p8, "totals", "unstable_never_reviewed"), get(c8, "totals", "unstable_never_reviewed"), better="lower"))
    for t in ("1", "2", "3"):
        rows.append(delta_row(f"M-C1 churn capture share [t={t}]",
                              get(p8, "totals", "churn_trigger_sweep", t, "capture_share"),
                              get(c8, "totals", "churn_trigger_sweep", t, "capture_share")))
        rows.append(delta_row(f"M-C2 max added load/setting [t={t}]",
                              get(p8, "totals", "churn_trigger_sweep", t, "max_added_load_per_setting"),
                              get(c8, "totals", "churn_trigger_sweep", t, "max_added_load_per_setting"), better="lower"))
    for k in ("10", "20", "30", "35", "40"):
        rows.append(delta_row(f"M-C1 rank-and-cap capture share [K={k}]",
                              get(p8, "totals", "rank_and_cap_sweep", k, "capture_share"),
                              get(c8, "totals", "rank_and_cap_sweep", k, "capture_share")))
        rows.append(delta_row(f"M-C2 rank-and-cap max added load [K={k}]",
                              get(p8, "totals", "rank_and_cap_sweep", k, "max_added_load_per_setting"),
                              get(c8, "totals", "rank_and_cap_sweep", k, "max_added_load_per_setting"), better="lower"))

    p9, c9 = load(prev_dir, "exp009-summary.json"), load(cur_dir, "exp009-summary.json")
    if p9 or c9:
        rows.append(delta_row("EXP-009 synthetic false positives",
                              get(p9, "metrics", "false_positives"),
                              get(c9, "metrics", "false_positives"), better="lower"))
        rows.append(delta_row("EXP-009 synthetic false negatives",
                              get(p9, "metrics", "false_negatives"),
                              get(c9, "metrics", "false_negatives"), better="lower"))

    p10, c10 = load(prev_dir, "exp010-summary.json"), load(cur_dir, "exp010-summary.json")
    if p10 or c10:
        pm, cm = exp010_bound(p10, 2), exp010_bound(c10, 2)
        rows.append(delta_row("EXP-010 B=2 timed-out/parked",
                              pm.get("timed_out_parked"), cm.get("timed_out_parked"), better="lower"))
        rows.append(delta_row("EXP-010 B=2 needs adjudication (not resolution)",
                              pm.get("needs_adjudication"), cm.get("needs_adjudication"), better="lower"))

    p12, c12 = load(prev_dir, "exp012-summary.json"), load(cur_dir, "exp012-summary.json")
    if p12 or c12:
        rows.append(delta_row("M-D generalization-safe labels available",
                              get(p12, "generalization_safe_baseline", "rows"),
                              get(c12, "generalization_safe_baseline", "rows")))
        rows.append(f"| M-D generalization-safe baseline status | {fmt(get(p12, 'generalization_safe_baseline', 'status'))} | {fmt(get(c12, 'generalization_safe_baseline', 'status'))} |")

    rows += ["", "Verdict rule: BETTER if a target metric improves with no guardrail degradation "
             "(see docs/research/h-layer/experiment-iteration-loop.md); record the verdict in the ledger. "
             "EXP-012 same-pattern material is excluded from verdict inputs. Harness-only iterations should be recorded NEUTRAL."]
    out = os.path.join(cur_dir, "iteration_report.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    print(f"iteration report -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
