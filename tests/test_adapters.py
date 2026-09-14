from ndi import NodeType, from_markitdown, from_records, parser_coverage


SHA = "a" * 64


def test_from_records_preserves_explicit_parent_and_provenance():
    doc = from_records(
        [
            {"type": "heading", "text": "Section", "page": 1, "bbox": [1, 2, 3, 4]},
            {"type": "paragraph", "text": "Body", "page": 1, "parent_ordinal": 0},
        ],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    assert len(doc.nodes) == 2
    assert doc.nodes[1].parent_id == doc.nodes[0].node_id
    assert doc.nodes[0].node_type == NodeType.SECTION
    assert parser_coverage(doc) == {"test": 2}


def test_from_markitdown_does_not_fabricate_page_anchors():
    doc = from_markitdown("# Title\n\nBody\n\n| A | B |", source_name="test.pdf", source_sha256=SHA, page_count=1)
    assert [n.node_type for n in doc.nodes] == [NodeType.SECTION, NodeType.PARAGRAPH, NodeType.TABLE_ROW]
    assert all(n.anchor is not None and n.anchor.page is None for n in doc.nodes)
