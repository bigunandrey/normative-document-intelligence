# Normative Document Intelligence

Open-source framework for converting normative documents into structured, traceable and verifiable digital representations.

## Scope

This repository contains the generic document-intelligence layer for PDF and other normative sources. Domain-specific engineering semantics and calculation engines remain downstream consumers.

## Protocols

- `docs/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md` — source-derived normative process specification, v2.1.
- `docs/NDI-DIGITAL-COPY-OPERATING-PROTOCOL.md` — NDI implementation and user-workflow supplement.
- `docs/IMPLEMENTATION-STATUS-DIGITAL-NORMATIVE-PROTOCOL.md` — current implementation status against the protocol.
- `docs/ROADMAP-DIGITAL-NORMATIVE-DOCUMENT.md` — current roadmap and definition of done.

## Protocol pipeline

```text
Original source
    ↓
Identity / integrity
    ↓
Multi-parser observations
    ↓
Canonical structure
    ↓
External evidence / comparison
    ↓
Reconciliation / discrepancy resolution
    ↓
Digital Copy semantics / tables / formulas / changes / dependencies
    ↓
Graphical verification
    ↓
Revision lock
    ↓
Independent verification
    ↓
Regression
    ↓
DIGITAL_ACCEPTED
    ↓
Downstream normative/domain layer
```

The executable gate contracts live in `src/ndi/verification.py`; the implementation contract is documented in `docs/VERIFICATION-GATES.md`.

## Current development strategy

The immediate objective is to finish the **generic PDF → Digital Copy product**, including end-to-end orchestration, user interface, graphical verification, evidence/revision workflow, reproducibility and generic regression fixtures.

Real normative documents are intentionally deferred as the primary development driver until that generic block is complete. Afterwards, DBN plus a diverse corpus of other normative documents will be used to expose and prioritize the weakest generic subsystems.

## Principles

- Extraction is evidence, not normative truth.
- Parser disagreement is retained explicitly.
- Every accepted element is traceable to source evidence.
- AI can assist verification but cannot silently promote inferred content to normative truth.
- Quality gates are fail-closed.
- Generic document intelligence is separated from domain-specific engineering logic.

## Current benchmark

The first real fixture is DBN V.2.5-56:2014 with Changes No. 1 and 2. Source PDFs are not redistributed by default; fixtures are referenced by provenance/hash and may be supplied through appropriately licensed storage.

The repository contains the registered fixture identity and historical multi-parser benchmark evidence. Fresh execution against the 105-page fixture is intentionally deferred until the generic Digital Copy workflow is complete.

## Status

The generic semantic and verification contracts are substantially implemented and CI-verified. The remaining priority is product integration: a usable Digital Copy workflow/UI, graphical verification, operational evidence/revision/handoff lifecycle, complete generic regression fixtures and reproducible end-to-end execution. Real-document corpus validation follows these blocks.

## License

TBD.
