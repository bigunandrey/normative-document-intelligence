from __future__ import annotations

"""Reconciliation of supplied parser evidence with external-source evidence."""

from dataclasses import dataclass
from typing import Sequence

from .canonical import CanonicalDocument
from .external_comparison import ExternalComparisonResult
from .external_sources import DiscrepancyEvidence
from .reconciliation import ReconciliationDecision, ReconciliationReport, reconcile_document


@dataclass(frozen=True)
class IntegratedReconciliationReport:
    """Single evidence view; any parser conflict or external discrepancy blocks acceptance."""

    parser_report: ReconciliationReport
    external_results: tuple[ExternalComparisonResult, ...]
    decisions: tuple[ReconciliationDecision, ...]
    external_discrepancies: tuple[DiscrepancyEvidence, ...]

    @property
    def conflicts(self) -> tuple[ReconciliationDecision, ...]:
        return tuple(self.parser_report.conflicts)

    @property
    def blocked(self) -> bool:
        return bool(self.conflicts or self.external_discrepancies)

    @property
    def accepted(self) -> bool:
        return not self.blocked


def reconcile_with_external(
    supplied: CanonicalDocument,
    external_results: Sequence[ExternalComparisonResult],
) -> IntegratedReconciliationReport:
    """Combine local parser reconciliation and external comparison without correction."""
    parser_report = reconcile_document(supplied)
    normalized_results = tuple(external_results)
    external_discrepancies = tuple(
        discrepancy
        for result in normalized_results
        for discrepancy in result.discrepancies
    )
    return IntegratedReconciliationReport(
        parser_report=parser_report,
        external_results=normalized_results,
        decisions=tuple(parser_report.decisions),
        external_discrepancies=external_discrepancies,
    )
