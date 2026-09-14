import pytest

from ndi import (
    CanonicalDocument,
    CanonicalNode,
    DiscrepancyKind,
    ExternalComparisonResult,
    ResolutionAction,
    ResolutionDecision,
    reconcile_with_external,
    resolve_reconciliation,
)
from ndi.canonical import NodeType
from ndi.external_sources import DiscrepancyEvidence


def document(*, conflict=False):
    doc = CanonicalDocument("doc", "test.pdf", "a" * 64, 1)
    node = CanonicalNode("n1", NodeType.PARAGRAPH, "canonical")
    from ndi.canonical import ParserObservation
    node.add_observation(ParserObservation("p1", "1", "o1", NodeType.PARAGRAPH, "first"))
    if conflict:
        node.add_observation(ParserObservation("p2", "1", "o2", NodeType.PARAGRAPH, "second"))
    doc.add_node(node)
    return doc


def test_clean_integrated_reconciliation_is_accepted():
    report = reconcile_with_external(document(), ())
    assert report.accepted
    assert not report.blocked


def test_parser_conflict_blocks_until_explicit_resolution():
    report = reconcile_with_external(document(conflict=True), ())
    assert report.blocked
    decision = ResolutionDecision(
        blocker_id="parser:n1",
        action=ResolutionAction.MANUAL_RESOLUTION,
        reviewer="reviewer",
        rationale="Reviewed source evidence and resolved manually.",
        evidence=("manual_review",),
    )
    resolved = resolve_reconciliation(report, (decision,))
    assert resolved.accepted
    assert resolved.decisions == (decision,)


def test_external_discrepancy_blocks_and_is_provenance_preserved():
    discrepancy = DiscrepancyEvidence(
        DiscrepancyKind.TEXT_MISMATCH,
        "external text differs",
        ("official",),
        evidence=("validated_same_revision_source",),
    )
    external_result = ExternalComparisonResult(
        source=None,
        discrepancies=(discrepancy,),
    )
    report = reconcile_with_external(document(), (external_result,))
    assert report.blocked
    assert report.external_discrepancies[0].source_ids == ("official",)


def test_resolution_requires_every_blocker_and_reject_stays_blocked():
    report = reconcile_with_external(document(conflict=True), ())
    with pytest.raises(ValueError, match="incomplete"):
        resolve_reconciliation(report, ())
    rejected = ResolutionDecision(
        blocker_id="parser:n1",
        action=ResolutionAction.REJECT,
        reviewer="reviewer",
        rationale="Evidence is insufficient for acceptance.",
        evidence=("review",),
    )
    resolved = resolve_reconciliation(report, (rejected,))
    assert not resolved.accepted
    assert resolved.blockers == ("parser:n1",)
