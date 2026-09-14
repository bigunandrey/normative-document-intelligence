from __future__ import annotations

"""Fail-closed orchestration for authoritative external-source cross-checking."""

from dataclasses import dataclass
from typing import Sequence

from .canonical import CanonicalDocument
from .external_comparison import ExternalComparisonResult, compare_observation_set
from .external_parsing import ExternalParser, aggregate_external_observations, parse_retrieved_external
from .external_retrieval import retrieve_validated
from .external_sources import ExternalSourceProvider, ValidatedSource, discover_validated
from .source_registry import DocumentIdentity


@dataclass(frozen=True)
class ExternalPipelineResult:
    """Complete evidence for one validated external source."""

    source: ValidatedSource
    comparison: ExternalComparisonResult


def run_external_cross_check(
    supplied: CanonicalDocument,
    identity: DocumentIdentity,
    providers: Sequence[ExternalSourceProvider],
    parsers: tuple[ExternalParser, ...],
) -> tuple[ExternalPipelineResult, ...]:
    """Execute discovery → retrieval → independent parsing → aggregation → comparison.

    The pipeline is fail-closed: no authoritative same-revision source yields no results,
    retrieval/parsing/integrity errors propagate, and disagreement between independent
    external parsers prevents comparison rather than selecting a parser silently.
    """
    discovered = discover_validated(identity, providers)
    results: list[ExternalPipelineResult] = []
    for source in discovered.sources:
        provider = next(
            (candidate for candidate in providers if source in discover_validated(identity, (candidate,)).sources),
            None,
        )
        if provider is None:
            raise ValueError(f"No provider is available to retrieve validated source {source.candidate.source_id}")
        retrieved = retrieve_validated(provider, source)
        observations = parse_retrieved_external(retrieved, parsers)
        aggregated = aggregate_external_observations(retrieved.document, observations)
        comparison = compare_observation_set(supplied, aggregated)
        results.append(ExternalPipelineResult(source, comparison))
    return tuple(results)
