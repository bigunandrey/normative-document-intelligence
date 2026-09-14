from ndi import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    GraphicalVerificationRecord,
    NodeType,
    ParserObservation,
    SourceAnchor,
    gate_c_structural_acceptance,
    validate_graphical_verification,
)
from ndi.reconciliation import ReconciliationDecision, ReconciliationReport

SHA = "a" * 64


def document():
    anchor = SourceAnchor(page=1, bbox=BoundingBox(0, 0, 100, 20), char_start=0, char_end=4)
    node = CanonicalNode(
        "n1",
        NodeType.PARAGRAPH,
        text="text",
        order=0,
        anchor=anchor,
        observations=[ParserObservation("test", "1.0", "o1", NodeType.PARAGRAPH, "text", anchor, 0.99)],
    )
    return CanonicalDocument("doc", "source.pdf", SHA, 3, [node])


def report():
    return ReconciliationReport([
        ReconciliationDecision("n1", "AGREED", ("o1",), "agreement")
    ])


def record(result="PASS"):
    return GraphicalVerificationRecord(
        "doc",
        SHA,
        (1, 2, 3),
        (
            "table structure and merged cells",
            "formula and numeric values",
            "normative operator symbols",
            "notes and footnotes",
            "numbering and page order",
            "amendment and deletion markers",
        ),
        result=result,
        verifier="AI-2",
        verified_at="2026-09-14T19:00:00Z",
    )


def test_gate_c_accepts_valid_graphical_evidence():
    graphical = validate_graphical_verification(record())
    result = gate_c_structural_acceptance(document(), report(), graphical_verification=graphical)
    assert result.status == "PASS"
    assert result.checks["graphical_verification_pass"]


def test_gate_c_rejects_failed_graphical_evidence():
    graphical = validate_graphical_verification(record(result="FAIL"))
    result = gate_c_structural_acceptance(document(), report(), graphical_verification=graphical)
    assert result.status == "FAIL"
    assert not result.checks["graphical_verification_pass"]
