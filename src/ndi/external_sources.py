from __future__ import annotations

"""Provider-neutral contracts for authoritative normative-source discovery."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Mapping, Protocol, Sequence

from .source_registry import Compatibility, DocumentIdentity, SourceCandidate

if TYPE_CHECKING:
    from .external_parsing import ExternalParserObservation


class DiscoveryStatus(StrEnum):
    MATCHED = "matched"
    NO_MATCH = "no_match"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class ValidatedSource:
    """A source candidate whose identity and authority checks have been completed."""

    candidate: SourceCandidate
    compatibility: Compatibility
    validation_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.compatibility == Compatibility.INVALID:
            raise ValueError("An invalid source cannot be a ValidatedSource")
        if not self.validation_evidence:
            raise ValueError("ValidatedSource requires validation evidence")


@dataclass(frozen=True)
class ExternalDocument:
    """Source-bound external document reference; content is supplied by a provider."""

    source: ValidatedSource
    content: Any
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExternalObservationSet:
    """Deterministically aggregated independent parser observations for one source."""

    document: ExternalDocument
    parser_observations: tuple[ExternalParserObservation, ...]
    canonical_document: Any

    def __post_init__(self) -> None:
        if self.document.source.compatibility != Compatibility.SAME_REVISION:
            raise ValueError("External observations require a validated same-revision source")
        if not self.parser_observations:
            raise ValueError("ExternalObservationSet requires at least one parser observation")
        source_sha = self.parser_observations[0].source_sha256
        if any(item.source_sha256 != source_sha for item in self.parser_observations):
            raise ValueError("ExternalObservationSet parser observations must share one source SHA-256")
        if self.canonical_document.source_sha256 != source_sha:
            raise ValueError("ExternalObservationSet canonical document is not source-bound")


class DiscrepancyKind(StrEnum):
    MISSING = "missing"
    TEXT_MISMATCH = "text_mismatch"
    STRUCTURE_MISMATCH = "structure_mismatch"
    VALUE_MISMATCH = "value_mismatch"
    REVISION_MISMATCH = "revision_mismatch"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class DiscrepancyEvidence:
    kind: DiscrepancyKind
    description: str
    source_ids: tuple[str, ...]
    anchors: tuple[Mapping[str, Any], ...] = ()
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("DiscrepancyEvidence requires a description")
        if not self.source_ids:
            raise ValueError("DiscrepancyEvidence requires source provenance")
        if not self.evidence:
            raise ValueError("DiscrepancyEvidence requires explicit evidence")


@dataclass(frozen=True)
class CrossCheckResult:
    status: DiscoveryStatus
    sources: tuple[ValidatedSource, ...] = ()
    discrepancies: tuple[DiscrepancyEvidence, ...] = ()
    reasons: tuple[str, ...] = ()


class ExternalSourceProvider(Protocol):
    """Provider contract; implementations perform discovery/retrieval externally."""

    name: str

    def discover(self, identity: DocumentIdentity) -> Sequence[SourceCandidate]:
        ...

    def retrieve(self, source: ValidatedSource) -> ExternalDocument:
        ...


def validate_candidate(identity: DocumentIdentity, candidate: SourceCandidate) -> ValidatedSource:
    """Validate authority and exact revision compatibility without silent fallback."""
    compatibility = candidate.compatibility_with(identity)
    evidence = tuple(candidate.evidence)
    if candidate.authority_verified:
        evidence += ("authority_verified",)
    if candidate.revision_verified:
        evidence += ("revision_verified",)
    if compatibility == Compatibility.INVALID:
        raise ValueError(f"Source candidate {candidate.source_id} is invalid")
    if not evidence:
        raise ValueError(f"Source candidate {candidate.source_id} has no validation evidence")
    return ValidatedSource(candidate, compatibility, evidence)


def discover_validated(
    identity: DocumentIdentity,
    providers: Sequence[ExternalSourceProvider],
) -> CrossCheckResult:
    """Discover and validate candidates across providers; never invent a match."""
    candidates: list[SourceCandidate] = []
    reasons: list[str] = []
    for provider in providers:
        found = tuple(provider.discover(identity))
        if not found:
            reasons.append(f"{provider.name}: no candidates returned")
            continue
        candidates.extend(found)

    validated: list[ValidatedSource] = []
    for candidate in candidates:
        try:
            source = validate_candidate(identity, candidate)
        except ValueError as exc:
            reasons.append(str(exc))
            continue
        if source.compatibility == Compatibility.SAME_REVISION:
            validated.append(source)
        else:
            reasons.append(
                f"{candidate.source_id}: compatibility={source.compatibility.value}; same-revision match required"
            )

    if validated:
        return CrossCheckResult(DiscoveryStatus.MATCHED, tuple(validated), reasons=tuple(reasons))
    return CrossCheckResult(DiscoveryStatus.NO_MATCH, reasons=tuple(reasons) or ("no authoritative same-revision source available",))
