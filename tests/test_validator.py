from ndi.canonical import CanonicalDocument, CanonicalNode, NodeType, ParserObservation, SourceAnchor
from ndi.validator import Quality, audit_document


SHA = "a" * 64


def node(node_id, order=0, parent_id=None, page=1, observation=True):
    observations = []
    if observation:
        observations.append(
            ParserObservation(
                parser="test",
                parser_version="1.0",
                observation_id=f"obs-{node_id}",
                node_type=NodeType.PARAGRAPH,
                text="text",
                anchor=SourceAnchor(page=page),
                confidence=0.99,
            )
        )
    return CanonicalNode(
        node_id=node_id,
        node_type=NodeType.PARAGRAPH,
        text="text",
        parent_id=parent_id,
        order=order,
        anchor=SourceAnchor(page=page),
        observations=observations,
    )


def document(*nodes, source_sha256=SHA):
    return CanonicalDocument("doc-test", "test.pdf", source_sha256, 1, list(nodes))


def test_valid_document_passes():
    audit = audit_document(document(node("n1")))
    assert audit.quality == Quality.PASS
    assert audit.passed
    assert not audit.issues


def test_missing_optional_evidence_is_warning():
    n = node("n1")
    n.anchor = SourceAnchor(page=1)
    n.observations[0] = ParserObservation("test", "1.0", "obs-n1", NodeType.PARAGRAPH, "text", SourceAnchor(page=1), None)
    audit = audit_document(document(n))
    assert audit.quality == Quality.PASS_WITH_WARNINGS
    assert any(i.code == "MISSING_CHAR_SPAN" for i in audit.warnings)
    assert any(i.code == "MISSING_BBOX" for i in audit.warnings)
    assert any(i.code == "MISSING_CONFIDENCE" for i in audit.warnings)


def test_missing_observation_fails():
    audit = audit_document(document(node("n1", observation=False)))
    assert audit.quality == Quality.FAIL
    assert any(i.code == "MISSING_OBSERVATION" for i in audit.errors)


def test_broken_parent_fails():
    audit = audit_document(document(node("n1", parent_id="missing")))
    assert audit.quality == Quality.FAIL
    assert any(i.code == "BROKEN_PARENT" for i in audit.errors)


def test_parent_cycle_fails():
    a = node("a", parent_id="b")
    b = node("b", parent_id="a")
    audit = audit_document(document(a, b))
    assert audit.quality == Quality.FAIL
    assert any(i.code == "PARENT_CYCLE" for i in audit.errors)


def test_invalid_source_hash_fails():
    audit = audit_document(document(node("n1"), source_sha256="not-a-sha"))
    assert audit.quality == Quality.FAIL
    assert any(i.code == "INVALID_SOURCE_HASH" for i in audit.errors)


def test_duplicate_sibling_order_fails():
    audit = audit_document(document(node("n1", order=1), node("n2", order=1)))
    assert audit.quality == Quality.FAIL
    assert any(i.code == "DUPLICATE_ORDER" for i in audit.errors)
