# DBN V.2.5-56:2014 benchmark

## Fixture identity

The registered fixture is the DBN V.2.5-56:2014 PDF with Changes 1 and 2.

- SHA-256: `fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a505`
- Size: `23,532,218` bytes
- Pages: `105`

The source PDF is not committed to this public repository. The identity is verified by provenance/hash when the fixture is supplied to a runner.

## Migrated benchmark evidence

This repository inherits the completed benchmark evidence from the Fire Protection Engine document-ingestion work. The PDF does **not** need to be executed again merely to populate NDI: the historical evidence is preserved in `MIGRATED-BASELINE.json` with its source workflow run IDs.

| Parser | Version | Time (s) | Characters | Lines | Headings | Table-like lines | Numbered items |
|---|---:|---:|---:|---:|---:|---:|---:|
| MarkItDown | 0.1.7 | 8.898 | 491,675 | 6,388 | 0 | 3,351 | 16 |
| Docling | 2.127.0 | 1438.329 | 328,429 | 3,637 | 262 | 659 | 98 |
| OpenDataLoader | 2.5.8 | 6.787 | 243,067 | 5,320 | 40 | 0 | 14 |

These values are **historical migrated evidence**, not measurements produced by a fresh NDI execution. They are retained as the established baseline for the next structural-recognition stage.

## NDI runner

The repository also contains `tools/dbn_benchmark.py`. It verifies fixture identity and can produce a new MarkItDown extraction report when a licensed copy of the fixture is supplied. A newly generated report must not overwrite the migrated historical baseline.

## Recognition boundary

The benchmark is concerned with document structure and evidence: page boundaries, reading order, headings/sections, paragraphs and lists, tables/cells, formulas, headers/footers, provenance, and parser disagreement. Normative semantics and engineering calculations remain outside NDI.
