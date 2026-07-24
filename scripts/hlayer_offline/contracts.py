"""Versioned data contracts for offline H-layer experiments.

The contracts are intentionally stricter than loose experiment dictionaries:
construction validates required lineage, enumerations, hashes, and safety
invariants.  They are not runtime APIs and do not import VEGO-AI modules.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Any, ClassVar

CONTRACT_SCHEMA_VERSION = "1.0"
EVENT_TYPES = frozenset(f"E{i}" for i in range(1, 16))
CAPTURE_STATUSES = frozenset({"observed", "reconstructed", "unobservable"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX16_RE = re.compile(r"^[0-9a-f]{16}$")
HRQ_RE = re.compile(r"^HRQ-.+-P[0-9]+$")


class ValidationError(ValueError):
    """Raised when an offline contract violates its declared schema."""


def canonical_json(value: Any) -> str:
    """Return stable JSON used for IDs, manifests, and replay comparisons."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_identifier(prefix: str, value: Any, length: int = 16) -> str:
    digest = sha256(canonical_json(value).encode("utf-8")).hexdigest()[:length]
    return f"{prefix}-{digest}"


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")


def _require_sha256(name: str, value: str) -> None:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ValidationError(f"{name} must be a lowercase 64-character SHA-256")


def _require_mapping(name: str, value: Mapping[str, Any], *, nonempty: bool = False) -> None:
    if not isinstance(value, Mapping) or (nonempty and not value):
        qualifier = "non-empty " if nonempty else ""
        raise ValidationError(f"{name} must be a {qualifier}mapping")


def _require_sequence(name: str, value: Sequence[Any], *, nonempty: bool = False) -> None:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError(f"{name} must be a sequence")
    if nonempty and not value:
        raise ValidationError(f"{name} must not be empty")


def _require_iso8601(name: str, value: str) -> None:
    _require_text(name, value)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{name} must be ISO-8601") from exc


class ContractMixin:
    contract_name: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["contract"] = self.contract_name
        return result


@dataclass(frozen=True)
class ObservationRecord(ContractMixin):
    """One observed, reconstructed, or explicitly unobservable E1-E15 event."""

    contract_name: ClassVar[str] = "ObservationRecord"
    observation_id: str
    event_type: str
    run_id: str
    setting_id: str
    producer: str
    channel: str
    sequence: int
    capture_status: str
    payload: Mapping[str, Any]
    case_id: str | None = None
    source_artifact: str | None = None
    source_sha256: str | None = None
    gap_reason: str | None = None
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("observation_id", "run_id", "setting_id", "producer", "channel"):
            _require_text(name, getattr(self, name))
        if self.event_type not in EVENT_TYPES:
            raise ValidationError(f"event_type must be E1-E15, got {self.event_type!r}")
        if self.capture_status not in CAPTURE_STATUSES:
            raise ValidationError(f"capture_status must be one of {sorted(CAPTURE_STATUSES)}")
        if not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValidationError("sequence must be a non-negative integer")
        _require_mapping("payload", self.payload)
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported ObservationRecord schema {self.schema_version!r}")
        if self.capture_status in {"observed", "reconstructed"}:
            _require_text("source_artifact", self.source_artifact or "")
            _require_sha256("source_sha256", self.source_sha256 or "")
            if self.gap_reason:
                raise ValidationError("captured observations cannot declare gap_reason")
        else:
            _require_text("gap_reason", self.gap_reason or "")
            if self.source_artifact is not None or self.source_sha256 is not None:
                raise ValidationError("unobservable events must not fabricate source lineage")


@dataclass(frozen=True)
class TriageDecision(ContractMixin):
    contract_name: ClassVar[str] = "TriageDecision"
    triage_id: str
    observation_ids: tuple[str, ...]
    trigger_codes: tuple[str, ...]
    severity: int
    dosage_config: Mapping[str, Any]
    bundle_key: str
    budget_state: str
    outcome: str
    rationale: str
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("triage_id", self.triage_id)
        _require_sequence("observation_ids", self.observation_ids, nonempty=True)
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValidationError("observation_ids must be unique")
        _require_sequence("trigger_codes", self.trigger_codes)
        if not isinstance(self.severity, int) or not 0 <= self.severity <= 3:
            raise ValidationError("severity must be an integer from 0 through 3")
        _require_mapping("dosage_config", self.dosage_config, nonempty=True)
        _require_text("bundle_key", self.bundle_key)
        if self.budget_state not in {"within_budget", "capped", "deferred", "evaluation_only"}:
            raise ValidationError("invalid budget_state")
        if self.outcome not in {"promote", "park"}:
            raise ValidationError("outcome must be promote or park")
        _require_text("rationale", self.rationale)
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported TriageDecision schema {self.schema_version!r}")


