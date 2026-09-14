from __future__ import annotations

"""Fail-closed orchestration for authoritative external-source cross-checking."""

from dataclasses import dataclass
from typing import Sequence

from .canonical import CanonicalDocument
from .external_comparison import ExternalComparisonResult, compare_observation_set
from .external_parsing import ExternalParser, aggregate_external_observations, parse_retrieved_external
from .external_retrieval import retrieve_validated
from .external_sources import ExternalSourceProvider, ValidatedSource, validate_candidate
from .source_registry import Compatibility, DocumentIdentity


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
    results: list[ExternalPipelineResult] = []
    seen_source_ids: set[str] = set()
    for provider in providers:
        candidates = tuple(provider.discover(identity))
        for candidate in sorted(candidates, key=lambda item: item.source_id):
            source = validate_candidate(identity, candidate)
            if source.compatibility != Compatibility.SAME_REVISION:
                continue
            if source.candidate.source_id in seen_source_ids:
                continue
            seen_source_ids.add(source.candidate.source_id)
            retrieved = retrieve_validated(provider, source)
            observations = parse_retrieved_external(retrieved, parsers)
            aggregated = aggregate_external_observations(retrieved.document, observations)
            comparison = compare_observation_set(supplied, aggregated)
            results.append(ExternalPipelineResult(source, comparison))
    return tuple(results)
