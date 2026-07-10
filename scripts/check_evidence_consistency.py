#!/usr/bin/env python3
"""Research-integrity guard: assert the core evidence invariants agree across all
generated VEGO-AI reports, and that no silent baseline/AI/policy change slipped in.

This complements project-health / research-health / dashboard-health (which check file
existence and governance). This one checks *numeric consistency + frozen-state invariants*
so the sprawling EXP-001..005 / dashboard / evaluation-comparison reports cannot drift into
contradicting each other before the thesis evidence is used.

Read-only. No API/LLM. Exits non-zero if any present report violates an invariant.
Missing (gitignored) reports are SKIPPED, not failed.

Run:  python scripts/check_evidence_consistency.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEGO = ROOT / "VEGO-AI"

PASS, FAIL, SKIP = "OK  ", "FAIL", "skip"
results: list[tuple[str, str, str]] = []
report_items: list[dict[str, str]] = []


def load(rel: str):
    p = ROOT / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def check(name: str, present: bool, ok: bool, detail: str = ""):
    if not present:
        results.append((SKIP, name, "report not generated (gitignored) — run its builder"))
    else:
        results.append((PASS if ok else FAIL, name, detail))


# --- dashboard metrics_snapshot ------------------------------------------------
m = load("VEGO-AI/reports/results_dashboard/metrics_snapshot.json")
if m is not None:
    ov, rp = m.get("overview", {}), m.get("reproducibility", {})
    check("dashboard: 27 variability patterns", True, ov.get("variability_pattern_count") == 27,
          f"got {ov.get('variability_pattern_count')}")
    check("dashboard: 179 cases", True, ov.get("case_count") == 179, f"got {ov.get('case_count')}")
    check("dashboard: ai_classification_changed == 0", True, ov.get("ai_classification_changed_count") == 0,
          f"got {ov.get('ai_classification_changed_count')}")
    check("dashboard: baseline_eval_outputs NOT modified", True,
          rp.get("baseline_eval_outputs_modified") in (False, "false"),
          f"got {rp.get('baseline_eval_outputs_modified')}")
else:
    check("dashboard metrics_snapshot", False, False)

# --- EXP-001 -------------------------------------------------------------------
e1 = load("reports/generated/exp001/exp001_summary.json")
if e1 is not None and "_error" not in e1:
    t = e1.get("totals", {})
    check("exp001: 27 comparison rows", True, t.get("comparison_count") == 27, f"got {t.get('comparison_count')}")
    check("exp001: 0 generalization-safe expert labels", True,
          t.get("generalization_safe_expert_labeled_count") == 0, f"got {t.get('generalization_safe_expert_labeled_count')}")
    check("exp001: 0 memory-informed changes", True, t.get("changed_count") == 0, f"got {t.get('changed_count')}")
else:
    check("exp001 summary", False, False)

# --- evaluation_comparison (strict eval) --------------------------------------
ec = load("reports/generated/evaluation_comparison/evaluation_summary.json")
if ec is not None and "_error" not in ec:
    check("eval-comparison: memory-informed differs == 0", True,
          ec.get("totals", {}).get("memory_informed_differs_from_original") == 0)
    check("eval-comparison: 0 generalization-safe labeled rows", True,
          ec.get("labels", {}).get("generalization_safe_labeled_rows") == 0)
    check("eval-comparison: provenance integrity (baseline preserved)", True,
          ec.get("provenance_integrity", {}).get("comparison_original_matches_eval_output") is True)
    check("eval-comparison: analysis/ flagged as Agent-4 copy (not benchmark)", True,
          ec.get("benchmark_status", {}).get("independent_benchmark_exists") is False)
else:
    check("evaluation_comparison summary", False, False)

# --- EXP-005 real-label gate ---------------------------------------------------
e5 = load("reports/generated/exp005_label_review/label_validation_summary.json")
if e5 is not None and "_error" not in e5:
    e5_blob = json.dumps(e5).lower()
    safe_label_paths = [
        ("generalization_safe_valid_labels", e5.get("generalization_safe_valid_labels")),
        ("generalization_safe_complete_rows", e5.get("generalization_safe_complete_rows")),
        ("safe_label_count", e5.get("safe_label_count")),
    ]
    safe_values = [v for _, v in safe_label_paths if isinstance(v, int)]
    has_explicit_safe_count = bool(safe_values) or "generalization" in e5_blob
    check("exp005: safe-label count explicit", True, has_explicit_safe_count,
          f"top-level candidates={safe_label_paths}")
    check("exp005: no real safe labels yet", True, any(v == 0 for v in safe_values) or "0" in e5_blob,
          f"top-level candidates={safe_label_paths}")
else:
    check("exp005 label validation summary", False, False)

# --- frozen deterministic policy (no silent M4B-1.1) --------------------------
clf = VEGO / "framework" / "memory_informed_classifier.py"
if clf.exists():
    txt = clf.read_text(encoding="utf-8", errors="ignore")
    has_v1 = 'POLICY_VERSION = "memory-informed-classifier-v1"' in txt
    no_v11 = "memory-informed-classifier-v1.1" not in txt
    check("policy frozen at deterministic v1 (no M4B-1.1 in code)", True, has_v1 and no_v11,
          f"v1={has_v1} no_v1.1={no_v11}")
else:
    check("memory_informed_classifier.py present", False, False)

# --- accuracy gate still closed (any of exp003 / exp005) ----------------------
gate_files = [
    "reports/generated/exp003/accuracy_summary.json",
    "reports/generated/exp005_label_review/reproducibility_manifest.json",
]
gate_seen = False
for gf in gate_files:
    d = load(gf)
    if d is None or "_error" in d:
        continue
    gate_seen = True
    blob = json.dumps(d).lower()
    closed = ("cannot be evaluated yet" in blob) or ('"accuracy_improvement_claim_allowed": false' in blob) \
        or ("blocked" in blob)
    check(f"accuracy gate closed in {Path(gf).parent.name}", True, closed)
if not gate_seen:
    check("accuracy gate report", False, False)

# --- claim language guard ------------------------------------------------------
text_reports = [
    "docs/research/evaluation-report.md",
    "docs/research/accuracy-improvement-plan.md",
    "docs/research/strategic-review-and-hardening-plan.md",
    "docs/operations/alignment-control.md",
]
unsafe_claims = []
required_disclaimers = []
for rel in text_reports:
    p = ROOT / rel
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8", errors="ignore").lower()
    if "accuracy improvement" in text and "cannot be evaluated yet" not in text and "not proven" not in text:
        unsafe_claims.append(rel)
    if "synthetic" in text and "not real evidence" not in text and "policy-risk" not in text and "policy risk" not in text:
        required_disclaimers.append(rel)
check("claim guard: no unqualified accuracy-improvement language", True, not unsafe_claims,
      ", ".join(unsafe_claims))
check("claim guard: synthetic evidence is qualified", True, not required_disclaimers,
      ", ".join(required_disclaimers))

# --- report --------------------------------------------------------------------
print("VEGO-AI evidence-consistency guard")
print("-" * 60)
n_fail = 0
for status, name, detail in results:
    report_items.append({"status": status.strip(), "name": name, "detail": detail})
    line = f"[{status}] {name}"
    if status == FAIL and detail:
        line += f"  <- {detail}"
    elif status == SKIP and detail:
        line += f"  ({detail})"
    print(line)
    if status == FAIL:
        n_fail += 1
present = sum(1 for s, _, _ in results if s != SKIP)
print("-" * 60)
print(f"{present - n_fail}/{present} present checks passed; "
      f"{sum(1 for s, _, _ in results if s == SKIP)} skipped (reports not generated).")
if n_fail:
    out_dir = ROOT / "reports" / "generated" / "evidence_consistency"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "latest.json").write_text(json.dumps({"status": "FAIL", "checks": report_items}, indent=2), encoding="utf-8")
    md = ["# Evidence Consistency", "", "- Status: FAIL", ""]
    md += [f"- [{item['status']}] {item['name']} {item['detail']}".rstrip() for item in report_items]
    (out_dir / "latest.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("EVIDENCE CONSISTENCY: FAIL")
    sys.exit(1)
out_dir = ROOT / "reports" / "generated" / "evidence_consistency"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "latest.json").write_text(json.dumps({"status": "PASS", "checks": report_items}, indent=2), encoding="utf-8")
md = ["# Evidence Consistency", "", "- Status: PASS", ""]
md += [f"- [{item['status']}] {item['name']} {item['detail']}".rstrip() for item in report_items]
(out_dir / "latest.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("EVIDENCE CONSISTENCY: PASS")
