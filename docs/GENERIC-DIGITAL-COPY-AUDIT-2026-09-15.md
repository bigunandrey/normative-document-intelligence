# Generic PDF → Digital Copy Audit

**Date:** 2026-09-15  
**Repository:** `bigunandrey/normative-document-intelligence`  
**Branch:** `main`  
**Purpose:** Production-readiness audit of the generic NDI Digital Copy subsystem before real normative-corpus validation.

## Executive result

The repository contains substantial, CI-tested generic contracts for identity, source binding, canonical structure, parser adapters, reconciliation, external-source comparison, graphical-verification validation, revision locking, independent verification and semantic representation.

The persistence boundary has now been hardened: Digital Copy packages can be created as self-contained packages, source/artifact hashes are verified, package-local paths are rebound on replay, and replay no longer depends on the original source/artifact locations.

The remaining critical gap is integration: the repository does not yet contain a production Digital Copy application workflow that takes a user PDF through one orchestrated job/package lifecycle to final acceptance, nor a user-facing web UI.

## Pipeline audit

| Block | Status | Evidence / finding | Required action |
|---|---|---|---|
| PDF INPUT | PARTIAL | CLI accepts a PDF path, but there is no user-facing intake/job lifecycle. | Add production intake API/service and persisted job creation. |
| IDENTITY | COMPLETE CORE / NOT ORCHESTRATED | `DocumentIdentity`, source registry and revision binding exist. | Integrate into intake workflow and lifecycle. |
| SOURCE INTEGRITY | COMPLETE CORE / NOT ORCHESTRATED | SHA-256 binding and revision lock exist; package-local source persistence is now implemented. | Integrate into complete job lifecycle and expose status. |
| EXTRACTION | PARTIAL | MarkItDown/pypdf plus adapter contracts exist; extraction is not unified into one production run. | Build orchestrated extraction stage and persistent extraction log. |
| PARSER REGISTRY | COMPLETE | Registry, contracts and default adapters exist. | Integrate runtime failure/availability states into job model. |
| ADAPTERS | COMPLETE CORE | MarkItDown, pypdf, Docling, OpenDataLoader adapters are present. | Add end-to-end fixtures for adapter failure/degraded cases. |
| OBSERVATIONS | COMPLETE CORE | Canonical observations and deterministic observation artifacts exist. | Persist package artifacts per job. |
| CANONICAL MODEL | COMPLETE CORE | Canonical node model includes structural nodes, anchors, provenance and parser metadata. | Add integration-level validation through full workflow. |
| STRUCTURE | PARTIAL | Structural gates and reconciliation exist. | Produce user-visible structural result/evidence bundle. |
| TABLES | PARTIAL | Table/cell nodes and rule-registry primitives exist. | Add robust reconstruction fixtures + visual evidence workflow. |
| FORMULAS | PARTIAL | Formula node/registry primitives exist. | Add graphical evidence and extraction fixtures for formulas/symbols. |
| READING ORDER | WEAK / NOT EXPLICITLY CONTRACTED | Canonical `order` exists, but no dedicated reading-order validation/reconciliation contract was found in the audit. | Add explicit reading-order evidence model, validators and fixtures. |
| HEADERS / FOOTERS | PARTIAL | Canonical node types include header/footer. | Add repeated-header/footer detection and fixture coverage. |
| FOOTNOTES / NOTES | PARTIAL | Canonical node types include note/footnote; graphical scope includes note checks. | Add extraction/reconciliation rules and fixtures for linkage/placement. |
| NUMBERING | WEAK / PARTIAL | `order` and structural nodes exist, but dedicated numbering validation is not evident. | Add numbering hierarchy/continuity contract and tests. |
| AMENDMENTS | COMPLETE SEMANTIC CONTRACT | Explicit ADD/REPLACE/DELETE semantics exist and are validated. | Integrate into end-to-end package and UI; add amendment fixtures. |
| EXTERNAL SOURCES | COMPLETE CORE | Discovery, validation, retrieval, integrity, parsing and comparison exist. | Integrate into orchestrated job lifecycle with persistent evidence. |
| RECONCILIATION | COMPLETE CORE / NOT ORCHESTRATED | Parser and external reconciliation/resolution primitives exist. | Build one production orchestration and persistent discrepancy register. |
| DISCREPANCIES | COMPLETE CORE / UI MISSING | Conflicts/missing/unmatched observations are retained. | First-class lifecycle/API/UI for review and resolution. |
| GRAPHICAL VERIFICATION | PARTIAL | Validator exists and is fail-closed, but there is no page/region viewer/evidence workflow. | Implement source-page/region evidence service + UI + fixture corpus. |
| PROVENANCE | COMPLETE CORE | Canonical/source anchors, semantic provenance and evidence hashes exist. | Verify provenance is emitted consistently in package export. |
| REVISION LOCK | COMPLETE CORE | Immutable revision ID, source hash, parser versions and evidence hashes. | Integrate into complete package lifecycle. |
| VERIFICATION | COMPLETE CORE / OPERATIONAL OPEN | AI verification records + final acceptance validator exist. | Implement review workflow and persisted verification archive. |
| REGRESSION | PARTIAL | Broad unit tests exist, including graphical and semantic tests; no generic end-to-end fixture corpus/workflow. | Build controlled generic fixtures and E2E regression suite. |
| DIGITAL_ACCEPTED | COMPLETE CORE / PRODUCT OPEN | Final gate blocks missing evidence and requires AI verification. | Make acceptance an emergent lifecycle state only after full orchestrated evidence chain. |
| REPRODUCIBILITY | COMPLETE PACKAGE CORE / PRODUCT INTEGRATION OPEN | Package creation persists source/job/manifest, verifies artifact hashes and replays using package-local paths after original locations are removed. | Integrate package creation/replay into the production lifecycle. |
| HANDOFF | MISSING AS FIRST-CLASS WORKFLOW | Protocol requires explicit handoff, implementation status marks it partial. | Add handoff artifact/schema/API/UI and pending state. |
| UI | OPEN / MISSING | No frontend framework or web application found. | Build web UI around the generic engine. |
| API/BACKEND | OPEN / MISSING | No FastAPI/Flask/other application backend found; only CLI entry point. | Add service/API layer for jobs, artifacts, discrepancies, verification and export. |

