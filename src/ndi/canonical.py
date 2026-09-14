from __future__ import annotations

"""Parser-neutral canonical structural model."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import hashlib
import json
from typing import Any


class NodeType(StrEnum):
    DOCUMENT = "document"
    PAGE = "page"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    FORMULA = "formula"
    NOTE = "note"
    FOOTNOTE = "footnote"
    FIGURE = "figure"
    HEADER = "header"
    FOOTER = "footer"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BoundingBox:
    left: float
    top: float
    right: float
    bottom: float


@dataclass(frozen=True)
class SourceAnchor:
    page: int | None = None
    bbox: BoundingBox | None = None
    char_start: int | None = None
    char_end: int | None = None
    source_fragment: str | None = None


@dataclass(frozen=True)
class ParserObservation:
    parser: str
    parser_version: str
    observation_id: str
    node_type: NodeType
    text: str = ""
    anchor: SourceAnchor | None = None
    confidence: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalNode:
    node_id: str
    node_type: NodeType
    text: str = ""
    parent_id: str | None = None
    order: int = 0
    anchor: SourceAnchor | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    observations: list[ParserObservation] = field(default_factory=list)

    def add_observation(self, observation: ParserObservation) -> None:
        if observation.observation_id not in {o.observation_id for o in self.observations}:
            self.observations.append(observation)


@dataclass
class CanonicalDocument:
    document_id: str
    source_name: str
    source_sha256: str
    page_count: int | None
    nodes: list[CanonicalNode] = field(default_factory=list)
    parser_versions: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: CanonicalNode) -> None:
        if any(existing.node_id == node.node_id for existing in self.nodes):
            raise ValueError(f"Duplicate canonical node id: {node.node_id}")
        self.nodes.append(node)

    def node(self, node_id: str) -> CanonicalNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(node_id)

    def children(self, parent_id: str | None) -> list[CanonicalNode]:
        return sorted(
            (node for node in self.nodes if node.parent_id == parent_id),
            key=lambda node: (node.order, node.node_id),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def stable_document_id(source_sha256: str) -> str:
    if len(source_sha256) != 64:
        raise ValueError("source_sha256 must be a SHA-256 hexadecimal digest")
    int(source_sha256, 16)
    return f"doc-{source_sha256[:16]}"


def stable_node_id(document_id: str, node_type: NodeType, anchor: SourceAnchor | None, ordinal: int) -> str:
    payload = json.dumps(
        {
            "document": document_id,
            "type": node_type.value,
            "page": anchor.page if anchor else None,
            "char_start": anchor.char_start if anchor else None,
            "char_end": anchor.char_end if anchor else None,
            "ordinal": ordinal,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"node-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"
