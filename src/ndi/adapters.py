from __future__ import annotations

"""Evidence-only adapters for common parser record shapes."""

from collections.abc import Mapping
from typing import Any

from .canonical import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor, stable_document_id
from .observations import RawObservation, add_observation


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("text", "content", "value", "label"):
            if key in value:
                return _text(value[key])
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
        for key in ("bbox", "bounding_box", "boundingBox", "prov_bbox"):
            if key in value:
                return _bbox(value[key])
    if isinstance(value, (list, tuple)) and len(value) == 4:
        return BoundingBox(*(float(x) for x in value))
    return None


def _page(item: Mapping[str, Any]) -> int | None:
    for key in ("page", "page_no", "page_number", "pageNo", "page_num", "page_index"):
        if key in item:
            try:
                value = int(item[key])
                return value + 1 if key == "page_index" and value >= 0 else value
            except (TypeError, ValueError):
                return None
    prov = item.get("prov", item.get("provenance"))
    if isinstance(prov, list) and prov and isinstance(prov[0], Mapping):
        return _page(prov[0])
    if isinstance(prov, Mapping):
        return _page(prov)
    return None


def _anchor(item: Mapping[str, Any]) -> SourceAnchor:
    return SourceAnchor(page=_page(item), bbox=_bbox(item), char_start=item.get("char_start"), char_end=item.get("char_end"))


def _node_type(value: Any) -> NodeType:
    raw = str(value or "").lower().replace("-", "_").replace(" ", "_")
    return {
        "document": NodeType.DOCUMENT, "page": NodeType.PAGE, "text": NodeType.PARAGRAPH,
        "paragraph": NodeType.PARAGRAPH, "heading": NodeType.SECTION, "title": NodeType.SECTION,
        "section": NodeType.SECTION, "list": NodeType.LIST, "list_item": NodeType.LIST_ITEM,
        "table": NodeType.TABLE, "row": NodeType.TABLE_ROW, "table_row": NodeType.TABLE_ROW,
        "cell": NodeType.TABLE_CELL, "table_cell": NodeType.TABLE_CELL, "formula": NodeType.FORMULA,
        "equation": NodeType.FORMULA, "note": NodeType.NOTE, "footnote": NodeType.FOOTNOTE,
        "figure": NodeType.FIGURE, "image": NodeType.FIGURE, "header": NodeType.HEADER,
        "footer": NodeType.FOOTER,
    }.get(raw, NodeType.UNKNOWN)


def new_document(source_name: str, source_sha256: str, page_count: int | None, parser: str, version: str) -> CanonicalDocument:
    return CanonicalDocument(document_id=stable_document_id(source_sha256), source_name=source_name,
                             source_sha256=source_sha256, page_count=page_count, parser_versions={parser: version})


def _expand_structural_record(item: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Expand common nested table/list records while retaining the parser payload verbatim."""
    result: list[Mapping[str, Any]] = [item]
    typ = _node_type(item.get("type", item.get("element_type", item.get("kind"))))
    if typ == NodeType.TABLE:
        rows = item.get("rows", item.get("children", ()))
        if isinstance(rows, (list, tuple)):
            for row in rows:
                if not isinstance(row, Mapping):
                    row = {"text": _text(row)}
                row_data = dict(row)
                row_data.setdefault("type", NodeType.TABLE_ROW.value)
                row_data.setdefault("page", _page(item))
                result.append(row_data)
                cells = row_data.get("cells", row_data.get("children", ()))
                if isinstance(cells, (list, tuple)):
                    for cell in cells:
                        cell_data = dict(cell) if isinstance(cell, Mapping) else {"text": _text(cell)}
                        cell_data.setdefault("type", NodeType.TABLE_CELL.value)
                        cell_data.setdefault("page", _page(row_data))
                        result.append(cell_data)
    elif typ == NodeType.LIST:
        items = item.get("items", item.get("children", ()))
        if isinstance(items, (list, tuple)):
            for child in items:
                child_data = dict(child) if isinstance(child, Mapping) else {"text": _text(child)}
                child_data.setdefault("type", NodeType.LIST_ITEM.value)
                child_data.setdefault("page", _page(item))
                result.append(child_data)
    return result


def from_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str,
                 page_count: int | None, parser: str, version: str) -> CanonicalDocument:
    """Map normalized parser records to canonical evidence without inference."""
    document = new_document(source_name, source_sha256, page_count, parser, version)
    expanded: list[Mapping[str, Any]] = []
    for item in records:
        expanded.extend(_expand_structural_record(item))
    node_by_ordinal: dict[int, CanonicalNode] = {}
    pending_parent: dict[int, int] = {}
    for ordinal, item in enumerate(expanded):
        node = add_observation(document, RawObservation(parser, version,
            _node_type(item.get("type", item.get("element_type", item.get("kind")))),
            _text(item.get("text", item.get("content", item.get("value")))), _anchor(item),
            item.get("confidence"), dict(item)), ordinal=ordinal)
        node_by_ordinal[ordinal] = node
        if item.get("parent_ordinal") is not None:
            try:
                pending_parent[ordinal] = int(item["parent_ordinal"])
            except (TypeError, ValueError):
                pass
    for ordinal, parent_ordinal in pending_parent.items():
        node, parent = node_by_ordinal.get(ordinal), node_by_ordinal.get(parent_ordinal)
        if node is not None and parent is not None:
            node.parent_id = parent.node_id
    return document


def from_markitdown(text: str, *, source_name: str, source_sha256: str,
                    page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    """Represent Markdown as evidence; never fabricate page anchors."""
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        value = line.strip()
        if not value:
            continue
        typ = NodeType.SECTION if value.startswith("#") else NodeType.TABLE_ROW if value.startswith("|") else NodeType.PARAGRAPH
        records.append({"type": typ.value, "text": value, "source_line": line_no})
    return from_records(records, source_name=source_name, source_sha256=source_sha256,
                        page_count=page_count, parser="markitdown", version=version)


def from_pypdf_pages(pages: list[str], *, source_name: str, source_sha256: str,
                     version: str = "unknown") -> CanonicalDocument:
    """Create page-aware text observations directly from PDF page boundaries."""
    records: list[dict[str, Any]] = []
    for page_number, text in enumerate(pages, 1):
        records.append({"type": NodeType.PAGE.value, "text": "", "page": page_number})
        for line in text.splitlines():
            value = line.strip()
            if value:
                records.append({"type": NodeType.PARAGRAPH.value, "text": value, "page": page_number})
    return from_records(records, source_name=source_name, source_sha256=source_sha256,
                        page_count=len(pages), parser="pypdf", version=version)


def from_docling_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str,
                         page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    """Adapt Docling-exported records without promoting its classification to truth."""
    return from_records(records, source_name=source_name, source_sha256=source_sha256,
                        page_count=page_count, parser="docling", version=version)


def from_opendataloader_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str,
                                page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    """Adapt OpenDataLoader records without parser-specific semantics leaking into NDI."""
    return from_records(records, source_name=source_name, source_sha256=source_sha256,
                        page_count=page_count, parser="opendataloader", version=version)
