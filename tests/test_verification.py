from pathlib import Path

from ndi import (
    AcceptanceEvidence,
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    ExternalCrossCheckRecord,
    GraphicalVerificationRecord,
    NodeType,
    ParserObservation,
    RevisionRecord,
    SourceAnchor,
    final_acceptance,
    gate_a_observations,
    gate_b_reconciliation,
    gate_c_structural_acceptance,
    gate_d_persistence,
    gate_e_revision_infrastructure,
    gate_f_verification,
)

SHA = "a" * 64


def make_doc(text="same"):
    doc = CanonicalDocument("doc-test", "test.pdf", SHA, 1)
    node = CanonicalNode(
        "node-1", NodeType.PARAGRAPH, text=text,
        anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10), char_start=0, char_end=len(text)),
        observations=[ParserObservation("p1", "1", "obs-1", NodeType.PARAGRAPH, text, SourceAnchor(page=1), 1.0)],
    )
    doc.add_node(node)
    return doc


def test_gate_a_requires_requested_parser_set():
    result = gate_a_observations([make_doc()], required_parsers={"p1", "p2"})
    assert result.status == "FAIL"
    assert not result.checks["required_parsers_present"]


def test_gate_b_and_c_pass_for_agreement():
    doc = make_doc()
    doc.nodes[0].add_observation(ParserObservation("p2", "1", "obs-2", NodeType.PARAGRAPH, "same", SourceAnchor(page=1), 1.0))
    b, report = gate_b_reconciliation(doc)
    assert b.status == "PASS"
    c = gate_c_structural_acceptance(doc, report)
    assert c.status == "PASS"


def test_gate_d_persists_source_bound_representation(tmp_path: Path):
    result = gate_d_persistence(make_doc(), tmp_path / "digital.json")
    assert result.status == "PASS"
    assert (tmp_path / "digital.json").is_file()


def test_gate_e_is_fail_closed_when_result_missing(tmp_path: Path):
    record = RevisionRecord("Rev_001", "doc-test", SHA, "sha256:x", "AI-1", "verification", "2026-09-14", True)
    result = gate_e_revision_infrastructure(record, tmp_path)
    assert result.status == "FAIL"
    assert not result.checks["result_recorded"]


def test_gate_f_requires_both_verification_layers():
    graphical = GraphicalVerificationRecord("doc-test", SHA, (1,), ("tables",), result="PASS", verifier="AI", verified_at="2026-09-14")
    external = ExternalCrossCheckRecord("doc-test", SHA, ("https://example.invalid/source",), ("identity",), result="PASS", resolution_status="RESOLVED")
    assert gate_f_verification(graphical, external).status == "PASS"


def test_final_acceptance_is_fail_closed():
    blocked = final_acceptance(AcceptanceEvidence(source_verified=True))
    assert blocked.status == "FAIL"
    accepted = final_acceptance(AcceptanceEvidence(*([True] * 7), ai_verifications=2, regression_verified=True, master_registers_synchronized=True, revision_locked=True))
    assert accepted.status == "PASS"
