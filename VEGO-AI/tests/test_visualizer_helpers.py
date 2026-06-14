from pathlib import Path
import sys
import tempfile


VISUALIZER_DIR = Path(__file__).resolve().parents[1] / "vego_visualizer_delivery"
if str(VISUALIZER_DIR) not in sys.path:
    sys.path.insert(0, str(VISUALIZER_DIR))

from visualizer_utils import (  # noqa: E402
    detect_model_result_match,
    extract_case_id_from_agentc_filename,
    extract_case_id_from_filename,
    extract_case_id_from_json,
    find_matching_model_for_result,
)


def test_extract_case_id_examples():
    assert extract_case_id_from_filename("70233_ex1_CD_FINAL_2026_NoaMeitar.txt") == "70233"
    assert extract_case_id_from_filename(r"C:\models\68064_ex1_UCD_FINAL.txt") == "68064"
    assert extract_case_id_from_agentc_filename("agentC_case_68064.json") == "68064"
    assert extract_case_id_from_agentc_filename("not_agent_c_68064.json") is None
    assert extract_case_id_from_json({"case_id": 70234}) == "70234"
    assert extract_case_id_from_json({"metadata": {"case_id": "68059"}}) == "68059"


def test_matching_true_for_same_case_and_diagram():
    match = detect_model_result_match(
        "70233_ex1_CD_FINAL_2026_NoaMeitar.txt",
        "agentC_case_70233.json",
        {"case_id": "70233", "diagram_type": "CD", "domain": "ParkWise"},
    )

    assert match["matched"] is True
    assert match["mismatch_type"] == "none"
    assert match["model_case_id"] == "70233"
    assert match["result_case_id"] == "70233"


def test_mismatching_case_ids_are_false():
    match = detect_model_result_match(
        "70233_ex1_CD_FINAL_2026_NoaMeitar.txt",
        "agentC_case_68064.json",
        {"case_id": "68064", "diagram_type": "CD"},
    )

    assert match["matched"] is False
    assert match["mismatch_type"] == "case_id_mismatch"
    assert "70233" in match["warning_message"]
    assert "68064" in match["warning_message"]


def test_stale_model_after_aggregate_selection_is_detected():
    stale_selection = detect_model_result_match(
        "70234_ex1_CD_FINAL_2026_JoelleLady.txt",
        "agentC_case_68064.json",
        {"case_id": "68064"},
    )

    assert stale_selection["matched"] is False
    assert stale_selection["mismatch_type"] == "case_id_mismatch"
    assert stale_selection["recommended_action"].endswith("68064_.")


def test_missing_matching_model_returns_no_matching_model_found():
    match = detect_model_result_match(None, "agentC_case_68064.json", {"case_id": "68064"})

    assert match["matched"] is False
    assert match["mismatch_type"] == "no_matching_model_found"
    assert match["model_case_id"] is None
    assert match["result_case_id"] == "68064"


def test_find_matching_model_uses_case_prefix_not_substring():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "x68064_ex1_UCD.txt").write_text("@startuml\n@enduml\n", encoding="utf-8")
        (root / "68064_ex1_UCD.txt").write_text("@startuml\n@enduml\n", encoding="utf-8")
        (root / "68064_notes.md").write_text("ignore", encoding="utf-8")

        match = find_matching_model_for_result(root, "68064")

    assert match is not None
    assert Path(match).name == "68064_ex1_UCD.txt"


def test_cross_domain_mismatch_detected():
    match = detect_model_result_match(
        "68064_ex1_UCD_FINAL.txt",
        "agentC_case_68064.json",
        {"case_id": "68064", "domain": "ParkWise parking vehicle permit"},
    )

    assert match["matched"] is False
    assert match["mismatch_type"] == "possible_domain_mismatch"
    assert match["model_domain"] == "Cheers"
    assert match["result_domain"] == "ParkWise"


def test_diagram_mismatch_detected():
    match = detect_model_result_match(
        "68064_ex1_UCD_FINAL.txt",
        "agentC_case_68064.json",
        {"case_id": "68064", "diagram_type": "CD"},
    )

    assert match["matched"] is False
    assert match["mismatch_type"] == "possible_diagram_mismatch"
    assert match["model_diagram_type"] == "UCD"
    assert match["result_diagram_type"] == "CD"


def _run_all():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()


if __name__ == "__main__":
    _run_all()
    print("visualizer helper tests passed")
