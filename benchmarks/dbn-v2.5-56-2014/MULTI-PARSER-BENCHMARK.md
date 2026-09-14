# DBN V.2.5-56:2014 Multi-Parser Benchmark

## Objective

Compare independent document parsers on the same verified DBN fixture before any normative semantics are inferred.

## Registered source

- Document: DBN V.2.5-56:2014 + Changes 1 and 2
- SHA-256: `fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056`
- Size: `23,532,218` bytes
- Pages: `105`

## Parser set

The benchmark is intentionally multi-engine. The first established baseline is MarkItDown. Subsequent adapters should add observations for engines such as Docling, OpenDataLoader PDF, PyMuPDF and pdfplumber where their licenses and runtime characteristics are suitable.

No parser is treated as normative truth.

## Metrics

### Extraction metrics

- elapsed time
- extracted character count
- line count
- headings
- numbered items
- table-like structures

### Structural metrics

- page boundaries
- section hierarchy
- paragraph/list recognition
- table detection
- table row/cell reconstruction
- formula detection
- header/footer separation
- reading order

### Evidence metrics

Every accepted structural node must retain, where available:

- source page
- bounding box
- character span
- raw text
- parser identity and version
- parser confidence/attributes
- reconciliation status

## Cross-parser policy

Disagreement is evidence. It must be retained and surfaced, not silently resolved by selecting one parser.

The benchmark therefore distinguishes:

1. parser observation;
2. canonical structural representation;
3. reconciliation decision;
4. recognition quality result.

A structural disagreement does not by itself establish that any parser is correct or incorrect.

## Next implementation target

Implement parser adapters that emit `ParserObservation` records into the existing canonical model, then produce a machine-readable discrepancy report for the DBN fixture.
