from __future__ import annotations

"""Independent parsing contracts for retrieved authoritative documents."""

import hashlib
from dataclasses import dataclass
from typing import Protocol

from .canonical import CanonicalDocument
from .external_retrieval import RetrievedSource


class ExternalParser(Protocol):
    name: str
    version: str

    def parse(self, content: bytes, *, source_name: str, source_sha256: str) -> CanonicalDocument:
        ...


@dataclass(frozen=True)
class ExternalParserObservation:
    parser: str
    parser_version: str
    document: CanonicalDocument
    source_sha256: str


def parse_retrieved_external(retrieved: RetrievedSource, parsers: tuple[ExternalParser, ...]) -> tuple[ExternalParserObservation, ...]:
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
    results = []
    for parser in parsers:
        document = parser.parse(content, source_name=retrieved.document.source.candidate.source_name, source_sha256=retrieved.sha256)
        if not isinstance(document, CanonicalDocument):
            raise ValueError(f"External parser {parser.name} returned an invalid document")
        if document.source_sha256 != retrieved.sha256:
            raise ValueError(f"External parser {parser.name} returned a document bound to another source")
        if document.parser_versions.get(parser.name) != parser.version:
            raise ValueError(f"External parser {parser.name} returned mismatched parser provenance")
        results.append(ExternalParserObservation(parser.name, parser.version, document, retrieved.sha256))
    return tuple(results)
