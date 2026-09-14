from __future__ import annotations

"""Conservative deterministic cross-parser comparison."""

from collections import defaultdict
import re
import unicodedata
from typing import Any

from .canonical import CanonicalDocument, CanonicalNode, NodeType


def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", value).strip()


def _anchor_key(node: CanonicalNode) -> tuple[Any, ...] | None:
    anchor = node.anchor
    if anchor is None or anchor.page is None:
        return None
    if anchor.bbox is None:
        return (anchor.page,)
    bbox = anchor.bbox
    return (anchor.page, round(bbox.left, 2), round(bbox.top, 2), round(bbox.right, 2), round(bbox.bottom, 2))


def match_nodes(left: CanonicalDocument, right: CanonicalDocument) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    right_by_anchor: dict[tuple[Any, ...], list[CanonicalNode]] = defaultdict(list)
    right_by_text: dict[tuple[int | None, str, str], list[CanonicalNode]] = defaultdict(list)
    for node in right.nodes:
        anchor_key = _anchor_key(node)
        if anchor_key is not None:
            right_by_anchor[anchor_key].append(node)
        right_by_text[(node.anchor.page if node.anchor else None, node.node_type.value, normalize_text(node.text))].append(node)

    used: set[str] = set()
    for node in left.nodes:
        candidate = None
        anchor_key = _anchor_key(node)
        if anchor_key is not None:
            candidate = next(
                (item for item in right_by_anchor[anchor_key] if item.node_id not in used and item.node_type == node.node_type),
                None,
            )
        if candidate is None and normalize_text(node.text):
            text_key = (node.anchor.page if node.anchor else None, node.node_type.value, normalize_text(node.text))
            candidate = next((item for item in right_by_text[text_key] if item.node_id not in used), None)
        if candidate is not None:
            matches.append((node.node_id, candidate.node_id))
            used.add(candidate.node_id)
    return matches


def _parent_type(document: CanonicalDocument, node: CanonicalNode) -> str | None:
    if node.parent_id is None:
        return None
    try:
        return document.node(node.parent_id).node_type.value
    except KeyError:
        return "UNKNOWN_PARENT"


def _child_signature(document: CanonicalDocument, node: CanonicalNode) -> tuple[str, ...]:
    return tuple(child.node_type.value for child in document.children(node.node_id))


def compare_documents(left: CanonicalDocument, right: CanonicalDocument) -> list[dict[str, Any]]:
    pairs = match_nodes(left, right)
    left_ids = {left_id for left_id, _ in pairs}
    right_ids = {right_id for _, right_id in pairs}
    left_by_id = {node.node_id: node for node in left.nodes}
    right_by_id = {node.node_id: node for node in right.nodes}
    discrepancies: list[dict[str, Any]] = []

    for left_id, right_id in pairs:
        left_node = left_by_id[left_id]
        right_node = right_by_id[right_id]
        if normalize_text(left_node.text) != normalize_text(right_node.text):
            discrepancies.append({"class": "TEXT_MISMATCH", "left": left_id, "right": right_id, "status": "REVIEW_REQUIRED"})
        if _anchor_key(left_node) != _anchor_key(right_node):
            discrepancies.append({"class": "ANCHOR_MISMATCH", "left": left_id, "right": right_id, "status": "REVIEW_REQUIRED"})
        if _parent_type(left, left_node) != _parent_type(right, right_node):
            discrepancies.append(
                {
                    "class": "STRUCTURE_MISMATCH",
                    "left": left_id,
                    "right": right_id,
                    "left_parent_type": _parent_type(left, left_node),
                    "right_parent_type": _parent_type(right, right_node),
                    "status": "REVIEW_REQUIRED",
                }
            )
        if left_node.node_type == NodeType.TABLE and _child_signature(left, left_node) != _child_signature(right, right_node):
            discrepancies.append(
                {
                    "class": "TABLE_MISMATCH",
                    "left": left_id,
                    "right": right_id,
                    "left_children": _child_signature(left, left_node),
                    "right_children": _child_signature(right, right_node),
                    "status": "REVIEW_REQUIRED",
                }
            )

    for node in left.nodes:
        if node.node_id not in left_ids:
            discrepancies.append({"class": "MISSING_OBSERVATION", "side": "right", "node_id": node.node_id, "status": "REVIEW_REQUIRED"})
    for node in right.nodes:
        if node.node_id not in right_ids:
            discrepancies.append({"class": "MISSING_OBSERVATION", "side": "left", "node_id": node.node_id, "status": "REVIEW_REQUIRED"})
    return discrepancies
