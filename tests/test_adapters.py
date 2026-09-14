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


def test_nested_table_rows_and_cells_preserve_parent_links():
    doc = from_records(
        [{"type": "table", "page": 1, "rows": [
            {"text": "r1", "cells": [{"text": "a"}, {"text": "b"}]},
            {"text": "r2", "cells": [{"text": "c"}]},
        ]}],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    assert [n.node_type for n in doc.nodes] == [NodeType.TABLE, NodeType.TABLE_ROW, NodeType.TABLE_CELL, NodeType.TABLE_CELL, NodeType.TABLE_ROW, NodeType.TABLE_CELL]
    assert doc.nodes[1].parent_id == doc.nodes[0].node_id
    assert doc.nodes[2].parent_id == doc.nodes[1].node_id
    assert doc.nodes[3].parent_id == doc.nodes[1].node_id
    assert doc.nodes[4].parent_id == doc.nodes[0].node_id
    assert doc.nodes[5].parent_id == doc.nodes[4].node_id


def test_nested_list_items_preserve_parent_link():
    doc = from_records(
        [{"type": "list", "page": 1, "items": [{"text": "one"}, {"text": "two"}]}],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    assert [n.node_type for n in doc.nodes] == [NodeType.LIST, NodeType.LIST_ITEM, NodeType.LIST_ITEM]
    assert doc.nodes[1].parent_id == doc.nodes[0].node_id
    assert doc.nodes[2].parent_id == doc.nodes[0].node_id
