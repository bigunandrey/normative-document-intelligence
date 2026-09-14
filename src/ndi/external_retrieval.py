from __future__ import annotations

"""Fail-closed retrieval and integrity verification for validated external sources."""

import hashlib
from dataclasses import dataclass
from typing import Any

from .external_sources import ExternalDocument, ExternalSourceProvider, ValidatedSource


@dataclass(frozen=True)
class RetrievedSource:
    document: ExternalDocument
    sha256: str


def verify_retrieved_bytes(source: ValidatedSource, content: bytes) -> RetrievedSource:
    """Verify retrieved bytes against candidate SHA-256 when the candidate supplies one."""
    digest = hashlib.sha256(content).hexdigest()
    expected = source.candidate.sha256
    if expected is not None and digest != expected:
        raise ValueError(
            f"External source {source.candidate.source_id}: retrieved SHA-256 does not match candidate"
        )
    document = ExternalDocument(source=source, content=content, metadata={"sha256": digest})
    return RetrievedSource(document=document, sha256=digest)


def retrieve_validated(
    provider: ExternalSourceProvider,
    source: ValidatedSource,
) -> RetrievedSource:
    """Retrieve through the provider and require explicit byte content for integrity verification."""
    if source.compatibility.value != "same_revision":
        raise ValueError("Retrieval requires a validated same-revision source")
    document = provider.retrieve(source)
    if not isinstance(document.content, (bytes, bytearray)):
        raise ValueError("External provider must return byte content for integrity verification")
    return verify_retrieved_bytes(source, bytes(document.content))
