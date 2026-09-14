from __future__ import annotations

"""Stable contract for parser adapters."""

from dataclasses import dataclass
from typing import Protocol, Sequence

from .canonical import CanonicalDocument, NodeType


@dataclass(frozen=True)
class AdapterCapabilities:
    pages: bool = True
    reading_order: bool = False
    headings: bool = False
    paragraphs: bool = True
    lists: bool = False
    tables: bool = False
    formulas: bool = False
    headers_footers: bool = False
    notes: bool = False
    figures: bool = False
    geometry: bool = False
    character_spans: bool = False


class ParserAdapter(Protocol):
    name: str
    version: str
    capabilities: AdapterCapabilities

    def adapt(self, source: object, *, source_name: str, source_sha256: str, page_count: int | None = None) -> CanonicalDocument:
        """Convert parser output to canonical evidence without semantic correction."""
        ...


def validate_adapter_capabilities(adapters: Sequence[ParserAdapter]) -> dict[str, AdapterCapabilities]:
    """Return the declared capabilities, rejecting duplicate parser names."""
    result: dict[str, AdapterCapabilities] = {}
    for adapter in adapters:
        if not adapter.name or not adapter.version:
            raise ValueError("Parser adapter name and version are required")
        if adapter.name in result:
            raise ValueError(f"Duplicate parser adapter: {adapter.name}")
        result[adapter.name] = adapter.capabilities
    return result


def validate_adapter_output(document: CanonicalDocument, *, parser: str, version: str) -> None:
    """Fail closed if an adapter violates the canonical observation contract."""
    if document.source_sha256 == "" or len(document.source_sha256) != 64:
        raise ValueError(f"{parser}: invalid source SHA-256")
    if document.parser_versions.get(parser) != version:
        raise ValueError(f"{parser}: parser version is not bound to the document")
    if parser not in document.parser_versions:
        raise ValueError(f"{parser}: parser provenance is missing")

    expected_orders = list(range(len(document.nodes)))
    actual_orders = [node.order for node in document.nodes]
    if sorted(actual_orders) != expected_orders:
        raise ValueError(f"{parser}: node order is not contiguous and unique")

    valid_types = set(NodeType)
    for node in document.nodes:
        if node.node_type not in valid_types:
            raise ValueError(f"{parser}: invalid node type")
        if node.anchor and document.page_count is not None and node.anchor.page is not None:
            if node.anchor.page < 1 or node.anchor.page > document.page_count:
                raise ValueError(f"{parser}: node anchor page is outside document bounds")
        if node.anchor and node.anchor.char_start is not None and node.anchor.char_end is not None:
            if node.anchor.char_start < 0 or node.anchor.char_end < node.anchor.char_start:
                raise ValueError(f"{parser}: invalid character span")
        if not node.observations:
            raise ValueError(f"{parser}: canonical node has no parser observation")
        for observation in node.observations:
            if observation.parser != parser or observation.parser_version != version:
                raise ValueError(f"{parser}: node contains unbound parser observation")
            if observation.node_type != node.node_type:
                raise ValueError(f"{parser}: observation/node type mismatch")
            if observation.confidence is not None and not 0.0 <= observation.confidence <= 1.0:
                raise ValueError(f"{parser}: confidence must be between 0 and 1")

    for node in document.nodes:
        if node.parent_id is not None and not any(parent.node_id == node.parent_id for parent in document.nodes):
            raise ValueError(f"{parser}: node references missing parent")