@dataclass(frozen=True)
class ReviewItem(ContractMixin):
    contract_name: ClassVar[str] = "ReviewItem"
    review_id: str
    triage_id: str
    evidence_snapshot: Mapping[str, Any]
    question: str
    risk: str
    owner_role: str
    deduplication_key: str
    due_state: str
    provenance: Mapping[str, Any]
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("review_id", "triage_id", "question", "owner_role", "deduplication_key"):
            _require_text(name, getattr(self, name))
        _require_mapping("evidence_snapshot", self.evidence_snapshot, nonempty=True)
        _require_mapping("provenance", self.provenance, nonempty=True)
        if self.risk not in {"low", "medium", "high"}:
            raise ValidationError("risk must be low, medium, or high")
        if self.due_state not in {"pending", "due", "overdue", "parked"}:
            raise ValidationError("invalid due_state")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported ReviewItem schema {self.schema_version!r}")


@dataclass(frozen=True)
class FeedbackRecord(ContractMixin):
    """Feedback with an explicit crosswalk to the existing feedback schema."""

    contract_name: ClassVar[str] = "FeedbackRecord"
    feedback_id: str
    review_id: str
    review_signature: str
    expert_id: str
    timestamp: str
    human_decision: Mapping[str, Any]
    reusable: bool
    reuse_scope: Mapping[str, Any]
    evidence_refs: tuple[str, ...]
    rationale: str
    confidence: str
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("feedback_id", "review_id", "expert_id", "rationale"):
            _require_text(name, getattr(self, name))
        if not HRQ_RE.fullmatch(self.review_id):
            raise ValidationError("review_id must match the existing HRQ pattern ^HRQ-.+-P[0-9]+$")
        if not HEX16_RE.fullmatch(self.review_signature):
            raise ValidationError("review_signature must be 16 lowercase hex characters")
        _require_iso8601("timestamp", self.timestamp)
        _require_mapping("human_decision", self.human_decision, nonempty=True)
        _require_mapping("reuse_scope", self.reuse_scope)
        _require_sequence("evidence_refs", self.evidence_refs, nonempty=True)
        if self.confidence not in {"High", "Medium", "Low"}:
            raise ValidationError("confidence must be High, Medium, or Low")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported FeedbackRecord schema {self.schema_version!r}")

    def to_human_feedback_crosswalk(self) -> dict[str, Any]:
        """Return fields shared with ``human_feedback.schema.json``."""

        return {
            "feedback_id": self.feedback_id,
            "review_id": self.review_id,
            "review_signature": self.review_signature,
            "expert_id": self.expert_id,
            "timestamp": self.timestamp,
            "human_decision": dict(self.human_decision),
            "reusable": self.reusable,
            "reuse_scope": dict(self.reuse_scope),
            "notes": self.rationale,
        }


@dataclass(frozen=True)
class VerificationRecord(ContractMixin):
    contract_name: ClassVar[str] = "VerificationRecord"
    verification_id: str
    feedback_id: str
    deterministic_checks: tuple[str, ...]
    source_versions: Mapping[str, str]
    conflicts: tuple[str, ...]
    rounds: int
    outcome: str
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("verification_id", self.verification_id)
        _require_text("feedback_id", self.feedback_id)
        _require_sequence("deterministic_checks", self.deterministic_checks, nonempty=True)
        _require_mapping("source_versions", self.source_versions, nonempty=True)
        _require_sequence("conflicts", self.conflicts)
        if not isinstance(self.rounds, int) or self.rounds < 1:
            raise ValidationError("rounds must be a positive integer")
        if self.outcome not in {"verified", "revised", "needs_adjudication"}:
            raise ValidationError("invalid verification outcome")
        if self.outcome == "verified" and self.conflicts:
            raise ValidationError("verified records cannot retain conflicts")
        if self.outcome == "needs_adjudication" and not self.conflicts:
            raise ValidationError("needs_adjudication requires at least one conflict")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported VerificationRecord schema {self.schema_version!r}")


@dataclass(frozen=True)
class CorrectionProposal(ContractMixin):
    contract_name: ClassVar[str] = "CorrectionProposal"
    proposal_id: str
    verification_id: str
    target_artifact: str
    target_sha256: str
    proposed_diff: str
    evidence_refs: tuple[str, ...]
    rollback_description: str
    approval_state: str = "pending"
    applied: bool = False
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "verification_id",
            "target_artifact",
            "proposed_diff",
            "rollback_description",
        ):
            _require_text(name, getattr(self, name))
        _require_sha256("target_sha256", self.target_sha256)
        _require_sequence("evidence_refs", self.evidence_refs, nonempty=True)
        if self.approval_state not in {"pending", "approved", "rejected", "deferred"}:
            raise ValidationError("invalid approval_state")
        if self.applied:
            raise ValidationError("offline CorrectionProposal records can never be applied")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported CorrectionProposal schema {self.schema_version!r}")


