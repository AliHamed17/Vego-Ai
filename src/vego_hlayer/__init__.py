"""Canonical, contract-driven VEGO-AI human-judgment layer.

This package contains data contracts, compatibility adapters, parity execution,
and safety state handling. Importing it performs no I/O and cannot modify the
Agent 4 baseline.
"""

from .contracts import (
    CONTRACT_SCHEMA_VERSION,
    AdviceRecord,
    ArchitectureRunManifest,
    ComparisonRecord,
    CorrectionProposal,
    ExperimentRunManifest,
    FeedbackRecord,
    MemoryRecord,
    ObservationRecord,
    ReviewItem,
    TriageDecision,
    ValidationError,
    VerificationRecord,
    contract_catalog,
)
from .runtime import ArchitectureExecution, apply_architecture_mode
from .state_machine import ReviewState, ReviewStateMachine, TrustedMemoryStore

__all__ = [
    "CONTRACT_SCHEMA_VERSION",
    "AdviceRecord",
    "ArchitectureRunManifest",
    "ArchitectureExecution",
    "ComparisonRecord",
    "CorrectionProposal",
    "ExperimentRunManifest",
    "FeedbackRecord",
    "MemoryRecord",
    "ObservationRecord",
    "ReviewItem",
    "ReviewState",
    "ReviewStateMachine",
    "TriageDecision",
    "TrustedMemoryStore",
    "ValidationError",
    "VerificationRecord",
    "contract_catalog",
    "apply_architecture_mode",
]
