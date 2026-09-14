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
    assert doc.nodes[0].anchor is not None
    assert doc.nodes[0].anchor.page == 1
    assert doc.nodes[0].anchor.bbox is not None
    assert doc.nodes[0].attributes["bbox"] == [1, 2, 3, 4]
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


def test_structural_parent_links_remain_local_across_multiple_top_level_records():
    doc = from_records(
        [
            {"type": "table", "page": 1, "rows": [{"text": "r1", "cells": [{"text": "a"}]}]},
            {"type": "list", "page": 1, "items": [{"text": "one"}]},
            {"type": "paragraph", "text": "child", "page": 1, "parent_ordinal": 0},
        ],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    assert [n.node_type for n in doc.nodes] == [
        NodeType.TABLE, NodeType.TABLE_ROW, NodeType.TABLE_CELL,
        NodeType.LIST, NodeType.LIST_ITEM, NodeType.PARAGRAPH,
    ]
    assert doc.nodes[1].parent_id == doc.nodes[0].node_id
    assert doc.nodes[2].parent_id == doc.nodes[1].node_id
    assert doc.nodes[4].parent_id == doc.nodes[3].node_id
    assert doc.nodes[5].parent_id == doc.nodes[0].node_id


def test_common_structural_types_and_anchor_aliases_are_preserved():
    records = [
        {"type": "formula", "text": "x = 0,5", "page_index": 0, "char_start": 10, "char_end": 16},
        {"type": "header", "text": "Header", "page_no": 2},
        {"type": "footer", "text": "Footer", "page_number": 2},
        {"type": "footnote", "text": "Note", "pageNo": 2},
        {"type": "figure", "text": "Fig. 1", "page_num": 2},
        {"type": "note", "text": "Note 2", "page": 2},
    ]
    doc = from_records(records, source_name="test.pdf", source_sha256=SHA, page_count=2, parser="test", version="1.0")
    assert [n.node_type for n in doc.nodes] == [
        NodeType.FORMULA, NodeType.HEADER, NodeType.FOOTER,
        NodeType.FOOTNOTE, NodeType.FIGURE, NodeType.NOTE,
    ]
    assert doc.nodes[0].anchor is not None
    assert doc.nodes[0].anchor.page == 1
    assert doc.nodes[0].anchor.char_start == 10
    assert doc.nodes[0].anchor.char_end == 16
    assert all(node.anchor is not None and node.anchor.page == 2 for node in doc.nodes[1:])


def test_provenance_aliases_and_bbox_shapes_are_preserved():
    doc = from_records(
        [
            {"type": "paragraph", "text": "A", "provenance": {"page": 3, "bbox": {"left": 1, "top": 2, "right": 4, "bottom": 6}}},
            {"type": "paragraph", "text": "B", "prov": [{"page_index": 3, "boundingBox": {"x": 5, "y": 6, "width": 2, "height": 4}}]},
        ],
        source_name="test.pdf", source_sha256=SHA, page_count=4, parser="test", version="1.0",
    )
    assert doc.nodes[0].anchor is not None
    assert doc.nodes[0].anchor.page == 3
    assert doc.nodes[0].anchor.bbox == type(doc.nodes[0].anchor.bbox)(1, 2, 4, 6)
    assert doc.nodes[1].anchor is not None
    assert doc.nodes[1].anchor.page == 4
    assert doc.nodes[1].anchor.bbox == type(doc.nodes[1].anchor.bbox)(5, 6, 7, 10)


def test_confidence_and_raw_parser_attributes_are_preserved():
    doc = from_records(
        [{"type": "paragraph", "text": "Evidence", "page": 1, "confidence": 0.93, "custom": "kept"}],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    node = doc.nodes[0]
    assert node.observations[0].confidence == 0.93
    assert node.observations[0].attributes["custom"] == "kept"


def test_recursive_list_expansion_preserves_depth_first_reading_order():
    doc = from_records(
        [{"type": "list", "page": 1, "items": [
            {"text": "one", "items": [{"text": "one.a"}, {"text": "one.b"}]},
            {"text": "two"},
        ]}],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    assert [n.text for n in doc.nodes] == ["", "one", "one.a", "one.b", "two"]
    assert doc.nodes[2].parent_id == doc.nodes[1].node_id
    assert doc.nodes[3].parent_id == doc.nodes[1].node_id
    assert doc.nodes[4].parent_id == doc.nodes[0].node_id
    assert [n.order for n in doc.nodes] == list(range(5))
