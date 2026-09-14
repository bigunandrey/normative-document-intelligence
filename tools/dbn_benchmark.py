from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Record DBN fixture provenance for NDI benchmark runs.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("benchmark-report.json"))
    args = parser.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"Fixture not found: {args.pdf}")
    payload = {
        "fixture": args.pdf.name,
        "source_sha256": sha256(args.pdf),
        "size_bytes": args.pdf.stat().st_size,
        "status": "SOURCE_REGISTERED",
        "note": "Structural parser benchmark execution is implemented in the next benchmark phase.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
