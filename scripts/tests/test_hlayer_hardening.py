from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

import exp005_label_review as exp005
import exp007_dosage_replay as exp007
import exp008_trigger_mining as exp008
import exp009_seeded_conflict as exp009
import exp010_convergence_sweep as exp010
import exp012_accuracy_baseline as exp012
import hlayer_harness as harness
from hlayer_offline.legacy_replay_adapter import adapt_reconstructed_row, event_type_of


def protected_authorization_environment() -> dict[str, str]:
    """Provide the subprocess with an explicit test-only external trust root."""

    environment = os.environ.copy()
    authorization = REPO / "configs" / "protected-change-authorization-v1.json"
    portable_bytes = authorization.read_bytes().replace(b"\r\n", b"\n")
    environment["H_LAYER_AUTHORIZATION_SHA256"] = hashlib.sha256(
        portable_bytes
    ).hexdigest()
    return environment


def deferred_decision_snapshot() -> dict:
    decisions = [
        {
            "id": decision_id,
            "decision_complete": False,
            "accepted": False,
            "effective_outcome": "Deferred",
        }
        for decision_id in harness.DECISION_IDS
    ]
    payload = {
        "schema_version": "1.0",
        "decision_ids": list(harness.DECISION_IDS),
        "decisions": decisions,
        "program_mode": "offline_only",
        "snapshot_status": "deferred",
        "offline_only": True,
        "live_shadow_authorized": False,
        "authorization_blockers": ["decisions deferred"],
        "implementation_gate": {"offline_only": True},
        "authorization_record": None,
    }
    payload["snapshot_sha256"] = harness.stable_digest(payload)
    return payload


def live_decision_snapshot() -> dict:
    payload = deferred_decision_snapshot()
    for decision in payload["decisions"]:
        if decision["id"] in {"M-02", "M-03", "M-04", "M-05"}:
            decision.update(decision_complete=True, accepted=True, effective_outcome="Accepted")
    payload.update(
        {
            "program_mode": "live_shadow_authorized",
            "snapshot_status": "complete",
            "offline_only": False,
            "live_shadow_authorized": True,
            "authorization_blockers": [],
            "implementation_gate": {"offline_only": False},
            "authorization_record": {
                "allowed_touch_outcome": "Accepted",
                "implementation_outcome": "Accepted",
                "allowed_touches": sorted(harness.EXPECTED_AUTHORIZED_TOUCHES),
                "approver": "supervisor",
                "approved_at": "2026-07-15T12:00:00+00:00",
            },
        }
    )
    payload["snapshot_sha256"] = harness.stable_digest(
        {key: value for key, value in payload.items() if key != "snapshot_sha256"}
    )
    return payload


def write_child_manifest(root: Path, name: str = "exp006", *, run_id: str = "test-run") -> Path:
    child = root / name
    child.mkdir(parents=True)
    outputs = []
    for filename in sorted(harness.REQUIRED_EXPERIMENT_OUTPUTS[name]):
        path = child / filename
        path.write_text(f"{name}:{filename}\n", encoding="utf-8")
        outputs.append(
            {
                "path": f"reports/generated/{name}/{filename}",
                "sha256": harness.sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": "volatile",
        "experiment_id": f"EXP-{name[3:]}",
        "experiment_version": "1.0",
        "config_version": "fixture-1.0",
        "outputs": outputs,
    }
    manifest["normalized_sha256"] = harness.normalized_manifest_digest(manifest)
    path = child / "manifest.json"
    harness.write_json(path, manifest)
    return path


def write_complete_suite_fixture(root: Path, *, run_id: str = "test-run") -> dict[str, Path]:
    return {
        name: write_child_manifest(root, name, run_id=run_id)
        for name in harness.REQUIRED_EXPERIMENT_OUTPUTS
    }


def write_zero_label_gate(root: Path) -> Path:
    """Create an unlabeled synthetic interface fixture, never expert evidence."""
    gate = root / "exp005-zero-label-fixture"
    gate.mkdir(parents=True)
    fields = [
        "setting",
        "pattern_id",
        "pattern_description",
        "original_agent4_classification",
        "memory_informed_classification",
        "generalization_safe_candidate",
        "evaluation_leakage_status",
        "expert_label",
        "expert_rationale",
        "reviewer_id",
        "review_date",
        "confidence",
    ]
    row = {
        "setting": "fixture_setting",
        "pattern_id": "SYNTHETIC_TEST_FIXTURE_P1",
        "pattern_description": "Synthetic mechanism fixture; not expert evidence.",
        "original_agent4_classification": "Occasional Variability",
        "memory_informed_classification": "Occasional Variability",
        "generalization_safe_candidate": "True",
        "evaluation_leakage_status": "none",
        "expert_label": "",
        "expert_rationale": "",
        "reviewer_id": "",
        "review_date": "",
        "confidence": "",
    }
    rows_path = gate / "exp005_label_review_full.csv"
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)
    summary, errors = exp005.summarize_labels([row])
    assert not errors
    summary["generated_at"] = "2026-07-25T00:00:00+00:00"
    harness.write_json(gate / "label_validation_summary.json", summary)
    return gate


