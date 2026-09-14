from __future__ import annotations

"""Registered, deterministic execution path for parser adapters."""

from dataclasses import dataclass
from typing import Any, Callable

from .adapter_contract import AdapterCapabilities, ParserAdapter, validate_adapter_capabilities
from .adapters import (
    from_docling_records,
    from_markitdown,
    from_opendataloader_records,
    from_pypdf_pages,
)
from .canonical import CanonicalDocument


@dataclass(frozen=True)
class RegisteredAdapter:
    """Concrete adapter binding parser identity, capabilities and adaptation."""

    name: str
    version: str
    capabilities: AdapterCapabilities
    _adapt: Callable[..., CanonicalDocument]

    def adapt(
        self,
        source: Any,
        *,
        source_name: str,
        source_sha256: str,
        page_count: int | None = None,
    ) -> CanonicalDocument:
        return self._adapt(
            source,
            source_name=source_name,
            source_sha256=source_sha256,
            page_count=page_count,
            version=self.version,
        )


def default_adapters(
    *,
    markitdown_version: str = "unknown",
    pypdf_version: str = "unknown",
    docling_version: str = "unknown",
    opendataloader_version: str = "unknown",
) -> tuple[ParserAdapter, ...]:
    """Return the configured parser set in stable order."""
    return (
        RegisteredAdapter(
            "markitdown", markitdown_version,
            AdapterCapabilities(
                pages=False, reading_order=True, headings=True, paragraphs=True,
                tables=True, geometry=False,
            ),
            from_markitdown,
        ),
        RegisteredAdapter(
            "pypdf", pypdf_version,
            AdapterCapabilities(pages=True, paragraphs=True),
            lambda pages, **kwargs: from_pypdf_pages(pages, **kwargs),
        ),
        RegisteredAdapter(
            "docling", docling_version,
            AdapterCapabilities(
                pages=True, reading_order=True, headings=True, paragraphs=True,
                lists=True, tables=True, formulas=True, headers_footers=True,
                notes=True, figures=True, geometry=True, character_spans=True,
            ),
            from_docling_records,
        ),
        RegisteredAdapter(
            "opendataloader", opendataloader_version,
            AdapterCapabilities(
                pages=True, reading_order=True, headings=True, paragraphs=True,
                lists=True, tables=True, formulas=True, headers_footers=True,
                notes=True, figures=True, geometry=True, character_spans=True,
            ),
            from_opendataloader_records,
        ),
    )


def adapt_registered(
    adapter: ParserAdapter,
    source: Any,
    *,
    source_name: str,
    source_sha256: str,
    page_count: int | None = None,
) -> CanonicalDocument:
    """Execute one registered adapter while preserving parser evidence verbatim."""
    validate_adapter_capabilities((adapter,))
    return adapter.adapt(
        source,
        source_name=source_name,
        source_sha256=source_sha256,
        page_count=page_count,
    )


def validate_default_adapters(adapters: tuple[ParserAdapter, ...] | None = None) -> dict[str, AdapterCapabilities]:
    """Validate the configured parser set and return its capability manifest."""
    return validate_adapter_capabilities(adapters or default_adapters())
