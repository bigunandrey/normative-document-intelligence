from __future__ import annotations

"""Explicit contracts for production Digital Copy stage evidence.

Stage executors remain domain-specific and dependency-injected. This module defines
only the deterministic evidence contract consumed by the orchestration boundary.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class StageEvidenceKind(StrEnum):
    IDENTITY = "IDENTITY"
    EXTRACTION = "EXTRACTION"
    RECONCILIATION = "RECONCILIATION"
    DIGITALIZATION = "DIGITALIZATION"
    GRAPHICAL_VERIFICATION = "GRAPHICAL_VERIFICATION"
    VERIFICATION = "VERIFICATION"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True)
class StageEvidence:
    """Immutable evidence declaration produced by a successful stage."""

    kind: StageEvidenceKind
    passed: bool
    artifacts: Mapping[str, str | bytes] = field(default_factory=dict)
    blockers: tuple[str, ...] = ()
    bindings: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.passed and not self.blockers:
            raise ValueError(f"Failed {self.kind.value} evidence must contain blockers")
        for key, value in self.bindings.items():
            if not str(key).strip() or not str(value).strip():
                raise ValueError(f"{self.kind.value} evidence contains an empty binding")
        for name in self.artifacts:
            if not str(name).strip():
                raise ValueError(f"{self.kind.value} evidence contains an empty artifact name")


_STAGE_BINDING_FIELDS = frozenset({"document_id", "revision_id"})


def apply_bindings(target: object, bindings: Mapping[str, str]) -> None:
    """Apply only recognized job bindings; reject unknown production bindings."""
    unknown = set(bindings) - _STAGE_BINDING_FIELDS
    if unknown:
        raise ValueError(f"Unsupported Digital Copy job bindings: {sorted(unknown)}")
    for key, value in bindings.items():
        setattr(target, key, value)
