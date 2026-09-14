from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
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


class ResolutionAction(StrEnum):
    ACCEPT_SUPPLIED = "accept_supplied"
    ACCEPT_EXTERNAL = "accept_external"
    MANUAL_RESOLUTION = "manual_resolution"
    REJECT = "reject"


@dataclass(frozen=True)
class ResolutionDecision:
    """Explicit, provenance-linked disposition of one reconciliation blocker."""

    blocker_id: str
    action: ResolutionAction
    reviewer: str
    rationale: str
    evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.blocker_id.strip():
            raise ValueError("ResolutionDecision requires blocker_id")
        if not self.reviewer.strip():
            raise ValueError("ResolutionDecision requires reviewer")
        if not self.rationale.strip():
            raise ValueError("ResolutionDecision requires rationale")
        if not self.evidence:
            raise ValueError("ResolutionDecision requires explicit evidence")


@dataclass(frozen=True)
class ResolvedReconciliation:
    """Resolution record; it never mutates or overwrites the source documents."""

    integrated: IntegratedReconciliationReport
    decisions: tuple[ResolutionDecision, ...]
    accepted: bool
    blockers: tuple[str, ...]


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


def resolve_reconciliation(
    report: IntegratedReconciliationReport,
    decisions: Sequence[ResolutionDecision],
) -> ResolvedReconciliation:
    """Resolve every blocker explicitly; incomplete or conflicting dispositions fail closed."""
    supplied_blockers = {
        f"parser:{item.node_id}": item
        for item in report.parser_report.decisions
        if item.status in {"CONFLICT", "MISSING_OBSERVATION"}
    }
    external_blockers = {
        f"external:{index}": item
        for index, item in enumerate(report.external_discrepancies)
    }
    blockers = {**supplied_blockers, **external_blockers}
    provided = tuple(decisions)
    by_id = {item.blocker_id: item for item in provided}
    if len(by_id) != len(provided):
        raise ValueError("Duplicate resolution blocker IDs are not allowed")
    missing = tuple(sorted(set(blockers) - set(by_id)))
    unknown = tuple(sorted(set(by_id) - set(blockers)))
    if missing:
        raise ValueError("Resolution is incomplete; unresolved blockers: " + ", ".join(missing))
    if unknown:
        raise ValueError("Resolution contains unknown blockers: " + ", ".join(unknown))

    rejected = tuple(
        item.blocker_id
        for item in provided
        if item.action == ResolutionAction.REJECT
    )
    unresolved = tuple(
        item.blocker_id
        for item in provided
        if item.action != ResolutionAction.REJECT and not item.rationale.strip()
    )
    final_blockers = tuple(sorted((*rejected, *unresolved)))
    return ResolvedReconciliation(
        integrated=report,
        decisions=provided,
        accepted=not final_blockers,
        blockers=final_blockers,
    )