def write_replay_inputs(root: Path) -> tuple[Path, Path]:
    """Create minimal four-setting replay inputs for clone-safe integration tests."""
    eval_root = root / "eval-output-fixture"
    run_root = root / "run-human-fixture"
    for setting in ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw"):
        setting_dir = eval_root / setting
        setting_dir.mkdir(parents=True)
        harness.write_json(
            setting_dir / "agentA_run1_template_fixture.json",
            {"guidelines": [{"id": "T1", "description": "initial"}]},
        )
        harness.write_json(
            setting_dir / "agentA_run2_template_fixture.json",
            {"guidelines": [{"id": "T1", "description": "revised"}]},
        )
        harness.write_json(
            setting_dir / "agentB_run1_guidelines_fixture.json",
            {
                "reference_guidelines": [
                    {
                        "id": "G1",
                        "guideline_name": "fixture one",
                        "description": "initial",
                        "mapping_certainty": 0.9,
                    }
                ]
            },
        )
        revised_guidelines = {
            "reference_guidelines": [
                {
                    "id": "G1",
                    "guideline_name": "fixture one",
                    "description": "revised",
                    "mapping_certainty": 0.8,
                },
                {
                    "id": "G2",
                    "guideline_name": "fixture two",
                    "description": "added",
                    "mapping_certainty": 0.6,
                },
            ],
            "questions_to_language_advisor": [{"id": "Q1", "related_template_ids": ["T1"]}],
        }
        harness.write_json(
            setting_dir / "agentB_run2_guidelines_fixture.json",
            revised_guidelines,
        )
        harness.write_json(
            setting_dir / "agentB_best_guidelines_fixture.json",
            revised_guidelines,
        )
        harness.write_json(
            setting_dir / "agentC_case_1_fixture.json",
            {
                "case_id": "1",
                "uncovered_fragments": ["fixture-uncovered"],
                "potential_found": ["fixture-potential"],
            },
        )
        harness.write_json(
            setting_dir / "agentD_deviation_patterns_fixture.json",
            {
                "recurring_fragment_patterns": [{"id": "P1"}],
                "recurring_guideline_patterns": [],
            },
        )
        harness.write_json(
            setting_dir / "agentD_variability_classes_fixture.json",
            {
                "variability_classifications": [
                    {
                        "pattern_id": "P1",
                        "classification": "Occasional Variability",
                        "confidence": "Medium",
                        "requires_human_review": True,
                        "flag_for_guidelines_update": False,
                    }
                ],
                "questions_to_domain_advisor": [{"id": "QD1"}],
                "questions_to_language_advisor": [],
            },
        )
        queue_dir = run_root / setting
        queue_dir.mkdir(parents=True)
        (queue_dir / "human_review_queue.jsonl").write_text(
            json.dumps(
                {
                    "review_id": f"fixture-{setting}",
                    "related_guideline_id": "G1",
                    "fixture_classification": "SYNTHETIC_NOT_EXPERT_EVIDENCE",
                }
            )
            + "\n",
            encoding="utf-8",
        )
    return eval_root, run_root


