# Generic PDF → Digital Copy Audit

**Date:** 2026-09-15  
**Repository:** `bigunandrey/normative-document-intelligence`  
**Branch:** `main`  
**Purpose:** Production-readiness audit of the generic NDI Digital Copy subsystem before real normative-corpus validation.

## Executive result

The generic NDI engine contains CI-verified contracts for identity, source binding, canonical structure, parser adapters, reconciliation, external-source comparison, canonical persistence/replay, typed orchestration, semantic representation and graphical verification evidence.

**Phase 7 — Graphical Verification is now complete at the generic evidence-contract level.** The new evidence layer records a source-bound page/region, critical element kind, source/observed text, match result, verifier and timestamp; validates coordinates and source hash; blocks mismatches/unresolved discrepancies; and persists deterministic JSON evidence with SHA-256.

The remaining critical product gap is still integration: no user-facing web UI/PDF viewer, no operational `Rev_NNN` verification archive, and no complete generic E2E fixture workflow.

## Pipeline audit

| Block | Status | Evidence / finding | Required action |
|---|---|---|---|
| PDF INPUT | PARTIAL | CLI/core intake exists; user-facing job lifecycle remains open. | UI/API intake. |
| IDENTITY | COMPLETE CORE / ORCHESTRATED | Identity and source binding are available to orchestration. | Concrete executor/API integration. |
| SOURCE INTEGRITY | COMPLETE CORE / ORCHESTRATED | SHA-256 and package-local source persistence. | Expose through product UI. |
| EXTRACTION | COMPLETE GENERIC WORKFLOW CONTRACT | Typed stage evidence and persistent extraction log. | Concrete parser execution/E2E fixtures. |
| PARSER REGISTRY | COMPLETE | Registry/contracts/default adapters. | Runtime degraded-state fixtures. |
| ADAPTERS | COMPLETE CORE | MarkItDown, pypdf, Docling, OpenDataLoader. | E2E degraded-case coverage. |
| OBSERVATIONS | COMPLETE CORE | Canonical observations/provenance. | Full workflow fixture coverage. |
| CANONICAL MODEL | COMPLETE CORE | Structural nodes, anchors, provenance and parser metadata. | Full workflow validation. |
| STRUCTURE | PARTIAL | Structural gates/reconciliation exist. | Explicit reading-order/numbering contracts. |
| TABLES | PARTIAL | Table/cell and registry primitives. | Robust reconstruction + real-document validation. |
| FORMULAS | PARTIAL | Formula node/registry primitives. | Concrete extraction/reconstruction validation. |
| READING ORDER | WEAK / PARTIAL | Canonical ordering exists, but dedicated validation is not closed. | Harden generic contract before real corpus. |
| HEADERS / FOOTERS | PARTIAL | Node types exist. | Detection/reconciliation fixtures. |
| FOOTNOTES / NOTES | PARTIAL | Node types and graphical taxonomy exist. | Linkage/placement fixtures. |
| NUMBERING | WEAK / PARTIAL | Structural order exists; dedicated continuity validation remains open. | Harden generic contract. |
| AMENDMENTS | COMPLETE SEMANTIC CONTRACT | ADD/REPLACE/DELETE semantics validated. | E2E/UI integration. |
| EXTERNAL SOURCES | COMPLETE CORE | Discovery, retrieval, integrity, parsing and comparison. | E2E lifecycle integration. |
| RECONCILIATION | COMPLETE CORE / ORCHESTRATED | Typed stage boundary now exists. | Concrete executor integration. |
| DISCREPANCIES | COMPLETE CORE / UI MISSING | Conflicts/missing/unmatched observations retained. | UI/API review workflow. |
| GRAPHICAL VERIFICATION | **COMPLETE GENERIC EVIDENCE CONTRACT** | Page/region model, critical taxonomy, source binding, text comparison, match result, verifier/time, deterministic persistence and fail-closed validation. | Phase 9 viewer/UI integration. |
| PROVENANCE | COMPLETE CORE | Source anchors and evidence hashes exist. | Verify complete export consistency. |
| REVISION LOCK | COMPLETE CORE | Immutable revision ID/source/parser/evidence bindings. | Operational archive workflow. |
| VERIFICATION | COMPLETE CORE / OPERATIONAL OPEN | AI verification records + acceptance validator. | Operational archive/review UI. |
| REGRESSION | PARTIAL | Strong unit coverage; generic full-pipeline E2E corpus absent. | Phase 10 E2E corpus. |
| DIGITAL_ACCEPTED | COMPLETE CORE / PRODUCT OPEN | Final gate exists. | Full production evidence chain. |
| REPRODUCIBILITY | COMPLETE PACKAGE CORE | Self-contained package, hashes and replay. | Full pipeline artifact population. |
| HANDOFF | COMPLETE GENERIC ARTIFACT CONTRACT | Handoff artifact persists package state. | Downstream workflow integration. |
| UI | OPEN / MISSING | No frontend/PDF viewer. | Phase 9. |
| API/BACKEND | OPEN / MISSING | No application API layer. | Phase 9. |

## Phase 7 evidence contract

The generic graphical evidence chain is:

```text
Source SHA-256
  → Page / Region
  → Critical Element
  → Source Text ↔ Observed Text
  → Match
  → Verifier + Timestamp
  → Bundle Validation
  → graphical-evidence.json + SHA-256
```

Supported critical categories:

- table;
- formula;
- normative operator;
- numeric value;
- unit;
- note;
- footnote;
- numbering;
- amendment;
- deletion.

A PASS bundle is rejected if any item is unmatched, source hashes differ, a region is invalid, or unresolved discrepancies remain.

## Phase 7 boundary

The following are intentionally **not** claimed as Phase 7 completion:

- PDF rendering/viewer;
- automatic screenshot acquisition;
- human click-through workflow;
- document-specific visual correctness;
- real normative-corpus execution.

These are Phase 9/UI and Phase 11 validation concerns.

## Immediate implementation priority

1. **Current:** Phase 9 — user-facing Digital Copy UI and source-page viewer.
2. Operational verification/revision archive.
3. Generic E2E fixture corpus.
4. Real normative corpus validation.
5. Downstream domain integration.

## Constraints respected

- No real normative document was used as the development driver.
- Historical DBN benchmark evidence remains historical.
- Phase 7 was closed only at the generic evidence-contract level; UI and real-document claims were not hidden behind it.
- `DIGITAL_ACCEPTED` remains a final lifecycle result requiring the complete evidence chain.
