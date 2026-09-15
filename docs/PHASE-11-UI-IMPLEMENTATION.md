# Phase 11 — Product UI Implementation

Implementation hardening of the closed Product UI Contract.

## Target

Deliver the Digital Copy Workspace defined by `docs/PRODUCT-UI-CONTRACT.md`.

## Implementation sequence

1. Native PDF rendering with page navigation and zoom.
2. Source-coordinate overlay layer bound to graphical evidence.
3. Bidirectional selection: `PDF ↔ Canonical Node ↔ Digital Copy`.
4. Structure Explorer.
5. Discrepancy and Evidence workspaces.
6. Verification and Acceptance workspaces.
7. Revision History and Export/Handoff views.
8. Accessibility/deployment/persistence hardening.

## Boundary

This phase may improve presentation and navigation but must not change normative semantics, source evidence, acceptance gates, revision identity, or fail-closed behavior.

## Acceptance

Every implemented feature requires tests and the exact resulting `main` commit must have a successful GitHub Actions run before it is treated as complete.
