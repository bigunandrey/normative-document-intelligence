from ndi.canonical import CanonicalDocument, CanonicalNode, NodeType, ParserObservation, SourceAnchor
from ndi.matching import compare_documents, match_nodes, normalize_text


def make_document(parser: str, text: str, anchor: SourceAnchor | None = None) -> CanonicalDocument:
    document = CanonicalDocument("doc-test", "test.pdf", "a" * 64, 1, parser_versions={parser: "1"})
    node = CanonicalNode(
        "node-1",
        NodeType.PARAGRAPH,
        text=text,
        anchor=anchor,
        observations=[ParserObservation(parser, "1", f"{parser}-1", NodeType.PARAGRAPH, text=text, anchor=anchor)],
    )
    document.add_node(node)
    return document


def test_normalize_text_is_deterministic():
    assert normalize_text("  A B  ") == "a b"


def test_match_nodes_prefers_anchor():
    anchor = SourceAnchor(page=2)
    left = make_document("a", "Hello", anchor=anchor)
    right = make_document("b", "Different spelling", anchor=anchor)
    assert match_nodes(left, right) == [("node-1", "node-1")]
    discrepancies = compare_documents(left, right)
    assert {item["class"] for item in discrepancies} == {"TEXT_MISMATCH"}


def test_missing_node_is_reported():
    left = make_document("a", "Hello")
    right = CanonicalDocument("doc-test", "test.pdf", "a" * 64, 1, parser_versions={"b": "1"})
    discrepancies = compare_documents(left, right)
    assert discrepancies[0]["class"] == "MISSING_OBSERVATION"
    assert discrepancies[0]["side"] == "right"
