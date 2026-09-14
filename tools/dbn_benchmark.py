from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import time
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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

    payload = {
        "benchmark": "DBN V.2.5-56:2014 + Changes 1 and 2",
        "source": {
            "filename": args.pdf.name,
            "source_sha256": sha256(args.pdf),
            "size_bytes": args.pdf.stat().st_size,
        },
        "parsers": [benchmark_markitdown(args.pdf)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