@dataclass(frozen=True)
class MemoryRecord(ContractMixin):
    contract_name: ClassVar[str] = "MemoryRecord"
    memory_id: str
    verification_id: str
    source_outcome: str
    validity_scope: Mapping[str, Any]
    conflicts: tuple[str, ...]
    provenance: Mapping[str, Any]
    leakage_classification: str
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("memory_id", self.memory_id)
        _require_text("verification_id", self.verification_id)
        if self.source_outcome not in {"verified", "supervisor_adjudicated"}:
            raise ValidationError(
                "trusted memory requires verified or supervisor-adjudicated input"
            )
        _require_mapping("validity_scope", self.validity_scope, nonempty=True)
        _require_sequence("conflicts", self.conflicts)
        if self.conflicts:
            raise ValidationError("trusted memory cannot contain unresolved conflicts")
        _require_mapping("provenance", self.provenance, nonempty=True)
        if self.leakage_classification not in {
            "same_pattern",
            "cross_pattern",
            "unknown",
            "not_applicable",
        }:
            raise ValidationError("invalid leakage_classification")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(f"unsupported MemoryRecord schema {self.schema_version!r}")


@dataclass(frozen=True)
class ExperimentRunManifest(ContractMixin):
    contract_name: ClassVar[str] = "ExperimentRunManifest"
    experiment_id: str
    run_id: str
    experiment_version: str
    config_version: str
    decision_snapshot_sha256: str
    decision_snapshot_status: str
    decision_snapshot_source: str
    git_revision: str
    git_dirty: bool
    started_at: str
    completed_at: str
    input_hashes: Mapping[str, str]
    output_hashes: Mapping[str, str]
    metric_schema: Mapping[str, Any]
    claim_scope: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    runtime_versions: Mapping[str, str] = field(default_factory=dict)
    normalized_manifest_sha256: str = ""
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "experiment_id",
            "run_id",
            "experiment_version",
            "config_version",
            "decision_snapshot_source",
            "git_revision",
            "claim_scope",
        ):
            _require_text(name, getattr(self, name))
        _require_sha256("decision_snapshot_sha256", self.decision_snapshot_sha256)
        if self.decision_snapshot_status not in {"recorded_snapshot", "offline_fallback"}:
            raise ValidationError("invalid decision_snapshot_status")
        _require_iso8601("started_at", self.started_at)
        _require_iso8601("completed_at", self.completed_at)
        for mapping_name in ("input_hashes", "output_hashes"):
            mapping = getattr(self, mapping_name)
            _require_mapping(mapping_name, mapping, nonempty=True)
            for key, digest in mapping.items():
                _require_text(f"{mapping_name} key", key)
                _require_sha256(f"{mapping_name}[{key}]", digest)
        _require_mapping("metric_schema", self.metric_schema, nonempty=True)
        _require_mapping("parameters", self.parameters)
        _require_mapping("runtime_versions", self.runtime_versions, nonempty=True)
        _require_sha256("normalized_manifest_sha256", self.normalized_manifest_sha256)
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise ValidationError(
                f"unsupported ExperimentRunManifest schema {self.schema_version!r}"
            )


def contract_catalog() -> dict[str, Any]:
    """Machine-readable catalog for validators and experiment manifests."""

    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contracts": {
            "ObservationRecord": {
                "event_types": sorted(EVENT_TYPES, key=lambda value: int(value[1:])),
                "capture_statuses": sorted(CAPTURE_STATUSES),
                "lineage_rule": (
                    "observed/reconstructed require source artifact and SHA-256; "
                    "unobservable requires gap_reason"
                ),
            },
            "TriageDecision": {"outcomes": ["promote", "park"]},
            "ReviewItem": {"due_states": ["pending", "due", "overdue", "parked"]},
            "FeedbackRecord": {"crosswalk": "VEGO-AI/schemas/human_feedback.schema.json"},
            "VerificationRecord": {"outcomes": ["verified", "revised", "needs_adjudication"]},
            "CorrectionProposal": {"offline_applied": False},
            "MemoryRecord": {"accepted_sources": ["verified", "supervisor_adjudicated"]},
            "ExperimentRunManifest": {"hash_algorithm": "sha256"},
        },
    }
