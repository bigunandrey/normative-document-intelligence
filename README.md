# Normative Document Intelligence

Open-source framework for converting normative documents into structured, traceable and verifiable digital representations.

## Scope

This repository contains the generic document-intelligence layer for PDF and other normative sources. Domain-specific engineering semantics and calculation engines remain downstream consumers.

## Protocol pipeline

```text
Original source
    ↓
Gate A — multi-parser observations
    ↓
Gate B — reconciliation / discrepancy analysis
    ↓
Gate C — fail-closed structural acceptance
    ↓
Gate D — persisted digital representation + revision hash
    ↓
Gate E — revision / verification evidence
    ↓
Gate F — graphical + external verification evidence
    ↓
Final DIGITAL_ACCEPTED gate
    ↓
Downstream normative/domain layer
```

The executable gate contracts live in `src/ndi/verification.py`; the implementation contract is documented in `docs/VERIFICATION-GATES.md`.

## Principles

- Extraction is evidence, not normative truth.
- Parser disagreement is retained explicitly.
- Every accepted element is traceable to source evidence.
- AI can assist verification but cannot silently promote inferred content to normative truth.
- Quality gates are fail-closed.
- Generic document intelligence is separated from domain-specific engineering logic.

## Current benchmark

The first real fixture is DBN V.2.5-56:2014 with Changes No. 1 and 2. Source PDFs are not redistributed by default; fixtures are referenced by provenance/hash and may be supplied through appropriately licensed storage.

The repository contains the registered fixture identity and historical multi-parser benchmark evidence. Fresh execution against the 105-page fixture requires the licensed PDF to be supplied to the runner.

## Status

The gate infrastructure A-F is implemented. Actual document acceptance remains evidence-driven: the DBN benchmark cannot be marked `DIGITAL_ACCEPTED` until fresh structural execution, graphical verification, external cross-check, independent verification records, regression, register synchronization and revision locking are present.

## License

TBD.
