# Normative Document Intelligence

Open-source framework for converting normative documents into structured, traceable and verifiable digital representations.

## Scope

This repository contains the generic document-intelligence layer for PDF and other normative sources. Domain-specific engineering semantics and calculation engines remain downstream consumers.

## Protocols

- `docs/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md` — source-derived normative process specification, v2.1.
- `docs/NDI-DIGITAL-COPY-OPERATING-PROTOCOL.md` — NDI implementation and user-workflow supplement.
- `docs/IMPLEMENTATION-STATUS-DIGITAL-NORMATIVE-PROTOCOL.md` — current implementation status against the protocol.
- `docs/ROADMAP-DIGITAL-NORMATIVE-DOCUMENT.md` — current roadmap and definition of done.
- `docs/PHASE-9-CLOSURE-2026-09-15.md` — Phase 9 UI-shell closure and explicit remaining boundary.

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

## Digital Copy UI

A dependency-free generic workspace is available through `ndi-ui` (or `python -m`-style integration via `ndi.digital_copy_ui`). It provides PDF intake, persisted job/status inspection, package-local source viewing, graphical-evidence display and an injected workflow-runner boundary. It does not bypass source hashes or acceptance gates.

## Current development strategy

The immediate objective is to finish the **generic PDF → Digital Copy product**, including operational revision/verification workflow, complete generic regression fixtures and reproducible end-to-end execution.

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

The generic engine contracts are substantially implemented and CI-verified. The Phase 9 UI shell is implemented; the current priority is operational revision/verification/handoff lifecycle, followed by generic end-to-end regression. Real-document corpus validation follows these blocks.

## License

TBD.
