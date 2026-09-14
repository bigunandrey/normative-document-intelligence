from __future__ import annotations

"""Fail-closed structural recognition quality gate.

This module validates the integrity of the canonical representation only. It
never decides whether extracted content is normatively correct.
"""

from dataclasses import dataclass, field
from enum import StrEnum
import re

from .canonical import CanonicalDocument, CanonicalNode


class Quality(StrEnum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class RecognitionIssue:
    code: str
    message: str
    node_id: str | None = None
    severity: str = "ERROR"


@dataclass
class RecognitionAudit:
    quality: Quality
    issues: list[RecognitionIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.quality != Quality.FAIL

    @property
    def errors(self) -> list[RecognitionIssue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> list[RecognitionIssue]:
        return [i for i in self.issues if i.severity == "WARNING"]


def _valid_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{64}", value or ""))


def _cycle_nodes(nodes_by_id: dict[str, CanonicalNode]) -> set[str]:
    cyclic: set[str] = set()
    for start in nodes_by_id:
        path: list[str] = []
        seen: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in seen:
                cyclic.update(path[path.index(current):])
                break
            seen.add(current)
            path.append(current)
            node = nodes_by_id.get(current)
            if node is None:
                break
            current = node.parent_id
    return cyclic


def audit_document(
    document: CanonicalDocument,
    *,
    require_page_anchors: bool = True,
    require_observations: bool = True,
    require_order: bool = True,
) -> RecognitionAudit:
    """Audit structural integrity and provenance completeness.

    The result is fail-closed: structural/provenance defects are FAIL; absent
    optional evidence such as bbox, character spans, or confidence is a warning.
    """
    issues: list[RecognitionIssue] = []

    if not _valid_sha256(document.source_sha256):
        issues.append(RecognitionIssue("INVALID_SOURCE_HASH", "source_sha256 is not a valid SHA-256 digest"))
    if not document.nodes:
        issues.append(RecognitionIssue("NO_NODES", "canonical document contains no nodes"))
        return RecognitionAudit(Quality.FAIL, issues)

    nodes_by_id: dict[str, CanonicalNode] = {}
    for node in document.nodes:
        if node.node_id in nodes_by_id:
            issues.append(RecognitionIssue("DUPLICATE_NODE_ID", "duplicate canonical node id", node.node_id))
        else:
            nodes_by_id[node.node_id] = node

    for node in document.nodes:
        if node.parent_id is not None and node.parent_id not in nodes_by_id:
            issues.append(RecognitionIssue("BROKEN_PARENT", f"parent {node.parent_id!r} does not exist", node.node_id))
        if require_page_anchors and node.node_type.value != "document":
            if node.anchor is None or node.anchor.page is None or node.anchor.page < 1:
                issues.append(RecognitionIssue("MISSING_PAGE_ANCHOR", "node lacks a valid page anchor", node.node_id))
        if require_observations and not node.observations:
            issues.append(RecognitionIssue("MISSING_OBSERVATION", "node has no parser observation", node.node_id))
        if require_order and not isinstance(node.order, int):
            issues.append(RecognitionIssue("INVALID_ORDER", "node order must be an integer", node.node_id))
        if node.anchor is not None:
            if node.anchor.char_start is None or node.anchor.char_end is None:
                issues.append(RecognitionIssue("MISSING_CHAR_SPAN", "character span is absent", node.node_id, "WARNING"))
            if node.anchor.bbox is None:
                issues.append(RecognitionIssue("MISSING_BBOX", "bounding box is absent", node.node_id, "WARNING"))
        for observation in node.observations:
            if observation.confidence is None:
                issues.append(RecognitionIssue("MISSING_CONFIDENCE", "parser confidence is absent", node.node_id, "WARNING"))

    for node_id in sorted(_cycle_nodes(nodes_by_id)):
        issues.append(RecognitionIssue("PARENT_CYCLE", "parent hierarchy contains a cycle", node_id))

    # Orders must be unique within each parent scope. Equal orders make reading
    # order ambiguous and therefore fail the recognition gate.
    if require_order:
        by_parent: dict[str | None, list[CanonicalNode]] = {}
        for node in document.nodes:
            by_parent.setdefault(node.parent_id, []).append(node)
        for parent_id, siblings in by_parent.items():
            seen_orders: dict[int, str] = {}
            for node in siblings:
                if node.order in seen_orders:
                    issues.append(RecognitionIssue("DUPLICATE_ORDER", "sibling nodes have the same order", node.node_id))
                else:
                    seen_orders[node.order] = node.node_id

    if any(i.severity == "ERROR" for i in issues):
        quality = Quality.FAIL
    elif issues:
        quality = Quality.PASS_WITH_WARNINGS
    else:
        quality = Quality.PASS
    return RecognitionAudit(quality, issues)
