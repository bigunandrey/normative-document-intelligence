from __future__ import annotations

"""Independent parsing contracts for retrieved authoritative documents."""

import hashlib
from dataclasses import dataclass
from typing import Protocol

from .canonical import CanonicalDocument
from .external_retrieval import RetrievedSource
from .external_sources import ExternalDocument, ExternalObservationSet
from .matching import compare_documents


class ExternalParser(Protocol):
    """Parser contract executed independently from the user-supplied observation set."""

    name: str
    version: str

    def parse(self, content: bytes, *, source_name: str, source_sha256: str) -> CanonicalDocument:
        ...


@dataclass(frozen=True)
class ExternalParserObservation:
    """One independently parsed, source-bound external representation."""

    parser: str
    parser_version: str
    document: CanonicalDocument
    source_sha256: str


def parse_retrieved_external(
    retrieved: RetrievedSource,
    parsers: tuple[ExternalParser, ...],
) -> tuple[ExternalParserObservation, ...]:
    """Parse verified external bytes with every configured independent parser."""
    if not parsers:
        raise ValueError("At least one independent external parser is required")
    identities = [(parser.name, parser.version) for parser in parsers]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate external parser identities are not allowed")

    content = retrieved.document.content
    if not isinstance(content, (bytes, bytearray)):
        raise ValueError("Retrieved external document must contain byte content")
    content = bytes(content)
    if hashlib.sha256(content).hexdigest() != retrieved.sha256:
        raise ValueError("Retrieved content no longer matches its verified SHA-256")

    results: list[ExternalParserObservation] = []
    for parser in parsers:
        document = parser.parse(
            content,
            source_name=retrieved.document.source.candidate.source_name,
            source_sha256=retrieved.sha256,
        )
        if not isinstance(document, CanonicalDocument):
            raise ValueError(f"External parser {parser.name} returned an invalid document")
        if document.source_sha256 != retrieved.sha256:
            raise ValueError(f"External parser {parser.name} returned a document bound to another source")
        if document.parser_versions.get(parser.name) != parser.version:
            raise ValueError(f"External parser {parser.name} returned mismatched parser provenance")
        results.append(ExternalParserObservation(parser.name, parser.version, document, retrieved.sha256))
    return tuple(results)


def aggregate_external_observations(
    document: ExternalDocument,
    observations: tuple[ExternalParserObservation, ...],
) -> ExternalObservationSet:
    """Aggregate independent external parser observations only when they agree."""
    if not observations:
        raise ValueError("At least one external parser observation is required")
    if document.source.compatibility.value != "same_revision":
        raise ValueError("External observation aggregation requires a validated same-revision source")

    expected_sha = document.metadata.get("sha256")
    for observation in observations:
        if observation.source_sha256 != expected_sha:
            raise ValueError("External parser observation is not bound to the retrieved source SHA-256")
        if observation.document.source_sha256 != expected_sha:
            raise ValueError("External parser observation document is not source-bound")

    ordered = tuple(sorted(observations, key=lambda item: (item.parser, item.parser_version)))
    reference = ordered[0].document
    disagreements: list[str] = []
    for observation in ordered[1:]:
        differences = compare_documents(reference, observation.document)
        if differences:
            disagreements.append(f"{observation.parser}@{observation.parser_version}: {differences}")
    if disagreements:
        raise ValueError("Independent external parser disagreement: " + " | ".join(disagreements))

    return ExternalObservationSet(
        document=document,
        parser_observations=ordered,
        canonical_document=reference,
    )
