from __future__ import annotations

"""Evidence-only adapters for common parser record shapes."""

from collections.abc import Mapping
from typing import Any

from .canonical import BoundingBox, CanonicalDocument, NodeType, SourceAnchor, stable_document_id
from .observations import RawObservation, add_observation


_LOCAL_PARENT = "_local_parent_ordinal"


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


def _provenance(item: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = item.get("prov", item.get("provenance"))
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, (list, tuple)):
        return [entry for entry in value if isinstance(entry, Mapping)]
    return []


def _page(item: Mapping[str, Any]) -> int | None:
    for key in ("page", "page_no", "page_number", "pageNo", "page_num", "page_index"):
        if key in item:
            try:
                value = int(item[key])
                return value + 1 if key == "page_index" and value >= 0 else value
            except (TypeError, ValueError):
                return None
    for provenance in _provenance(item):
        page = _page(provenance)
        if page is not None:
            return page
    return None


def _anchor(item: Mapping[str, Any]) -> SourceAnchor:
    bbox = _bbox(item)
    if bbox is None:
        for provenance in _provenance(item):
            bbox = _bbox(provenance)
            if bbox is not None:
                break
    char_start = item.get("char_start")
    char_end = item.get("char_end")
    if char_start is None or char_end is None:
        for provenance in _provenance(item):
            char_start = provenance.get("char_start", char_start)
            char_end = provenance.get("char_end", char_end)
    return SourceAnchor(page=_page(item), bbox=bbox, char_start=char_start, char_end=char_end)


def _node_type(value: Any) -> NodeType:
    raw = str(value or "").lower().replace("-", "_").replace(" ", "_")
    return {
        "document": NodeType.DOCUMENT,
        "page": NodeType.PAGE,
        "text": NodeType.PARAGRAPH,
        "paragraph": NodeType.PARAGRAPH,
        "heading": NodeType.SECTION,
        "title": NodeType.SECTION,
        "section": NodeType.SECTION,
        "list": NodeType.LIST,
        "list_item": NodeType.LIST_ITEM,
        "table": NodeType.TABLE,
        "row": NodeType.TABLE_ROW,
        "table_row": NodeType.TABLE_ROW,
        "cell": NodeType.TABLE_CELL,
        "table_cell": NodeType.TABLE_CELL,
        "formula": NodeType.FORMULA,
        "equation": NodeType.FORMULA,
        "note": NodeType.NOTE,
        "footnote": NodeType.FOOTNOTE,
        "figure": NodeType.FIGURE,
        "image": NodeType.FIGURE,
        "header": NodeType.HEADER,
        "footer": NodeType.FOOTER,
    }.get(raw, NodeType.UNKNOWN)


def new_document(source_name: str, source_sha256: str, page_count: int | None, parser: str, version: str) -> CanonicalDocument:
    return CanonicalDocument(
        document_id=stable_document_id(source_sha256),
        source_name=source_name,
        source_sha256=source_sha256,
        page_count=page_count,
        parser_versions={parser: version},
    )


