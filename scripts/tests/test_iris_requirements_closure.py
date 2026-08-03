from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_iris_requirements_closure.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_iris_requirements_closure", SCRIPT
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_control_set_is_exact_and_contiguous() -> None:
    expected = (
        tuple(f"R-{index:02d}" for index in range(1, 20))
        + tuple(f"A-{index:02d}" for index in range(1, 16))
        + tuple(f"Q-{index:02d}" for index in range(1, 11))
    )
    assert MODULE.EXPECTED_IDS == expected
    assert len(MODULE.EXPECTED_IDS) == 44


def test_all_structural_checks_pass_without_promoting_human_gates() -> None:
    results = [MODULE.RUNNERS[experiment]() for experiment in MODULE.EXPERIMENTS]

    assert MODULE.EXPERIMENTS == tuple(
        f"IRIS-EXP-{index:02d}" for index in range(1, 11)
    )
    assert all(result.passed_for_mode("structure") for result in results)
    assert [result.state for result in results] == [
        "PASS",
        "READY_PENDING_HUMAN_RUN",
        "PASS",
        "READY_PENDING_NEXT_MEETING",
        "STRUCTURE_PASS_PENDING_FULL_MEDIA_HUMAN_REVIEW",
        "STRUCTURE_PASS_PENDING_DUAL_BILINGUAL_REVIEW",
        "PASS",
        "STRUCTURE_PASS_PENDING_REHEARSAL_AND_DELIVERY",
        "STRUCTURE_PASS_PENDING_SUPERVISOR_DECISIONS",
        "STRUCTURE_PASS_CERTIFICATE_NOT_ISSUED",
    ]


def test_readiness_and_closure_modes_fail_closed_on_pending_human_evidence() -> None:
    results = [MODULE.RUNNERS[experiment]() for experiment in MODULE.EXPERIMENTS]

    assert not all(result.passed_for_mode("readiness") for result in results)
    assert not all(result.passed_for_mode("closure") for result in results)
    assert not MODULE.RUNNERS["IRIS-EXP-05"]().passed_for_mode("readiness")
    assert not MODULE.RUNNERS["IRIS-EXP-10"]().passed_for_mode("closure")


def test_structure_mode_render_names_selected_gate() -> None:
    report = MODULE.render([MODULE.RUNNERS["IRIS-EXP-05"]()], "structure")

    assert "Selected gate mode: **structure**" in report
    assert "Structure gate: **PASS**" in report
    assert "STRUCTURE_PASS_PENDING_FULL_MEDIA_HUMAN_REVIEW" in report


def test_audited_readiness_distribution_is_preserved() -> None:
    assert MODULE.EXPECTED_STATUS_COUNTS == {
        "Verified complete": 2,
        "Implemented awaiting human acceptance": 6,
        "Partial": 22,
        "Open": 5,
        "Blocked": 9,
    }


def test_master_parser_keeps_canonical_rows_before_companion_status_view() -> None:
    rows = MODULE.table_rows(MODULE.MASTER)

    assert tuple(rows) == MODULE.EXPECTED_IDS
    assert all(len(row) == 11 for row in rows.values())


def test_exp05_independently_reconciles_interval_union_and_gap_ledger() -> None:
    source_rows = MODULE.read_jsonl(MODULE.MACHINE_JSONL)
    metrics, expected_gaps = MODULE.machine_timeline_accounting(source_rows)
    result = MODULE.RUNNERS["IRIS-EXP-05"]()
    structure_checks = {check.name: check for check in result.checks}

    assert metrics["asr_interval_union_seconds"] == MODULE.Decimal("2333.500")
    assert metrics["uncovered_seconds"] == MODULE.Decimal("452.783")
    assert metrics["machine_accounted_timeline_seconds"] == MODULE.Decimal(
        "2786.283"
    )
    assert metrics["internal_gap_count"] == 932
    assert len(expected_gaps) == 934
    assert structure_checks[
        "ASR interval union and uncovered intervals account for the complete media duration"
    ].passed
    assert structure_checks[
        "machine uncovered-interval ledger is exact and remains human-pending"
    ].passed
    assert not result.passed_for_mode("readiness")


def test_decision_vocabulary_maps_supersession_and_rejects_legacy_approve() -> None:
    outcomes = MODULE.decision_outcomes(
        "\n".join(
            (
                "| D-RQ-01 | Decision | Confirm |",
                "| D-RQ-02 | Decision | Confirm with correction |",
                "| D-RQ-03 | Decision | Retire or supersede |",
                "| D-RQ-04 | Decision | Defer |",
                "| D-RQ-05 | Decision | Approve |",
            )
        )
    )

    assert outcomes == {
        "D-RQ-01": "Confirm",
        "D-RQ-02": "Confirm with correction",
        "D-RQ-03": "Retire or supersede",
        "D-RQ-04": "Defer",
    }


def test_presentation_readiness_requires_artifacts_hashes_qa_and_human_gates() -> None:
    result = MODULE.RUNNERS["IRIS-EXP-08"]()
    readiness_checks = {check.name: check for check in result.readiness_checks}
    readiness_names = set(readiness_checks)

    assert {
        "controlled PPTX, PDF, review workbook, and backup exist",
        "current package hashes and backup members match controlled artifacts",
        "verified render manifest binds the current package and all 21 inspected native slides",
        "visual QA is bound to the current PPTX/PDF hashes",
        "dated four-role live rehearsal is complete",
        "Iris and Arnon delivery/access tests pass",
    } <= readiness_names
    assert not readiness_checks[
        "current package hashes and backup members match controlled artifacts"
    ].passed
    assert not result.passed_for_mode("readiness")


