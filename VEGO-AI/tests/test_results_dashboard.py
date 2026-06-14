from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import build_results_dashboard as brd  # noqa: E402


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "VEGO-AI"
    eval_dir = root / "eval_output" / "ucd_ch"
    human_dir = root / "human_review_output" / "ucd_ch"

    _write_json(
        eval_dir / "agentC_all_scores.json",
        {
            "ranking": [
                {"rank": 1, "case_id": "A", "score_pct": 90.0, "overall_assessment": "strong"},
                {"rank": 2, "case_id": "B", "score_pct": 70.0, "overall_assessment": "medium"},
            ]
        },
    )
    _write_json(
        eval_dir / "agentC_case_A.json",
        {
            "existing_mapping": [
                {"guideline_id": "G1", "compliance_status": "Satisfied"},
                {"guideline_id": "G2", "compliance_status": "Partially-Satisfied"},
                {"guideline_id": "G3", "compliance_status": "Not-Satisfied"},
            ]
        },
    )
    _write_json(
        eval_dir / "agentD_variability_classes__ucd_ch.json",
        {
            "variability_classifications": [
                {
                    "pattern_id": "P1",
                    "classification": "Substantial Variability",
                    "confidence": "High",
                    "flag_for_guidelines_update": True,
                },
                {
                    "pattern_id": "P2",
                    "classification": "Occasional Variability",
                    "confidence": "Medium",
                    "flag_for_guidelines_update": False,
                },
            ]
        },
    )
    _write_json(
        eval_dir / "agentD_deviation_patterns_ucd_ch.json",
        {
            "recurring_guideline_patterns": [
                {
                    "pattern_id": "P1",
                    "guideline_id": "G1",
                    "description": "Guideline pattern",
                    "affected_cases": ["A", "B"],
                    "pattern_strength": "50.0%",
                }
            ],
            "recurring_fragment_patterns": [
                {
                    "pattern_id": "P2",
                    "description": "Fragment pattern",
                    "affected_cases": ["A"],
                    "pattern_strength": "25.0%",
                }
            ],
        },
    )
    _write_jsonl(
        human_dir / "human_review_queue.jsonl",
        [
            {
                "review_id": "HRQ-1",
                "status": "pending",
                "setting_id": "ucd_ch",
                "related_guideline_id": "G1",
                "trigger_reasons": ["medium_confidence"],
                "pattern_strength": {"value": 0.5, "display": "50.0%"},
                "ai_decision": {"classification": "Substantial Variability"},
            }
        ],
    )
    _write_jsonl(
        human_dir / "human_review_queue_resolved.jsonl",
        [
            {
                "review_id": "HRQ-1",
                "status": "resolved",
                "related_guideline_id": "G1",
                "human_feedback": {
                    "feedback_id": "HF-1",
                    "human_decision": {
                        "decision_type": "valid_alternative",
                        "corrected_classification": "Substantial Variability",
                    },
                    "reusable": True,
                    "guideline_update": {"action": "add_alternative"},
                },
            }
        ],
    )
    _write_jsonl(
        human_dir / "human_judgment_memory.jsonl",
        [
            {
                "memory_id": "HJM-1",
                "status": "active",
                "conflict_status": "none",
                "decision_type": "valid_alternative",
                "related_guideline_id": "G1",
                "reuse_scope": {"applies_to_future_models": True},
            }
        ],
    )
    _write_json(
        human_dir / "memory_advice.json",
        {
            "advice_mode": "advisory_only",
            "advice": [
                {
                    "advice_id": "MADV-1",
                    "pattern_id": "P1",
                    "advice_mode": "advisory_only",
                    "advice_strength": "strong",
                    "memory_matches": [{"memory_id": "HJM-1"}],
                    "has_conflicting_memory": False,
                    "ai_classification_changed": False,
                }
            ],
        },
    )
    return root


def _build(tmp_path: Path, root: Path | None = None, *, json_only: bool = False) -> tuple[dict, Path]:
    root = root or _fixture_root(tmp_path)
    out = tmp_path / "dashboard"
    snapshot = brd.build_dashboard(root=root, out_dir=out, settings=["ucd_ch"], json_only=json_only)
    return snapshot, out


