from ndi import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    ExternalComparisonResult,
    DiscrepancyEvidence,
    DiscrepancyKind,
    NodeType,
    ParserObservation,
    ResolutionAction,
    ResolutionDecision,
    SourceAnchor,
    gate_c_structural_acceptance,
    reconcile_with_external,
    resolve_reconciliation,
)


def make_doc(conflict=False):
    doc = CanonicalDocument("doc", "test.pdf", "a" * 64, 1)
    node = CanonicalNode("n1", NodeType.PARAGRAPH, "same", anchor=SourceAnchor(page=1))
    node.add_observation(ParserObservation("p1", "1", "o1", NodeType.PARAGRAPH, "same", SourceAnchor(page=1), 1.0))
    if conflict:
        node.add_observation(ParserObservation("p2", "1", "o2", NodeType.PARAGRAPH, "different", SourceAnchor(page=1), 1.0))
    doc.add_node(node)
    return doc


def test_gate_c_accepts_only_resolved_integrated_reconciliation():
    clean = make_doc()
    report = reconcile_with_external(clean, ())
    _, parser_report = __import__("ndi").gate_b_reconciliation(clean)
    assert gate_c_structural_acceptance(clean, parser_report, report).status == "PASS"

    conflict = make_doc(conflict=True)
    integrated = reconcile_with_external(conflict, ())
    _, conflict_report = __import__("ndi").gate_b_reconciliation(conflict)
    result = gate_c_structural_acceptance(conflict, conflict_report, integrated)
    assert result.status == "FAIL"
    assert not result.checks["integrated_reconciliation_resolved"]


def test_resolved_blocker_can_close_gate_c_without_mutating_document():
    doc = make_doc(conflict=True)
    original = doc.to_json()
    integrated = reconcile_with_external(doc, ())
    resolved = resolve_reconciliation(
        integrated,
        (ResolutionDecision(
            "parser:n1", ResolutionAction.MANUAL_RESOLUTION, "reviewer",
            "Manual review completed against preserved source evidence.",
            ("manual_review",),
        ),),
    )
    assert resolved.accepted
    assert doc.to_json() == original
    _, parser_report = __import__("ndi").gate_b_reconciliation(doc)
    result = gate_c_structural_acceptance(doc, parser_report, integrated)
    assert result.status == "FAIL"


def test_external_blocker_remains_blocking_until_explicit_resolution():
    discrepancy = DiscrepancyEvidence(
        DiscrepancyKind.TEXT_MISMATCH, "text differs", ("official",),
        evidence=("validated_same_revision_source",),
    )
    external = ExternalComparisonResult(None, (discrepancy,))
    integrated = reconcile_with_external(make_doc(), (external,))
    assert integrated.blocked
    resolved = resolve_reconciliation(
        integrated,
        (ResolutionDecision(
            "external:0", ResolutionAction.ACCEPT_SUPPLIED, "reviewer",
            "Reviewed discrepancy; supplied representation retained.",
            ("comparison_review",),
        ),),
    )
    assert resolved.accepted