@pytest.fixture(scope="module", autouse=True)
def clone_safe_hlayer_inputs() -> None:
    """Bind the whole module to explicit synthetic fixtures in every clone."""
    generated = REPO / "reports" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".clone-safe-inputs-", dir=generated) as temp:
        root = Path(temp)
        gate = write_zero_label_gate(root)
        eval_root, run_root = write_replay_inputs(root)
        updates = {
            "HLAYER_EXP005_DIR": str(gate),
            "HLAYER_EVAL_OUTPUT_ROOT": str(eval_root),
            "HLAYER_RUN_HUMAN_ROOT": str(run_root),
        }
        previous = {key: os.environ.get(key) for key in updates}
        os.environ.update(updates)
        try:
            yield
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class AtomicPromotionTests(unittest.TestCase):
    def test_normalize_manifest_accepts_windows_powershell_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            path = Path(temp) / "iteration_manifest.json"
            payload = {"schema_version": "1.0", "run_id": "bom-fixture"}
            path.write_text(json.dumps(payload), encoding="utf-8-sig")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "hlayer_harness.py"),
                    "normalize-manifest",
                    "--input",
                    str(path),
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            normalized = json.loads(path.read_text(encoding="utf-8"))
            self.assertRegex(normalized["normalized_sha256"], r"^[0-9a-f]{64}$")

    def test_experiment_manifest_records_explicit_experiment_and_config_versions(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            output = Path(temp)
            result = output / "summary.json"
            result.write_text("{}\n", encoding="utf-8")
            manifest = harness.write_experiment_manifest(
                output,
                experiment_id="EXP-TEST",
                experiment_version="9.1",
                config_version="fixture-3",
                claim_scope="mechanism test only",
                script_path=Path(__file__),
                inputs=[Path(__file__)],
                outputs=[result],
                config={},
                metric_schema={},
            )
            self.assertEqual(manifest["experiment_version"], "9.1")
            self.assertEqual(manifest["config_version"], "fixture-3")
            self.assertRegex(manifest["normalized_sha256"], r"^[0-9a-f]{64}$")

    def test_normalized_manifest_digest_excludes_only_run_identity_time(self) -> None:
        first = {
            "run_id": "run-a",
            "generated_at": "2026-01-01T00:00:00Z",
            "inputs": [{"path": "input", "sha256": "abc"}],
            "outputs": [{"path": "output", "sha256": "def"}],
        }
        second = dict(first, run_id="run-b", generated_at="2026-01-02T00:00:00Z")
        self.assertEqual(
            harness.normalized_manifest_digest(first), harness.normalized_manifest_digest(second)
        )
        changed = dict(second, outputs=[{"path": "output", "sha256": "changed"}])
        self.assertNotEqual(
            harness.normalized_manifest_digest(first), harness.normalized_manifest_digest(changed)
        )

    def test_promotion_rolls_back_every_target_after_mid_commit_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            root = Path(temp)
            stage = root / "stage"
            target = root / "target"
            (stage / "exp006").mkdir(parents=True)
            (stage / "exp006" / "value.txt").write_text("new-dir", encoding="utf-8")
            (stage / "suite.json").write_text("new-file", encoding="utf-8")
            (target / "exp006").mkdir(parents=True)
            (target / "exp006" / "value.txt").write_text("old-dir", encoding="utf-8")
            (target / "suite.json").write_text("old-file", encoding="utf-8")

            real_replace = os.replace
            calls = 0

            def fail_once(source, destination):
                nonlocal calls
                calls += 1
                # Two stage->incoming moves, two old->backup moves, then first
                # incoming->target succeeds; fail the second promotion.
                if calls == 6:
                    raise OSError("injected promotion failure")
                return real_replace(source, destination)

            with mock.patch("hlayer_harness.os.replace", side_effect=fail_once):
                with self.assertRaises(harness.HarnessError):
                    harness.atomic_promote(stage, target, ["exp006"], ["suite.json"])

            self.assertEqual(
                (target / "exp006" / "value.txt").read_text(encoding="utf-8"), "old-dir"
            )
            self.assertEqual((target / "suite.json").read_text(encoding="utf-8"), "old-file")

    def test_success_replaces_directory_instead_of_retaining_stale_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            root = Path(temp)
            stage = root / "stage"
            target = root / "target"
            (stage / "exp006").mkdir(parents=True)
            (stage / "exp006" / "fresh.txt").write_text("fresh", encoding="utf-8")
            (stage / "suite.json").write_text("fresh", encoding="utf-8")
            (target / "exp006").mkdir(parents=True)
            (target / "exp006" / "stale.txt").write_text("stale", encoding="utf-8")
            (target / "suite.json").write_text("stale", encoding="utf-8")
            harness.atomic_promote(stage, target, ["exp006"], ["suite.json"])
            self.assertFalse((target / "exp006" / "stale.txt").exists())
            self.assertEqual((target / "exp006" / "fresh.txt").read_text(encoding="utf-8"), "fresh")


class ManifestIntegrityTests(unittest.TestCase):
    def test_live_authorization_requires_exact_five_path_touch_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "decision_snapshot.json"
            payload = live_decision_snapshot()
            harness.write_json(path, payload)
            with mock.patch.dict(os.environ, {"HLAYER_DECISION_SNAPSHOT": str(path)}):
                self.assertFalse(harness.decision_snapshot()["offline_only"])
                payload["authorization_record"]["allowed_touches"].append(
                    "VEGO-AI/framework/extra.py"
                )
                payload["snapshot_sha256"] = harness.stable_digest(
                    {key: value for key, value in payload.items() if key != "snapshot_sha256"}
                )
                harness.write_json(path, payload)
                with self.assertRaisesRegex(
                    harness.HarnessError, "authorization flags are inconsistent"
                ):
                    harness.decision_snapshot()

    def test_decision_snapshot_rejects_tampering_even_with_recomputed_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "decision_snapshot.json"
            payload = deferred_decision_snapshot()
            harness.write_json(path, payload)
            with mock.patch.dict(os.environ, {"HLAYER_DECISION_SNAPSHOT": str(path)}):
                self.assertTrue(harness.decision_snapshot()["offline_only"])

                tampered = dict(payload, offline_only=False)
                harness.write_json(path, tampered)
                with self.assertRaisesRegex(harness.HarnessError, "hash mismatch"):
                    harness.decision_snapshot()

                tampered["snapshot_sha256"] = harness.stable_digest(
                    {key: value for key, value in tampered.items() if key != "snapshot_sha256"}
                )
                harness.write_json(path, tampered)
                with self.assertRaisesRegex(
                    harness.HarnessError, "authorization flags are inconsistent"
                ):
                    harness.decision_snapshot()

    def test_decision_snapshot_rejects_schema_or_decision_id_drift(self) -> None:
        for mutation in ("schema", "ids"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "decision_snapshot.json"
                payload = deferred_decision_snapshot()
                if mutation == "schema":
                    payload["schema_version"] = "2.0"
                else:
                    payload["decision_ids"] = list(harness.DECISION_IDS[:-1])
                payload["snapshot_sha256"] = harness.stable_digest(
                    {key: value for key, value in payload.items() if key != "snapshot_sha256"}
                )
                harness.write_json(path, payload)
                with mock.patch.dict(os.environ, {"HLAYER_DECISION_SNAPSHOT": str(path)}):
                    with self.assertRaises(harness.HarnessError):
                        harness.decision_snapshot()

    def test_suite_manifest_recomputes_child_digest_and_output_hashes(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            root = Path(temp)
            manifest_path = write_complete_suite_fixture(root)["exp006"]
            destination = root / "suite.json"
            with mock.patch.dict(
                os.environ,
                {"HLAYER_OUTPUT_ROOT": str(root), "HLAYER_RUN_ID": "test-run"},
            ):
                result = harness.write_suite_manifest(
                    root, list(harness.REQUIRED_EXPERIMENT_OUTPUTS), destination
                )
                self.assertRegex(result["normalized_sha256"], r"^[0-9a-f]{64}$")

                child = json.loads(manifest_path.read_text(encoding="utf-8"))
                child["normalized_sha256"] = "0" * 64
                harness.write_json(manifest_path, child)
                with self.assertRaisesRegex(harness.HarnessError, "normalized manifest mismatch"):
                    harness.write_suite_manifest(
                        root, list(harness.REQUIRED_EXPERIMENT_OUTPUTS), destination
                    )

    def test_suite_manifest_rejects_forged_or_partial_output_sets(self) -> None:
        for mutation in ("forged_hash", "partial", "path_escape"):
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp,
            ):
                root = Path(temp)
                manifest_path = write_complete_suite_fixture(root)["exp006"]
                child = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mutation == "forged_hash":
                    child["outputs"][0]["sha256"] = "f" * 64
                elif mutation == "partial":
                    child["outputs"].pop()
                else:
                    child["outputs"][0]["path"] = "reports/generated/exp006/../escape.json"
                child["normalized_sha256"] = harness.normalized_manifest_digest(child)
                harness.write_json(manifest_path, child)
                with mock.patch.dict(
                    os.environ,
                    {"HLAYER_OUTPUT_ROOT": str(root), "HLAYER_RUN_ID": "test-run"},
                ):
                    with self.assertRaises(harness.HarnessError):
                        harness.write_suite_manifest(
                            root, list(harness.REQUIRED_EXPERIMENT_OUTPUTS), root / "suite.json"
                        )

    def test_suite_manifest_rejects_missing_experiment(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            root = Path(temp)
            write_complete_suite_fixture(root)
            with mock.patch.dict(
                os.environ,
                {"HLAYER_OUTPUT_ROOT": str(root), "HLAYER_RUN_ID": "test-run"},
            ):
                with self.assertRaisesRegex(harness.HarnessError, "must contain exactly"):
                    harness.write_suite_manifest(
                        root, list(harness.REQUIRED_EXPERIMENT_OUTPUTS)[:-1], root / "suite.json"
                    )

    def test_exp005_gate_rejects_tampered_gate_and_reliability_sections(self) -> None:
        source = Path(os.environ["HLAYER_EXP005_DIR"])
        for section in ("strict_gate", "reviewer_reliability"):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as temp:
                target = Path(temp)
                shutil.copy2(
                    source / "exp005_label_review_full.csv", target / "exp005_label_review_full.csv"
                )
                summary = json.loads(
                    (source / "label_validation_summary.json").read_text(encoding="utf-8")
                )
                summary[section] = {"tampered": True}
                harness.write_json(target / "label_validation_summary.json", summary)
                with mock.patch.dict(os.environ, {"HLAYER_EXP005_DIR": str(target)}):
                    with self.assertRaisesRegex(harness.HarnessError, section):
                        harness.load_exp005_gate()


class DeterminismAndWorkloadTests(unittest.TestCase):
    def test_legacy_event_adapter_validates_observation_contract(self) -> None:
        row = {
            "event_id": "OBS-fixture",
            "event": "E2_question_from_B",
            "setting": "cd_ch",
            "sequence": "1",
            "producer": "Agent B",
            "channel": "offline_artifact_replay",
            "capture_status": "reconstructed",
            "subject_id": "question:B:Q1",
            "severity": "2",
            "uncertainty": "1",
            "detail": "Q1",
            "source_artifact": "fixture.json",
            "source_sha256": "0" * 64,
        }
        record = adapt_reconstructed_row(row, run_id="fixture-run")
        self.assertEqual(record.event_type, "E2")
        self.assertEqual(record.payload["subject_id"], "question:B:Q1")
        self.assertEqual(event_type_of("E15_evaluation"), "E15")

    def test_numeric_case_and_guideline_ties_are_deterministic(self) -> None:
        self.assertEqual(sorted(["10", "2", "1"], key=exp007.natural_key), ["1", "2", "10"])
        tied = {
            "G10": {"instability": 2, "revisions": 1, "added_late": 1, "removed": 0},
            "G2": {"instability": 2, "revisions": 1, "added_late": 1, "removed": 0},
        }
        ranked = sorted(tied, key=lambda item: exp008.rank_key(item, tied[item]))
        self.assertEqual(ranked, ["G2", "G10"])

    def test_bundling_uses_fixed_denominator_and_never_crosses_setting(self) -> None:
        events = [
            {"setting": "a", "subject_id": "case:2", "event": "E6_inspector_uncertainty", "sev": 2},
            {"setting": "a", "subject_id": "case:2", "event": "E13_agent4_signals", "sev": 3},
            {"setting": "b", "subject_id": "case:2", "event": "E6_inspector_uncertainty", "sev": 2},
        ]
        result = exp007.metrics(events, events)
        self.assertEqual(result["triageable_event_total"], 3)
        self.assertEqual(result["review_transactions"], 2)
        self.assertEqual(result["review_transaction_load_vs_every_decision_events"], 0.667)
        self.assertEqual(result["bundling_reduction_vs_unbundled_selected"], 0.333)
        self.assertEqual(result["severity_mass_total_unique_subject_max"], 5)

    def test_question_threads_from_different_producers_never_bundle(self) -> None:
        events = [
            {
                "setting": "cd_ch",
                "subject_id": "question:B:Q1",
                "event": "E2_question_from_B",
                "sev": 2,
            },
            {
                "setting": "cd_ch",
                "subject_id": "question:D:Q1",
                "event": "E2_question_from_D",
                "sev": 2,
            },
        ]
        result = exp007.metrics(events, events)
        self.assertEqual(result["review_transactions"], 2)
        self.assertEqual(result["bundling_reduction_vs_unbundled_selected"], 0.0)

    def test_pareto_frontier_reports_tradeoff_without_selecting_default(self) -> None:
        rows = [
            {
                "mode": "a",
                "event_load_vs_every_decision": 1.0,
                "review_transaction_load_vs_every_decision_events": 1.0,
                "weighted_severity_coverage": 1.0,
                "high_severity_coverage": 1.0,
            },
            {
                "mode": "b",
                "event_load_vs_every_decision": 0.8,
                "review_transaction_load_vs_every_decision_events": 0.7,
                "weighted_severity_coverage": 0.98,
                "high_severity_coverage": 1.0,
            },
            {
                "mode": "dominated",
                "event_load_vs_every_decision": 0.9,
                "review_transaction_load_vs_every_decision_events": 0.8,
                "weighted_severity_coverage": 0.9,
                "high_severity_coverage": 0.8,
            },
            {
                "mode": "silent",
                "event_load_vs_every_decision": 0.0,
                "review_transaction_load_vs_every_decision_events": 0.0,
                "weighted_severity_coverage": 0.0,
                "high_severity_coverage": 0.0,
            },
        ]
        frontier = exp007.pareto_frontier(rows)
        self.assertEqual([row["mode"] for row in frontier], ["silent", "b", "a"])


class SyntheticTraceTests(unittest.TestCase):
    def test_exp009_is_balanced_and_overrides_remain_pending(self) -> None:
        fixture = exp009.load_fixture()
        records = exp009.run_simulation(fixture)
        metrics = exp009.metric_summary(records)
        self.assertEqual(
            metrics["synthetic_conflict_cases"], metrics["synthetic_non_conflict_cases"]
        )
        self.assertEqual(metrics["false_positives"], 0)
        self.assertEqual(metrics["false_negatives"], 0)
        override_states = {
            record["final_status"] for record in records if record["id"] in {"SEED_01", "SEED_04"}
        }
        self.assertEqual(override_states, {"escalated_pending_adjudication"})
        self.assertTrue(all(not record["trusted_memory_write"] for record in records))

    def test_exp010_consumes_exp009_trace_outcomes_without_combining_adjudication(self) -> None:
        records = exp009.run_simulation(exp009.load_fixture())
        bound_one = exp010.simulate_for_bound(records, 1)
        bound_two = exp010.simulate_for_bound(records, 2)
        self.assertGreater(bound_one["timed_out_parked"], 0)
        self.assertGreater(bound_two["needs_adjudication"], 0)
        self.assertNotIn("convergence_rate", bound_two)


class Exp012BoundaryTests(unittest.TestCase):
    @staticmethod
    def valid_row(leakage: str, safe: str = "True", pattern: str = "P1") -> dict[str, str]:
        return {
            "setting": "cd_ch",
            "pattern_id": pattern,
            "expert_label": "Substantial Variability",
            "expert_rationale": "Independent review rationale",
            "reviewer_id": "reviewer-1",
            "review_date": "2026-07-10",
            "confidence": "High",
            "reviewer_confidence": "",
            "adjudicated_label": "",
            "original_agent4_classification": "Substantial Variability",
            "memory_informed_classification": "Occasional Variability",
            "generalization_safe_candidate": safe,
            "evaluation_leakage_status": leakage,
        }

    def test_blank_unknown_and_non_allowlisted_leakage_are_excluded(self) -> None:
        rows = [
            self.valid_row("none", pattern="P1"),
            self.valid_row("cross_setting_memory_used", pattern="P2"),
            self.valid_row("", pattern="P3"),
            self.valid_row("unknown", pattern="P4"),
            self.valid_row("same_setting_memory_used", pattern="P5"),
            self.valid_row("same_pattern_memory_used", pattern="P6"),
            self.valid_row("none", safe="", pattern="P7"),
        ]
        safe, same_pattern, excluded = exp012.partition_validated_rows(rows)
        self.assertEqual([row["pattern_id"] for row in safe], ["P1", "P2"])
        self.assertEqual([row["pattern_id"] for row in same_pattern], ["P6"])
        self.assertEqual(excluded["leakage_not_allowlisted:blank"], 1)
        self.assertEqual(excluded["leakage_not_allowlisted:unknown"], 1)
        self.assertEqual(excluded["leakage_not_allowlisted:same_setting_memory_used"], 1)

    def test_zero_pilot_and_quantitative_gate_bands(self) -> None:
        self.assertEqual(exp012.gate_band(0)["band"], "blocked_zero_labels")
        self.assertEqual(exp012.gate_band(1)["band"], "pilot_only")
        self.assertEqual(exp012.gate_band(19)["band"], "pilot_only")
        self.assertEqual(exp012.gate_band(20)["band"], "quantitative_baseline_available")

    def test_nonzero_fixture_matches_canonical_exp003_evaluator(self) -> None:
        first = self.valid_row("none", pattern="P1")
        second = self.valid_row("cross_setting_memory_used", pattern="P2")
        second["expert_label"] = "Occasional Variability"
        second["original_agent4_classification"] = "Substantial Variability"
        second["memory_informed_classification"] = "Occasional Variability"
        rows = [first, second]
        local = exp012.metric_pack(rows)
        result = exp012.canonical_cross_check(rows, local)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["canonical_metrics"]["rows"], 2)
        self.assertEqual(local["original_accuracy"], 0.5)
        self.assertEqual(local["memory_informed_accuracy"], 0.5)


@pytest.mark.slow  # full-suite subprocess replays (~1min); deselect with -m "not slow"
class EvidenceGuardIntegrationTests(unittest.TestCase):
    def test_second_protected_path_guard_failure_prevents_promotion(self) -> None:
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            self.skipTest("PowerShell is not available")
        with (
            tempfile.TemporaryDirectory() as output_temp,
            tempfile.TemporaryDirectory() as counter_temp,
        ):
            generated = Path(output_temp) / "generated"
            targets = [
                generated / "exp006" / "summary.json",
                generated / "hlayer_suite_manifest.json",
            ]
            before = {
                path: harness.sha256_file(path) if path.is_file() else None for path in targets
            }
            env = os.environ.copy()
            env["HLAYER_TEST_GUARD_COUNTER"] = str(Path(counter_temp) / "counter.txt")
            proc = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-File",
                    str(SCRIPTS / "build-hlayer-experiments.ps1"),
                    "-GeneratedOutputRoot",
                    str(generated),
                    "-ProtectedPathGuardScript",
                    str(SCRIPTS / "tests" / "fixtures" / "pass_then_fail_protected_guard.py"),
                ],
                cwd=REPO,
                env=env,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=180,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertRegex(
                proc.stdout + proc.stderr,
                r"rechecking protected-path hashes before promotion",
            )
            after = {
                path: harness.sha256_file(path) if path.is_file() else None for path in targets
            }
            self.assertEqual(
                before,
                after,
                "failed pre-promotion protected guard changed canonical outputs",
            )
            self.assertFalse(list(generated.glob(".hlayer-stage-*")))

    def test_three_identical_replays_have_identical_metrics_and_normalized_manifests(self) -> None:
        experiment_scripts = [
            ("exp006", "exp006_event_replay.py"),
            ("exp007", "exp007_dosage_replay.py"),
            ("exp008", "exp008_trigger_mining.py"),
            ("exp009", "exp009_seeded_conflict.py"),
            ("exp010", "exp010_convergence_sweep.py"),
            ("exp012", "exp012_accuracy_baseline.py"),
        ]
        observations = []
        with tempfile.TemporaryDirectory(dir=REPO / "reports" / "generated") as temp:
            for replay in range(3):
                root = Path(temp) / f"replay-{replay}"
                env = os.environ.copy()
                env["HLAYER_OUTPUT_ROOT"] = str(root)
                env["HLAYER_RUN_ID"] = f"volatile-run-{replay}"
                env["HLAYER_GENERATED_AT"] = f"2026-07-1{replay}T00:00:00+00:00"
                for _, script in experiment_scripts:
                    proc = subprocess.run(
                        [sys.executable, str(SCRIPTS / script)],
                        cwd=REPO,
                        env=env,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        capture_output=True,
                        timeout=120,
                    )
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                observations.append(
                    {
                        experiment: {
                            "summary": harness.sha256_file(root / experiment / "summary.json"),
                            "manifest": json.loads(
                                (root / experiment / "manifest.json").read_text(encoding="utf-8")
                            )["normalized_sha256"],
                        }
                        for experiment, _ in experiment_scripts
                    }
                )
        self.assertEqual(observations[0], observations[1])
        self.assertEqual(observations[1], observations[2])

    def test_failed_exp007_cannot_promote_or_mix_old_exp008_exp009(self) -> None:
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as output_temp:
            generated = Path(output_temp) / "generated"
            targets = [
                generated / experiment / "summary.json"
                for experiment in ("exp006", "exp007", "exp008", "exp009")
            ]
            before = {
                path: harness.sha256_file(path) if path.is_file() else None for path in targets
            }
            proc = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-File",
                    str(SCRIPTS / "build-hlayer-experiments.ps1"),
                    "-GeneratedOutputRoot",
                    str(generated),
                    "-TestFailExperiment",
                    "exp007",
                ],
                cwd=REPO,
                env=protected_authorization_environment(),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=180,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            combined = proc.stdout + proc.stderr
            without_ansi = re.sub(r"\x1b\[[0-9;]*m", "", combined)
            normalized = " ".join(without_ansi.split())
            self.assertIn("Injected test-only failure after", normalized)
            self.assertIn("exp007", normalized)
            after = {
                path: harness.sha256_file(path) if path.is_file() else None for path in targets
            }
            self.assertEqual(
                before,
                after,
                "failed EXP-007 changed or mixed canonical outputs",
            )
            self.assertFalse(list(generated.glob(".hlayer-stage-*")))

    def test_nonzero_evidence_guard_prevents_promotion(self) -> None:
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as output_temp:
            generated = Path(output_temp) / "generated"
            tracked_targets = [
                generated / "exp006" / "summary.json",
                generated / "hlayer_suite_manifest.json",
            ]
            before = {
                path: harness.sha256_file(path) if path.is_file() else None
                for path in tracked_targets
            }
            proc = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-File",
                    str(SCRIPTS / "build-hlayer-experiments.ps1"),
                    "-GeneratedOutputRoot",
                    str(generated),
                    "-EvidenceGuardScript",
                    str(SCRIPTS / "tests" / "fixtures" / "failing_evidence_guard.py"),
                ],
                cwd=REPO,
                env=protected_authorization_environment(),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=180,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            after = {
                path: harness.sha256_file(path) if path.is_file() else None
                for path in tracked_targets
            }
            self.assertEqual(
                before,
                after,
                "nonzero evidence guard promoted staged outputs",
            )
            self.assertFalse(list(generated.glob(".hlayer-stage-*")))


if __name__ == "__main__":
    unittest.main()
