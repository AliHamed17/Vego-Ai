"""Validated, append-only experiment run storage for the VEGO-AI BigUI.

Tracked accepted-run bundles are privacy-safe projections.  The ignored SQLite
database is only an index and can always be rebuilt from those JSON bundles.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BundleValidationError(ValueError):
    """Raised when a run bundle is invalid or internally inconsistent."""


class BundleValidator:
    """Validate bundle records against the repository schemas."""

    SCHEMA_FILES = (
        "accepted-experiment-run-bundle-v1.schema.json",
        "experiment-run-envelope-v2.schema.json",
        "experiment-evaluation-v1.schema.json",
        "metric-definition-v1.schema.json",
        "metric-observation-v2.schema.json",
        "run-acceptance-record-v1.schema.json",
    )

    def __init__(self, schema_root: Path) -> None:
        self.schema_root = schema_root
        self.schemas = {
            name: json.loads((schema_root / name).read_text(encoding="utf-8"))
            for name in self.SCHEMA_FILES
        }
        root_schema = self.schemas[
            "accepted-experiment-run-bundle-v1.schema.json"
        ]
        registry = Registry().with_resources(
            [
                (schema["$id"], Resource.from_contents(schema))
                for schema in self.schemas.values()
            ]
        )
        self.validator = jsonschema.Draft202012Validator(
            root_schema,
            registry=registry,
            format_checker=jsonschema.FormatChecker(),
        )

    def validate(self, bundle: Mapping[str, Any]) -> None:
        errors = sorted(
            self.validator.iter_errors(bundle),
            key=lambda item: tuple(str(part) for part in item.absolute_path),
        )
        if errors:
            details = "; ".join(
                f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
                f"{error.message}"
                for error in errors[:8]
            )
            raise BundleValidationError(details)

        envelope = bundle["envelope"]
        acceptance = bundle["acceptance"]
        experiment_id = envelope["experimentId"]
        run_id = envelope["runId"]
        if acceptance["experimentId"] != experiment_id:
            raise BundleValidationError("acceptance experimentId does not match")
        if acceptance["runId"] != run_id:
            raise BundleValidationError("acceptance runId does not match")
        if acceptance["status"] != envelope["acceptanceStatus"]:
            raise BundleValidationError("acceptance status does not match envelope")

        definitions = {
            item["metricId"]: item for item in bundle["metricDefinitions"]
        }
        if len(definitions) != len(bundle["metricDefinitions"]):
            raise BundleValidationError("metric definitions must be unique")
        observations = {
            item["observationId"]: item for item in bundle["metricObservations"]
        }
        if len(observations) != len(bundle["metricObservations"]):
            raise BundleValidationError("metric observations must be unique")
        if set(observations) != set(envelope["metricObservationIds"]):
            raise BundleValidationError(
                "envelope metricObservationIds do not match observations"
            )
        if set(definitions) != set(envelope["metricDefinitionHashes"]):
            raise BundleValidationError(
                "envelope metricDefinitionHashes do not match definitions"
            )
        for metric_id, definition in definitions.items():
            expected_hash = canonical_sha256(definition)
            if envelope["metricDefinitionHashes"][metric_id] != expected_hash:
                raise BundleValidationError(
                    f"metric definition hash mismatch for {metric_id}"
                )
        for observation in observations.values():
            if observation["experimentId"] != experiment_id:
                raise BundleValidationError(
                    "metric observation experimentId does not match envelope"
                )
            if observation["runId"] != run_id:
                raise BundleValidationError(
                    "metric observation runId does not match envelope"
                )
            definition = definitions.get(observation["metricId"])
            if definition is None:
                raise BundleValidationError(
                    f"missing metric definition {observation['metricId']}"
                )
            if observation["metricDefinitionSha256"] != canonical_sha256(definition):
                raise BundleValidationError(
                    f"observation definition hash mismatch for "
                    f"{observation['metricId']}"
                )
            if (
                observation["metricId"].startswith(("CLASSIFICATION_", "PAIRED_"))
                and observation["denominator"] == 0
                and observation["value"] is not None
            ):
                raise BundleValidationError(
                    f"{observation['metricId']} must be null at denominator zero"
                )


def load_bundles(
    accepted_root: Path,
    schema_root: Path,
) -> list[dict[str, Any]]:
    validator = BundleValidator(schema_root)
    if not accepted_root.is_dir():
        return []
    bundles: list[dict[str, Any]] = []
    seen_attempts: set[tuple[str, str, str]] = set()
    seen_observations: set[str] = set()
    for path in sorted(accepted_root.glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise BundleValidationError(f"{path.name} must contain an object")
        validator.validate(value)
        envelope = value["envelope"]
        identity = (
            envelope["experimentId"],
            envelope["runId"],
            envelope["attemptId"],
        )
        if identity in seen_attempts:
            raise BundleValidationError(f"duplicate run attempt {identity}")
        seen_attempts.add(identity)
        for observation in value["metricObservations"]:
            observation_id = observation["observationId"]
            if observation_id in seen_observations:
                raise BundleValidationError(
                    f"duplicate metric observation {observation_id}"
                )
            seen_observations.add(observation_id)
        value["_bundlePath"] = path.as_posix()
        value["_bundleSha256"] = file_sha256(path)
        bundles.append(value)
    return bundles


def run_store_summary(bundles: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    materialized = list(bundles)
    envelopes = [item["envelope"] for item in materialized]
    accepted = [
        item for item in envelopes if item["acceptanceStatus"] == "accepted"
    ]
    unique_runs = {
        (item["experimentId"], item["runId"]) for item in accepted
    }
    unique_run_ids = {item["runId"] for item in accepted}
    observations = [
        observation
        for bundle in materialized
        for observation in bundle["metricObservations"]
    ]
    return {
        "schemaVersion": "BigUIRunStoreSummary-v1",
        "bundleCount": len(materialized),
        "acceptedAttemptCount": len(accepted),
        "uniqueExperimentRunCount": len(unique_runs),
        "uniqueRunIdCount": len(unique_run_ids),
        "experimentsWithAcceptedRuns": len(
            {item["experimentId"] for item in accepted}
        ),
        "metricObservationCount": len(observations),
        "experimentIds": sorted({item["experimentId"] for item in accepted}),
    }


def rebuild_sqlite(
    bundles: Iterable[Mapping[str, Any]],
    output: Path,
) -> dict[str, Any]:
    """Rebuild the ignored SQLite index transactionally."""

    materialized = list(bundles)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.unlink(missing_ok=True)
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE run (
              experiment_id TEXT NOT NULL,
              run_id TEXT NOT NULL,
              attempt_id TEXT NOT NULL,
              execution_status TEXT NOT NULL,
              acceptance_status TEXT NOT NULL,
              evidence_class TEXT NOT NULL,
              started_at TEXT,
              completed_at TEXT,
              duration_ms REAL,
              manifest_path TEXT NOT NULL,
              manifest_sha256 TEXT NOT NULL,
              source_revision TEXT NOT NULL,
              envelope_json TEXT NOT NULL,
              PRIMARY KEY (experiment_id, run_id, attempt_id)
            );
            CREATE TABLE metric_definition (
              metric_id TEXT NOT NULL,
              definition_sha256 TEXT NOT NULL,
              definition_json TEXT NOT NULL,
              PRIMARY KEY (metric_id, definition_sha256)
            );
            CREATE TABLE metric_observation (
              observation_id TEXT PRIMARY KEY,
              experiment_id TEXT NOT NULL,
              run_id TEXT NOT NULL,
              attempt_id TEXT NOT NULL,
              metric_id TEXT NOT NULL,
              value_json TEXT NOT NULL,
              numerator REAL,
              denominator REAL,
              unit TEXT NOT NULL,
              evidence_class TEXT NOT NULL,
              observation_json TEXT NOT NULL,
              FOREIGN KEY (experiment_id, run_id, attempt_id)
                REFERENCES run (experiment_id, run_id, attempt_id)
            );
            CREATE TABLE artifact (
              experiment_id TEXT NOT NULL,
              run_id TEXT NOT NULL,
              attempt_id TEXT NOT NULL,
              artifact_ref TEXT NOT NULL,
              PRIMARY KEY (experiment_id, run_id, attempt_id, artifact_ref),
              FOREIGN KEY (experiment_id, run_id, attempt_id)
                REFERENCES run (experiment_id, run_id, attempt_id)
            );
            CREATE TABLE acceptance (
              experiment_id TEXT NOT NULL,
              run_id TEXT NOT NULL,
              attempt_id TEXT NOT NULL,
              status TEXT NOT NULL,
              acceptance_json TEXT NOT NULL,
              PRIMARY KEY (experiment_id, run_id, attempt_id),
              FOREIGN KEY (experiment_id, run_id, attempt_id)
                REFERENCES run (experiment_id, run_id, attempt_id)
            );
            CREATE TABLE refresh_history (
              refresh_sha256 TEXT PRIMARY KEY,
              bundle_count INTEGER NOT NULL,
              metric_count INTEGER NOT NULL
            );
            CREATE INDEX metric_by_run
              ON metric_observation (experiment_id, run_id, metric_id);
            """
        )
        for bundle in materialized:
            envelope = bundle["envelope"]
            identity = (
                envelope["experimentId"],
                envelope["runId"],
                envelope["attemptId"],
            )
            connection.execute(
                """
                INSERT INTO run VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    *identity,
                    envelope["executionStatus"],
                    envelope["acceptanceStatus"],
                    envelope["evidenceClass"],
                    envelope["startedAt"],
                    envelope["completedAt"],
                    envelope["durationMilliseconds"],
                    envelope["manifestPath"],
                    envelope["manifestSha256"],
                    envelope["sourceRevision"],
                    canonical_json(envelope),
                ),
            )
            for definition in bundle["metricDefinitions"]:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO metric_definition VALUES (?, ?, ?)
                    """,
                    (
                        definition["metricId"],
                        canonical_sha256(definition),
                        canonical_json(definition),
                    ),
                )
            for observation in bundle["metricObservations"]:
                connection.execute(
                    """
                    INSERT INTO metric_observation VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        observation["observationId"],
                        *identity,
                        observation["metricId"],
                        json.dumps(observation["value"], ensure_ascii=False),
                        observation["numerator"],
                        observation["denominator"],
                        observation["unit"],
                        observation["evidenceClass"],
                        canonical_json(observation),
                    ),
                )
            for artifact_ref in envelope["artifactRefs"]:
                connection.execute(
                    "INSERT INTO artifact VALUES (?, ?, ?, ?)",
                    (*identity, artifact_ref),
                )
            connection.execute(
                "INSERT INTO acceptance VALUES (?, ?, ?, ?, ?)",
                (
                    *identity,
                    bundle["acceptance"]["status"],
                    canonical_json(bundle["acceptance"]),
                ),
            )
        summary = run_store_summary(materialized)
        connection.execute(
            "INSERT INTO refresh_history VALUES (?, ?, ?)",
            (
                canonical_sha256(
                    [
                        {
                            "path": item.get("_bundlePath"),
                            "sha256": item.get("_bundleSha256"),
                        }
                        for item in materialized
                    ]
                ),
                summary["bundleCount"],
                summary["metricObservationCount"],
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        temporary.unlink(missing_ok=True)
        raise
    else:
        connection.close()
        os.replace(temporary, output)
    return summary
