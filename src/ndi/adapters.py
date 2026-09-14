from __future__ import annotations

"""Evidence-only adapters for common parser record shapes."""

from collections.abc import Mapping
from typing import Any

from .canonical import BoundingBox, CanonicalDocument, NodeType, SourceAnchor, stable_document_id
from .observations import RawObservation, add_observation


def _text(value: Any) -> str:
    if value is None: return ""
    if isinstance(value, str): return value
    if isinstance(value, Mapping):
        for key in ("text", "content", "value", "label"):
            if key in value: return _text(value[key])
    return str(value)


def _bbox(value: Any) -> BoundingBox | None:
    if isinstance(value, Mapping):
        if all(k in value for k in ("left", "top", "right", "bottom")):
            return BoundingBox(*(float(value[k]) for k in ("left", "top", "right", "bottom")))
        if all(k in value for k in ("l", "t", "r", "b")):
            return BoundingBox(*(float(value[k]) for k in ("l", "t", "r", "b")))
        if all(k in value for k in ("x", "y", "width", "height")):
            x, y, w, h = (float(value[k]) for k in ("x", "y", "width", "height"))
            return BoundingBox(x, y, x + w, y + h)
        for key in ("bbox", "bounding_box", "boundingBox"):
            if key in value: return _bbox(value[key])
    if isinstance(value, (list, tuple)) and len(value) == 4:
        return BoundingBox(*(float(x) for x in value))
    return None


def _page(item: Mapping[str, Any]) -> int | None:
    for key in ("page", "page_no", "page_number", "pageNo", "page_num"):
        if key in item:
            try: return int(item[key])
            except (TypeError, ValueError): return None
    prov = item.get("prov", item.get("provenance"))
    if isinstance(prov, list) and prov and isinstance(prov[0], Mapping): return _page(prov[0])
    if isinstance(prov, Mapping): return _page(prov)
    return None


def _anchor(item: Mapping[str, Any]) -> SourceAnchor:
    return SourceAnchor(page=_page(item), bbox=_bbox(item))


def _node_type(value: Any) -> NodeType:
    raw = str(value or "").lower().replace("-", "_").replace(" ", "_")
    return {"document": NodeType.DOCUMENT, "page": NodeType.PAGE, "text": NodeType.PARAGRAPH,
            "paragraph": NodeType.PARAGRAPH, "heading": NodeType.SECTION, "title": NodeType.SECTION,
            "section": NodeType.SECTION, "list": NodeType.LIST, "list_item": NodeType.LIST_ITEM,
            "table": NodeType.TABLE, "row": NodeType.TABLE_ROW, "table_row": NodeType.TABLE_ROW,
            "cell": NodeType.TABLE_CELL, "table_cell": NodeType.TABLE_CELL, "formula": NodeType.FORMULA,
            "equation": NodeType.FORMULA, "note": NodeType.NOTE, "footnote": NodeType.FOOTNOTE,
            "figure": NodeType.FIGURE, "image": NodeType.FIGURE, "header": NodeType.HEADER,
            "footer": NodeType.FOOTER}.get(raw, NodeType.UNKNOWN)


def new_document(source_name: str, source_sha256: str, page_count: int | None, parser: str, version: str) -> CanonicalDocument:
    return CanonicalDocument(document_id=stable_document_id(source_sha256), source_name=source_name,
                             source_sha256=source_sha256, page_count=page_count,
                             parser_versions={parser: version})


def from_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str,
                 page_count: int | None, parser: str, version: str) -> CanonicalDocument:
    document = new_document(source_name, source_sha256, page_count, parser, version)
    node_by_ordinal: dict[int, CanonicalNode] = {}
    pending_parent: dict[int, int] = {}
    for ordinal, item in enumerate(records):
        node = add_observation(document, RawObservation(parser, version,
            _node_type(item.get("type", item.get("element_type", item.get("kind")))),
            _text(item.get("text", item.get("content", item.get("value")))), _anchor(item),
            item.get("confidence"), dict(item)), ordinal=ordinal)
        node_by_ordinal[ordinal] = node
        if item.get("parent_ordinal") is not None:
            try: pending_parent[ordinal] = int(item["parent_ordinal"])
            except (TypeError, ValueError): pass
    for ordinal, parent_ordinal in pending_parent.items():
        node, parent = node_by_ordinal.get(ordinal), node_by_ordinal.get(parent_ordinal)
        if node is not None and parent is not None: node.parent_id = parent.node_id
    return document


def from_markitdown(text: str, *, source_name: str, source_sha256: str,
                    page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        value = line.strip()
        if not value: continue
        typ = NodeType.SECTION if value.startswith("#") else NodeType.TABLE_ROW if value.startswith("|") else NodeType.PARAGRAPH
        records.append({"type": typ.value, "text": value, "source_line": line_no})
    return from_records(records, source_name=source_name, source_sha256=source_sha256,
                        page_count=page_count, parser="markitdown", version=version)
