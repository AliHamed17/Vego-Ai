from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "build_hlayer_decision_snapshot.py"
REPO = SCRIPT.parents[1]
SPEC = importlib.util.spec_from_file_location("build_hlayer_decision_snapshot", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def register(outcomes: dict[str, str]) -> str:
    sections = []
    for number in range(1, 7):
        decision_id = f"M-{number:02d}"
        sections.append(
            "\n".join(
                [
                    f"## {decision_id} - Decision {number}",
                    "",
                    "| Field | Value |",
                    "| --- | --- |",
                    f"| ID | {decision_id} |",
                    f"| exact decision requested | Decide {number}. |",
                    f"| outcome | {outcomes.get(decision_id, '')} |",
                    "| selected value | Recorded selection. |",
                    "| rationale | Recorded rationale. |",
                    "| approver | Iris and Arnon. |",
                    "| decision date | 2026-07-15. |",
                    "| due date | 2026-07-15. |",
                    "| confirmation status | Open choice. |",
                ]
            )
        )
    return "\n\n".join(sections) + "\n"


def test_unrecorded_and_ambiguous_outcomes_are_deferred(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    source.write_text(register({"M-01": "Not yet recorded.", "M-02": "Maybe"}), encoding="utf-8")
    snapshot = MODULE.build_snapshot(source)
    by_id = {item["id"]: item for item in snapshot["decisions"]}
    assert by_id["M-01"]["effective_outcome"] == "Deferred"
    assert by_id["M-01"]["outcome_interpretation"] == "placeholder_or_blank"
    assert by_id["M-02"]["effective_outcome"] == "Deferred"
    assert by_id["M-02"]["outcome_interpretation"] == "ambiguous_unrecognized"
    assert snapshot["program_mode"] == "offline_only"


def test_m05_acceptance_alone_never_authorizes_live_work(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    source.write_text(register({"M-05": "Accepted"}), encoding="utf-8")
    snapshot = MODULE.build_snapshot(source)
    assert snapshot["live_shadow_authorized"] is False
    assert any(
        "authorization record is absent" in reason for reason in snapshot["authorization_blockers"]
    )


def test_outcome_without_recorded_rationale_remains_incomplete(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    source.write_text(
        register({"M-02": "Accepted"}).replace("Recorded rationale.", "To be recorded."),
        encoding="utf-8",
    )
    snapshot = MODULE.build_snapshot(source)
    by_id = {item["id"]: item for item in snapshot["decisions"]}
    assert by_id["M-02"]["decision_complete"] is False
    assert by_id["M-02"]["selected_value"] is None


def test_selected_value_is_not_inferred_from_rationale(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    content = register({"M-02": "Accepted"}).replace(
        "| selected value | Recorded selection. |", "| selected value | Not yet recorded. |"
    )
    source.write_text(content, encoding="utf-8")
    snapshot = MODULE.build_snapshot(source)
    by_id = {item["id"]: item for item in snapshot["decisions"]}
    assert by_id["M-02"]["rationale"] == "Recorded rationale"
    assert by_id["M-02"]["selected_value"] is None
    assert by_id["M-02"]["decision_complete"] is False


def test_exact_separate_authorization_opens_gate_deterministically(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    source.write_text(
        register(
            {
                "M-02": "Accepted",
                "M-03": "Accepted with changes",
                "M-04": "Rejected",
                "M-05": "Accepted with changes",
            }
        ),
        encoding="utf-8",
    )
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "authorization_id": "AUTH-001",
                "approved_at": "2026-07-16",
                "approver": "Iris and Arnon",
                "scope": "h_layer_shadow_listener",
                "allowed_touch_outcome": "Accepted",
                "implementation_outcome": "Accepted",
                "allowed_touches": list(reversed(MODULE.EXPECTED_TOUCHES)),
            }
        ),
        encoding="utf-8",
    )
    first = MODULE.build_snapshot(source, authorization)
    second = MODULE.build_snapshot(source, authorization)
    assert first == second
    assert first["live_shadow_authorized"] is True
    assert first["program_mode"] == "live_shadow_authorized"


def test_authorization_rejects_extra_touch(tmp_path: Path) -> None:
    source = tmp_path / "register.md"
    source.write_text(register({"M-05": "Accepted"}), encoding="utf-8")
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "authorization_id": "AUTH-002",
                "approved_at": "2026-07-16",
                "approver": "Iris and Arnon",
                "scope": "h_layer_shadow_listener",
                "allowed_touch_outcome": "Accepted",
                "implementation_outcome": "Accepted",
                "allowed_touches": [*MODULE.EXPECTED_TOUCHES, "VEGO-AI/framework/agent4.py"],
            }
        ),
        encoding="utf-8",
    )
    snapshot = MODULE.build_snapshot(source, authorization)
    assert snapshot["live_shadow_authorized"] is False
    assert any("does not exactly match" in reason for reason in snapshot["authorization_blockers"])


def test_tracked_authorization_template_matches_boundary_but_cannot_approve() -> None:
    template = REPO / "docs/research/h-layer/allowed-touch-authorization.template.json"
    record, reasons = MODULE.read_authorization(template)
    assert record is not None
    assert set(record["allowed_touches"]) == set(MODULE.EXPECTED_TOUCHES)
    assert record["_template_notice"] == "TEMPLATE_ONLY_NOT_AN_APPROVAL_RECORD"
    assert any("missing nonblank authorization_id" in reason for reason in reasons)
    assert any("allowed-touch list is not explicitly accepted" in reason for reason in reasons)
    assert any("implementation is not separately" in reason for reason in reasons)