## Important findings

### 1. The current CLI is not the Digital Copy product

`ndi-ingest` currently performs direct PDF extraction with MarkItDown and prints the source SHA-256 and parser version. It does not create a Digital Copy job, run the full parser set, persist a complete evidence package, expose discrepancies, run graphical verification, manage verification records, or produce a final acceptance package.

### 2. The persistence/replay boundary is now closed at generic package level

A Digital Copy package now has a deterministic manifest, immutable package-local source copy, job JSON and artifact hashes. Replay verifies these bindings and returns package-local source/artifact paths, so the package can be moved or replayed after the original source/artifact locations are removed.

This closes the previously identified package/replay gap, but it does not populate the package with the full pipeline's artifacts automatically.

### 3. The core contracts are present but disconnected

`ingestion.py`, `verification.py`, `graphical_verification.py`, `revision_lock.py`, external-source modules and semantic modules establish substantial building blocks. The principal engineering gap is now the unified orchestration layer that composes them deterministically and persists all intermediate/final artifacts.

### 4. Canonical structure has some implicit fields but lacks dedicated generic contracts for known failure classes

Headers/footers, notes/footnotes and node ordering exist at model level, but reading order and numbering are not yet explicit production verification contracts. These should be hardened before real-document corpus work.

### 5. Graphical verification is currently validation logic, not an evidence-producing product workflow

The validator requires source hash, checked pages, critical categories, verifier/timestamp and no unresolved discrepancies. What is missing is the actual page/region evidence capture and user interaction needed to produce those records reliably.

### 6. UI and API are a P0 product gap

No frontend or application server was found in the repository. This is consistent with the roadmap's Phase 9 `OPEN` status.

### 7. Generic regression is not yet end-to-end

The repository has many focused unit tests, including adapter, ingestion, reconciliation, graphical verification, external-source and semantic tests. A controlled end-to-end fixture corpus that drives a complete PDF → Digital Copy lifecycle is still missing.

## Immediate implementation priority

1. **Current:** create the production orchestration service for one Digital Copy job lifecycle.
2. Integrate intake → identity → hash → parser observations → reconciliation → external check → canonicalization → semantic artifacts → graphical verification evidence → revision lock → independent verification → regression → final acceptance.
3. Persist a complete package after each material stage and retain extraction/discrepancy/verification evidence.
4. Add explicit reading-order and numbering validation contracts.
5. Expose the workflow through an application API.
6. Build the UI against that API.
7. Build generic end-to-end fixtures and make CI exercise the complete workflow.

## Constraints respected

- No real normative document was executed as the development driver.
- Historical DBN benchmark artifacts remain historical evidence only.
- No generic subsystem was declared complete solely because a unit contract exists.
- `DIGITAL_ACCEPTED` remains a final lifecycle state requiring the complete evidence chain.
