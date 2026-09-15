# UI Implementation Result — 2026-09-15

## Result

The Product UI Contract has moved from specification-only to an implemented generic workspace.

Implemented in `src/ndi/digital_copy_ui_v2.py`, exposed through `src/ndi/digital_copy_ui.py`.

## Implemented contract areas

- Digital Copies dashboard and PDF intake.
- Overview, Extraction, Structure, Discrepancies, Digital Copy, Graphical Verification, Verification, Acceptance, Revision History, Export / Handoff views.
- Immutable package-local source PDF remains the source of truth.
- Server-side rendering of the exact source PDF page using PyMuPDF.
- Page navigation and zoom controls.
- Graphical evidence overlays driven by persisted `page + bbox` evidence.
- Evidence selection navigates to its source page.
- Canonical-node/source-anchor display in Structure.
- Machine-derived acceptance display; no manual `DIGITAL_ACCEPTED` control.
- Operational archive state remains read-only UI data.
- Path confinement for source and artifact reads.

## Dependency

`PyMuPDF>=1.24` was added to the runtime dependencies for exact source-page rendering.

## Verification

The implementation is validated through the repository GitHub Actions regression workflow. Any failing run is treated as non-closure and must be corrected before claiming the implementation complete.

## Remaining P1 hardening

The generic contract implementation does not by itself close production deployment hardening, accessibility audit, browser compatibility testing, or real normative-corpus validation. Those remain separate Phase 11 validation/hardening work.