def test_parse_minimal_agent_c_scores(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    perf = snapshot["settings"]["ucd_ch"]["model_performance"]
    assert perf["case_count"] == 2
    assert perf["score_mean"] == 80.0
    assert perf["compliance_status_counts"]["Satisfied"] == 1
    assert perf["compliance_status_counts"]["Partially-Satisfied"] == 1
    assert perf["compliance_status_counts"]["Not-Satisfied"] == 1


def test_parse_minimal_agent_d_variability(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    variability = snapshot["settings"]["ucd_ch"]["variability"]
    assert variability["classification_count"] == 2
    assert variability["classification_counts"]["Substantial Variability"] == 1
    assert variability["classification_counts"]["Occasional Variability"] == 1
    assert variability["pattern_count"] == 2
    assert variability["top_patterns"][0]["pattern_id"] == "P1"


def test_parse_human_review_queue_jsonl(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    queue = snapshot["settings"]["ucd_ch"]["human_review_queue"]
    assert queue["queue_count"] == 1
    assert queue["pending_count"] == 1
    assert queue["trigger_counts"]["medium_confidence"] == 1
    assert queue["guideline_counts"]["G1"] == 1


def test_parse_resolved_human_feedback(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    feedback = snapshot["settings"]["ucd_ch"]["human_feedback"]
    assert feedback["resolved_feedback_count"] == 1
    assert feedback["decision_counts"]["valid_alternative"] == 1
    assert feedback["reusable_count"] == 1
    assert feedback["guideline_update_count"] == 1


def test_parse_human_judgment_memory(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    memory = snapshot["settings"]["ucd_ch"]["human_judgment_memory"]
    assert memory["memory_count"] == 1
    assert memory["active_count"] == 1
    assert memory["decision_counts"]["valid_alternative"] == 1
    assert memory["reusable_count"] == 1


def test_parse_memory_advice(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    advice = snapshot["settings"]["ucd_ch"]["memory_advisory"]
    assert advice["advice_count"] == 1
    assert advice["strength_counts"]["strong"] == 1
    assert advice["matched_advice_count"] == 1
    assert advice["advisory_only_boundary_ok"] is True


def test_missing_files_safe(tmp_path: Path):
    root = tmp_path / "VEGO-AI"
    snapshot, out = _build(tmp_path, root=root)
    assert out.joinpath("metrics_snapshot.json").exists()
    assert snapshot["settings"]["ucd_ch"]["model_performance"]["case_count"] == 0
    assert snapshot["health"]["files_missing"]


def test_invalid_json_records_health_issue(tmp_path: Path):
    root = tmp_path / "VEGO-AI"
    bad = root / "eval_output" / "ucd_ch" / "agentC_all_scores.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{not-json", encoding="utf-8")
    snapshot, _ = _build(tmp_path, root=root)
    assert snapshot["health"]["parse_errors"]
    assert "agentC_all_scores.json" in snapshot["health"]["parse_errors"][0]["path"]


def test_metrics_snapshot_generated(tmp_path: Path):
    snapshot, out = _build(tmp_path)
    generated = json.loads(out.joinpath("metrics_snapshot.json").read_text(encoding="utf-8"))
    assert generated["schema_version"] == brd.SCHEMA_VERSION
    assert generated["overview"]["case_count"] == snapshot["overview"]["case_count"]


def test_index_generated(tmp_path: Path):
    _, out = _build(tmp_path)
    html = out.joinpath("index.html").read_text(encoding="utf-8")
    assert "VEGO-AI Results Dashboard" in html
    assert "Human Judgment Memory" in html
    assert "Memory Advisory" in html


def test_m4a_boundary_ai_classification_changed_count_zero(tmp_path: Path):
    snapshot, _ = _build(tmp_path)
    advice = snapshot["settings"]["ucd_ch"]["memory_advisory"]
    assert advice["ai_classification_changed_count"] == 0
    assert snapshot["overview"]["ai_classification_changed_count"] == 0


def test_generation_with_temp_fixture_dir(tmp_path: Path):
    root = _fixture_root(tmp_path)
    out = tmp_path / "custom-out"
    result = brd.main(["--root", str(root), "--out", str(out), "--settings", "ucd_ch"])
    assert result == 0
    assert out.joinpath("index.html").exists()
    assert out.joinpath("settings", "ucd_ch.html").exists()


def test_json_only_generates_snapshot_without_html(tmp_path: Path):
    _, out = _build(tmp_path, json_only=True)
    assert out.joinpath("metrics_snapshot.json").exists()
    assert not out.joinpath("index.html").exists()


def _run_all() -> int:
    funcs = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    failures = 0
    for func in funcs:
        try:
            with tempfile.TemporaryDirectory() as directory:
                func(Path(directory))
            print(f"PASS {func.__name__}")
        except Exception as exc:  # pragma: no cover - direct runner aid
            failures += 1
            print(f"FAIL {func.__name__}: {exc}")
    return failures


if __name__ == "__main__":
    raise SystemExit(_run_all())
