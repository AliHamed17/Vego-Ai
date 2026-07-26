"""Offline, contract-first H-layer research helpers.

This package is deliberately isolated from ``VEGO-AI/framework``.  It models
proposed H-layer records and safety behavior for reproducible offline
experiments; importing it cannot change baseline runtime behavior.
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
from .state_machine import (
    ReviewState,
    ReviewStateMachine,
    TrustedMemoryStore,
    route_observation,
)
from .suite import execute_suite

__all__ = [
    "CONTRACT_SCHEMA_VERSION",
    "AdviceRecord",
    "ArchitectureRunManifest",
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
    "execute_suite",
    "route_observation",
]
