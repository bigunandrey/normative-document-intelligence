from __future__ import annotations

"""Stable contract for parser adapters."""

from dataclasses import dataclass
from typing import Protocol, Sequence

from .canonical import CanonicalDocument


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
