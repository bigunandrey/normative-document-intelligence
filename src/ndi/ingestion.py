from __future__ import annotations

"""Deterministic parser-observation ingestion orchestration."""

from dataclasses import dataclass
from typing import Any, Mapping

from .adapter_registry import ParserAdapter, adapt_all, default_adapters, validate_default_adapters
from .canonical import CanonicalDocument
from .observation_artifacts import observation_artifact_json, observation_artifact_sha256


@dataclass(frozen=True)
class ObservationArtifact:
    """Source-bound observation artifact produced by one parser."""

    parser: str
    parser_version: str
    document: CanonicalDocument
    manifest_json: str
    sha256: str


@dataclass(frozen=True)
class ObservationPackage:
    """Complete deterministic package for the configured parser set."""

    source_name: str
    source_sha256: str
    parsers: tuple[ObservationArtifact, ...]

    @property
    def parser_names(self) -> tuple[str, ...]:
        return tuple(item.parser for item in self.parsers)


def ingest_parser_outputs(
    sources: Mapping[str, Any],
    *,
    source_name: str,
    source_sha256: str,
    page_count: int | None = None,
    adapters: tuple[ParserAdapter, ...] | None = None,
) -> ObservationPackage:
    """Convert a complete parser-output set into source-bound observation artifacts.

    Every configured parser must have an explicit output. The function never substitutes
    one parser for another and never silently drops an unavailable parser.
    """
    configured = adapters or default_adapters()
    validate_default_adapters(configured)
    documents = adapt_all(
        sources,
        source_name=source_name,
        source_sha256=source_sha256,
        page_count=page_count,
        adapters=configured,
    )
    artifacts = tuple(
        ObservationArtifact(
            parser=adapter.name,
            parser_version=adapter.version,
            document=documents[adapter.name],
            manifest_json=observation_artifact_json(documents[adapter.name]),
            sha256=observation_artifact_sha256(documents[adapter.name]),
        )
        for adapter in configured
    )
    return ObservationPackage(source_name, source_sha256, artifacts)