def _expand_structural_record(item: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Expand nested structures with explicit local parent references."""
    result: list[Mapping[str, Any]] = [dict(item)]
    typ = _node_type(item.get("type", item.get("element_type", item.get("kind"))))
    if typ == NodeType.TABLE:
        rows = item.get("rows", item.get("children", ()))
        if isinstance(rows, (list, tuple)):
            for row in rows:
                row_data = dict(row) if isinstance(row, Mapping) else {"text": _text(row)}
                row_data.setdefault("type", NodeType.TABLE_ROW.value)
                row_data.setdefault("page", _page(item))
                row_data.setdefault(_LOCAL_PARENT, 0)
                result.append(row_data)
                row_ordinal = len(result) - 1
                cells = row_data.get("cells", row_data.get("children", ()))
                if isinstance(cells, (list, tuple)):
                    for cell in cells:
                        cell_data = dict(cell) if isinstance(cell, Mapping) else {"text": _text(cell)}
                        cell_data.setdefault("type", NodeType.TABLE_CELL.value)
                        cell_data.setdefault("page", _page(row_data))
                        cell_data.setdefault(_LOCAL_PARENT, row_ordinal)
                        result.append(cell_data)
    elif typ == NodeType.LIST:
        items = item.get("items", item.get("children", ()))
        if isinstance(items, (list, tuple)):
            for child in items:
                child_data = dict(child) if isinstance(child, Mapping) else {"text": _text(child)}
                child_data.setdefault("type", NodeType.LIST_ITEM.value)
                child_data.setdefault("page", _page(item))
                child_data.setdefault(_LOCAL_PARENT, 0)
                result.append(child_data)
    return result


def from_records(
    records: list[Mapping[str, Any]],
    *,
    source_name: str,
    source_sha256: str,
    page_count: int | None,
    parser: str,
    version: str,
) -> CanonicalDocument:
    document = new_document(source_name, source_sha256, page_count, parser, version)
    expanded: list[Mapping[str, Any]] = []
    parent_refs: dict[int, int] = {}
    for item in records:
        start = len(expanded)
        for child in _expand_structural_record(item):
            child_data = dict(child)
            local_parent = child_data.pop(_LOCAL_PARENT, None)
            ordinal = len(expanded)
            expanded.append(child_data)
            if local_parent is not None:
                parent_refs[ordinal] = start + int(local_parent)
            elif child_data.get("parent_ordinal") is not None:
                try:
                    parent_refs[ordinal] = int(child_data["parent_ordinal"])
                except (TypeError, ValueError):
                    pass

    for ordinal, item in enumerate(expanded):
        add_observation(
            document,
            RawObservation(
                parser,
                version,
                _node_type(item.get("type", item.get("element_type", item.get("kind")))),
                _text(item.get("text", item.get("content", item.get("value")))),
                _anchor(item),
                item.get("confidence"),
                dict(item),
            ),
            ordinal=ordinal,
        )

    for ordinal, parent_ordinal in parent_refs.items():
        if 0 <= ordinal < len(document.nodes) and 0 <= parent_ordinal < len(document.nodes) and ordinal != parent_ordinal:
            document.nodes[ordinal].parent_id = document.nodes[parent_ordinal].node_id
    return document


def from_markitdown(text: str, *, source_name: str, source_sha256: str, page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    records = []
    for line_no, line in enumerate(text.splitlines(), 1):
        value = line.strip()
        if value:
            records.append({
                "type": NodeType.SECTION.value if value.startswith("#") else NodeType.TABLE_ROW.value if value.startswith("|") else NodeType.PARAGRAPH.value,
                "text": value,
                "source_line": line_no,
            })
    return from_records(records, source_name=source_name, source_sha256=source_sha256, page_count=page_count, parser="markitdown", version=version)


def from_pypdf_pages(pages: list[str], *, source_name: str, source_sha256: str, version: str = "unknown", page_count: int | None = None) -> CanonicalDocument:
    records = []
    for page_number, text in enumerate(pages, 1):
        records.append({"type": NodeType.PAGE.value, "text": "", "page": page_number})
        records.extend({"type": NodeType.PARAGRAPH.value, "text": value, "page": page_number} for value in (line.strip() for line in text.splitlines()) if value)
    return from_records(records, source_name=source_name, source_sha256=source_sha256, page_count=len(pages), parser="pypdf", version=version)


def from_docling_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str, page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    return from_records(records, source_name=source_name, source_sha256=source_sha256, page_count=page_count, parser="docling", version=version)


def from_opendataloader_records(records: list[Mapping[str, Any]], *, source_name: str, source_sha256: str, page_count: int | None, version: str = "unknown") -> CanonicalDocument:
    return from_records(records, source_name=source_name, source_sha256=source_sha256, page_count=page_count, parser="opendataloader", version=version)
