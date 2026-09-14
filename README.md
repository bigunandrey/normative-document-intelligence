# Normative Document Intelligence

Open-source framework for converting normative documents into structured, traceable and verifiable digital representations.

## Scope

This repository contains the generic document-intelligence layer for PDF and other normative sources. Domain-specific engineering semantics and calculation engines remain downstream consumers.

## Pipeline

```text
Original source
    ↓
Multi-parser ingestion
    ↓
Canonical structural document model
    ↓
Structural recognition audit
    ↓
Parser reconciliation / discrepancy analysis
    ↓
Verified digital representation
```

## Principles

- Extraction is evidence, not normative truth.
- Parser disagreement is retained explicitly.
- Every accepted element is traceable to source evidence.
- AI can assist verification but cannot silently promote inferred content to normative truth.
- Quality gates are fail-closed.
- Generic document intelligence is separated from domain-specific engineering logic.

## Current benchmark

The first real fixture is DBN V.2.5-56:2014 with Changes No. 1 and 2. Source PDFs are not redistributed by default; fixtures are referenced by provenance/hash and may be supplied through appropriately licensed storage.

## Status

Early development.

## License

TBD.
