from __future__ import annotations

import argparse
from pathlib import Path

from .extractor import extract_pdf, markitdown_version
from .hashing import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a normative PDF as parser evidence.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    extract_pdf(args.pdf, args.output)
    print(f"source_sha256={sha256_file(args.pdf)}")
    print(f"parser=markitdown version={markitdown_version()}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
