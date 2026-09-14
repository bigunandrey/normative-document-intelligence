from __future__ import annotations

import importlib.metadata
from pathlib import Path


class ExtractionError(RuntimeError):
    """Raised when MarkItDown is unavailable or conversion fails."""


def markitdown_version() -> str:
    try:
        return importlib.metadata.version("markitdown")
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


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
