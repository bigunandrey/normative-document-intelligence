from __future__ import annotations

import importlib.metadata
from pathlib import Path


class ExtractionError(RuntimeError):
    """Raised when an extraction engine is unavailable or conversion fails."""


def markitdown_version() -> str:
    try:
        return importlib.metadata.version("markitdown")
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def pypdf_version() -> str:
    try:
        return importlib.metadata.version("pypdf")
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def pdf_page_text(source: Path) -> list[str]:
    """Extract one raw text stream per PDF page; page numbers are native evidence."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ExtractionError("pypdf is not installed") from exc
    try:
        return [(page.extract_text() or "") for page in PdfReader(str(source)).pages]
    except Exception as exc:
        raise ExtractionError(f"pypdf extraction failed: {exc}") from exc


def extract_pdf(source: Path, output: Path) -> str:
    """Convert a PDF to Markdown without silently changing extraction engines."""
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise ExtractionError("MarkItDown is not installed. Install with: pip install 'markitdown[pdf]'") from exc
    try:
        result = MarkItDown().convert(str(source))
        markdown = getattr(result, "markdown", None) or getattr(result, "text_content", None)
        if not markdown:
            raise ExtractionError("MarkItDown returned empty Markdown output")
    except Exception as exc:
        raise ExtractionError(f"MarkItDown conversion failed: {exc}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    return markdown


def extract_pdf_evidence(source: Path, markdown_output: Path, pages_output: Path) -> dict[str, object]:
    """Run MarkItDown and pypdf while preserving independent evidence artifacts."""
    markdown = extract_pdf(source, markdown_output)
    pages = pdf_page_text(source)
    pages_output.parent.mkdir(parents=True, exist_ok=True)
    pages_output.write_text("\n\n".join(f"=== PAGE {i} ===\n{text}" for i, text in enumerate(pages, 1)), encoding="utf-8")
    return {"source": str(source), "markitdown_version": markitdown_version(), "pypdf_version": pypdf_version(), "page_count": len(pages), "markdown_output": str(markdown_output), "pages_output": str(pages_output), "markdown_characters": len(markdown)}