def test_render_manifest_template_is_pending_and_verified_record_is_hash_bound() -> None:
    template = MODULE.read_json(MODULE.PRESENTATION_RENDER_TEMPLATE)
    record = MODULE.read_json(MODULE.PRESENTATION_RENDER_RECORD)

    assert MODULE.PRESENTATION_RENDER_SCHEMA.is_file()
    assert MODULE.render_manifest_structure_errors(
        template, require_verified=False
    ) == []
    assert template["status"] == "PENDING_FINAL_RENDER"
    assert record
    assert MODULE.render_manifest_structure_errors(record, require_verified=True) == []


def test_offline_backup_members_must_match_current_artifacts(tmp_path: Path) -> None:
    artifacts = tuple(
        tmp_path / name
        for name in ("package.pptx", "package.pdf", "review.xlsx")
    )
    for index, artifact in enumerate(artifacts):
        artifact.write_bytes(f"artifact-{index}".encode())
    backup = tmp_path / "backup.zip"
    with zipfile.ZipFile(backup, "w") as archive:
        for artifact in artifacts:
            archive.write(artifact, artifact.name)

    assert MODULE.backup_members_match(backup, artifacts)

    artifacts[0].write_bytes(b"corrected presentation")
    assert not MODULE.backup_members_match(backup, artifacts)


def test_submission_receipt_template_is_structured_pending_evidence() -> None:
    payload = MODULE.read_json(MODULE.SUBMISSION_RECEIPT_TEMPLATE)

    assert MODULE.SUBMISSION_RECEIPT_SCHEMA.is_file()
    assert MODULE.receipt_structure_errors(payload) == []
    assert payload["status"] == "NOT_SUBMITTED"
    assert payload["authorization"]["authorized"] is False
    assert not MODULE.SUBMISSION_RECEIPT_RECORD.exists()


def test_receipt_named_decoy_does_not_satisfy_exp10(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "fake-submission-receipt.md").write_text("not evidence")
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)
    monkeypatch.setattr(
        MODULE,
        "SUBMISSION_RECEIPT_RECORD",
        tmp_path / "docs/research/phd-proposal/authorized-submission-receipt.json",
    )

    checks = {check.name: check for check in MODULE.exp10().closure_checks}

    assert not checks["verified authorized submission receipt record exists"].passed


def test_verified_receipt_requires_and_accepts_all_hash_bindings(
    tmp_path: Path, monkeypatch
) -> None:
    docs = tmp_path / "docs/research/phd-proposal"
    docs.mkdir(parents=True)
    package = tmp_path / "submission/package.zip"
    external_receipt = tmp_path / "submission/official-receipt.pdf"
    authorization = tmp_path / "submission/authorization.txt"
    for path, content in (
        (package, b"submitted package"),
        (external_receipt, b"official receipt"),
        (authorization, b"authorized by accountable authority"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    package_hash = MODULE.sha256(package)
    receipt_hash = MODULE.sha256(external_receipt)
    authorization_hash = MODULE.sha256(authorization)
    receipt_id = "RECEIPT-TEST-001"
    certificate_id = "IRIS-CLOSE-20260801-v1.0"
    record_relative = "docs/research/phd-proposal/authorized-submission-receipt.json"
    certificate = docs / "iris-closure-certificate-template.md"
    certificate.write_text(
        "\n".join(
            (
                f"- Certificate ID when issued: `{certificate_id}`",
                "Certificate status: **ISSUED**",
                "Unresolved controls: **0**",
                "Human review: **COMPLETE**",
                "Supervisor acceptance: **CONFIRMED**",
                "Submission evidence: **VERIFIED**",
                record_relative,
                receipt_id,
                package_hash,
                receipt_hash,
            )
        ),
        encoding="utf-8",
    )
    certificate_hash = MODULE.sha256(certificate)
    record = tmp_path / record_relative
    record.write_text(
        json.dumps(
            {
                "schema_version": "IrisAuthorizedSubmissionReceipt-v1",
                "status": "VERIFIED",
                "submission": {
                    "route": "authorized university portal",
                    "submitted_at": "2026-08-01T14:00:00+03:00",
                    "receipt_id": receipt_id,
                    "submitted_by": "Ali Hamed",
                    "recipient_authority": "Graduate Studies",
                },
                "authorization": {
                    "authorized": True,
                    "authority": "Graduate Studies coordinator",
                    "authorized_at": "2026-08-01T13:30:00+03:00",
                    "evidence_path": "submission/authorization.txt",
                    "evidence_sha256": authorization_hash,
                },
                "package": {
                    "path": "submission/package.zip",
                    "sha256": package_hash,
                },
                "receipt_artifact": {
                    "path": "submission/official-receipt.pdf",
                    "sha256": receipt_hash,
                },
                "certificate_binding": {
                    "certificate_id": certificate_id,
                    "certificate_path": "docs/research/phd-proposal/iris-closure-certificate-template.md",
                    "certificate_sha256": certificate_hash,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(MODULE, "ROOT", tmp_path)
    monkeypatch.setattr(MODULE, "CLOSURE_CERTIFICATE", certificate)
    monkeypatch.setattr(MODULE, "SUBMISSION_RECEIPT_RECORD", record)

    receipt_checks = {
        check.name: check.passed
        for check in MODULE.exp10().closure_checks
        if "receipt" in check.name
        or "submission route" in check.name
        or "submitted package" in check.name
        or "authorization" in check.name
    }

    assert receipt_checks
    assert all(receipt_checks.values())
