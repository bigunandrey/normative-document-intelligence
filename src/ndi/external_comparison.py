from __future__ import annotations

"""Comparison of supplied observations against validated external-source evidence."""

from dataclasses import dataclass
from typing import Sequence

from .canonical import CanonicalDocument
from .external_sources import CrossCheckResult, DiscrepancyEvidence, DiscrepancyKind, DiscoveryStatus, ValidatedSource
from .matching import compare_documents


@dataclass(frozen=True)
class ExternalComparisonResult:
    source: ValidatedSource
    discrepancies: tuple[DiscrepancyEvidence, ...]

    @property
    def passed(self) -> bool:
        return not self.discrepancies


def compare_against_external(
    supplied: CanonicalDocument,
    external: CanonicalDocument,
    source: ValidatedSource,
) -> ExternalComparisonResult:
    """Convert deterministic document differences into provenance-bound evidence."""
    if source.compatibility.value != "same_revision":
        raise ValueError("External comparison requires a validated same-revision source")
    raw = compare_documents(supplied, external)
    discrepancies: list[DiscrepancyEvidence] = []
    for item in raw:
        cls = item.get("class")
        if cls == "TEXT_MISMATCH":
            kind = DiscrepancyKind.TEXT_MISMATCH
        elif cls in {"STRUCTURE_MISMATCH", "TABLE_MISMATCH"}:
            kind = DiscrepancyKind.STRUCTURE_MISMATCH
        elif cls == "ANCHOR_MISMATCH":
            kind = DiscrepancyKind.MISSING
        elif cls == "MISSING_OBSERVATION":
            kind = DiscrepancyKind.MISSING
        else:
            kind = DiscrepancyKind.UNRESOLVED
        anchors = tuple(
            {key: value for key, value in item.items() if key in {"left", "right", "node_id", "side"}}
        )
        discrepancies.append(
            DiscrepancyEvidence(
                kind=kind,
                description=f"External comparison: {cls}",
                source_ids=(source.candidate.source_id,),
                anchors=(anchors,) if anchors else (),
                evidence=("validated_same_revision_source", "deterministic_compare_documents"),
            )
        )
    return ExternalComparisonResult(source=source, discrepancies=tuple(discrepancies))


def compare_discovered_sources(
    supplied: CanonicalDocument,
    external_documents: Sequence[tuple[ValidatedSource, CanonicalDocument]],
) -> CrossCheckResult:
    """Compare supplied evidence against every validated same-revision external document."""
    results: list[ExternalComparisonResult] = []
    reasons: list[str] = []
    for source, external in external_documents:
        try:
            results.append(compare_against_external(supplied, external, source))
        except ValueError as exc:
            reasons.append(str(exc))
    sources = tuple(result.source for result in results)
    discrepancies = tuple(item for result in results for item in result.discrepancies)
    if not sources:
        return CrossCheckResult(DiscoveryStatus.NO_MATCH, reasons=tuple(reasons) or ("no validated external documents available",))
    return CrossCheckResult(
        DiscoveryStatus.MATCHED,
        sources=sources,
        discrepancies=discrepancies,
        reasons=tuple(reasons),
    )
