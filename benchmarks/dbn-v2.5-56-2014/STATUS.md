# DBN Benchmark Status

## Verified historical source

The registered DBN V.2.5-56:2014 + Changes 1 and 2 fixture was already executed and verified in the Fire Protection Engine document-ingestion workflow. NDI reuses that completed evidence rather than requiring a duplicate PDF execution.

- SHA-256: `fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056`
- Size: `23,532,218` bytes
- Pages: `105`
- Ingestion workflow run: `34831546595`
- Multi-parser benchmark run: `34839092802`
- MarkItDown: `0.1.7`
- Docling: `2.127.0`
- OpenDataLoader: `2.5.8`

The source PDF is not redistributed by this public repository. The migrated baseline is identified by provenance and SHA-256.

## Current baseline

`MIGRATED-BASELINE.json` is the authoritative migrated record of the completed benchmark evidence. It explicitly records that the measurements were produced in the original repository and are reused here as historical evidence.

The parser measurements are structural/extraction evidence only. They do not establish normative truth.

## Superseded artifact

`result.json` is retained only as a historical pointer and is marked `SUPERSEDED`. Its original `numbered_items` metric was affected by an invalid regular-expression escape in the NDI benchmark runner. The corrected runner is present in `tools/dbn_benchmark.py`, but NDI does not claim a fresh execution of that runner against the PDF.

## Next gate

The next implementation gate is multi-parser structural recognition and reconciliation using the already established DBN evidence:

- parser observations;
- page boundaries and reading order;
- headings, sections, paragraphs and numbered items;
- tables, rows and cells;
- formulas;
- headers and footers;
- provenance;
- explicit cross-parser discrepancies.

No parser is silently promoted to normative truth.
