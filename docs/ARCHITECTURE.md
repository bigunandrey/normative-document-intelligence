# Architecture

## Purpose

Normative Document Intelligence (NDI) is a generic, parser-neutral pipeline for turning normative source documents into structured and traceable digital representations.

## Boundary

NDI answers: what structure and source evidence are present in a document?

Downstream domain projects answer: what does that content mean for engineering or compliance decisions?

## Processing pipeline

```text
SOURCE
  |
  v
INGESTION
  |
  +--> PDF-native extraction
  +--> layout-aware parsing
  +--> OCR / scanned-document fallback
  |
  v
PARSER OBSERVATIONS
  |
  v
CANONICAL DOCUMENT MODEL
  |
  +--> structure
  +--> provenance
  +--> geometry
  +--> reading order
  |
  v
RECONCILIATION
  |
  +--> parser agreement
  +--> parser disagreement
  +--> missing observations
  |
  v
RECOGNITION QUALITY GATE
  |
  +--> PASS
  +--> PASS_WITH_WARNINGS
  +--> FAIL
  |
  v
DIGITAL DOCUMENT REPRESENTATION
```

## Canonical model

The canonical model is intentionally independent of any parser vendor. Nodes represent document structure such as pages, sections, paragraphs, lists, tables, rows, cells, formulas, notes, footnotes, figures, headers and footers.

Each node may carry:

- stable canonical identifier;
- parent and document order;
- source anchor;
- bounding box;
- character span where available;
- raw/source text;
- parser observations;
- parser-specific confidence and attributes.

## Provenance invariant

Every recognized element must remain traceable to source evidence. Missing provenance is a quality defect, not an invitation to infer a location.

## Multi-parser invariant

A parser is an observation source, not a truth source. Agreement between parsers increases evidence quality but does not by itself make content normative.

## Verification boundary

Recognition, reconciliation and provenance are generic. Normative decomposition, semantic rule modeling and domain-specific calculations are downstream layers.

## External engines

NDI can adapt results from engines such as Docling, OpenDataLoader, PyMuPDF, pdfplumber and specialized table/formula recognizers. External engine schemas are adapted into the NDI canonical contract instead of becoming the project source of truth.

## Data flow contract

```text
raw source
  -> parser observation(s)
  -> canonical document
  -> recognition report
  -> downstream consumer
```

No stage may silently overwrite source evidence.
