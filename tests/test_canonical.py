from ndi.canonical import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    SourceAnchor,
    stable_document_id,
    stable_node_id,
)


def test_stable_document_id_is_source_based():
    digest = "a" * 64
    assert stable_document_id(digest) == "doc-aaaaaaaaaaaaaaaa"


def test_canonical_document_rejects_duplicate_node_ids():
    document = CanonicalDocument("doc-x", "x.pdf", "a" * 64, 1)
    node = CanonicalNode("node-1", NodeType.PARAGRAPH)
    document.add_node(node)
    try:
        document.add_node(node)
    except ValueError as exc:
        assert "Duplicate canonical node id" in str(exc)
    else:
        raise AssertionError("duplicate node id was accepted")


def test_stable_node_id_uses_anchor_and_ordinal():
    document_id = "doc-1234"
    anchor = SourceAnchor(page=4, bbox=BoundingBox(1, 2, 3, 4))
    first = stable_node_id(document_id, NodeType.PARAGRAPH, anchor, 1)
    second = stable_node_id(document_id, NodeType.PARAGRAPH, anchor, 1)
    assert first == second
