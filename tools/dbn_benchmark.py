from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import time
from pathlib import Path

EXPECTED_SHA256 = "fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056"
EXPECTED_SIZE_BYTES = 23_532_218
EXPECTED_PAGE_COUNT = 105


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_count(source: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(source)).pages)


def benchmark_markitdown(source: Path) -> dict[str, object]:
    from markitdown import MarkItDown

    started = time.perf_counter()
    result = MarkItDown().convert(str(source))
    elapsed = time.perf_counter() - started
    text = getattr(result, "markdown", None) or getattr(result, "text_content", None) or ""
    lines = text.splitlines()
    return {
        "parser": "MarkItDown",
        "version": importlib.metadata.version("markitdown"),
        "elapsed_seconds": round(elapsed, 3),
        "characters": len(text),
        "lines": len(lines),
        "headings": len(re.findall(r"(?m)^#{1,6}\\s+", text)),
        "table_like_lines": sum("|" in line for line in lines),
        "numbered_items": len(re.findall(r"(?m)^\\s*\\d+(?:\\.\\d+)*[.)]\\s+", text)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the DBN parser benchmark for NDI.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("benchmark-report.json"))
    args = parser.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"Fixture not found: {args.pdf}")

    source_digest = sha256(args.pdf)
    source_size = args.pdf.stat().st_size
    pages = page_count(args.pdf)
    if source_digest != EXPECTED_SHA256 or source_size != EXPECTED_SIZE_BYTES or pages != EXPECTED_PAGE_COUNT:
        raise SystemExit(
            "DBN fixture identity mismatch: "
            f"sha256={source_digest}, size={source_size}, pages={pages}; "
            "expected the registered DBN V.2.5-56:2014 fixture."
        )

    payload = {
        "benchmark": "DBN V.2.5-56:2014 + Changes 1 and 2",
        "source": {
            "filename": args.pdf.name,
            "source_sha256": source_digest,
            "size_bytes": source_size,
            "page_count": pages,
            "identity_verified": True,
        },
        "parsers": [benchmark_markitdown(args.pdf)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
