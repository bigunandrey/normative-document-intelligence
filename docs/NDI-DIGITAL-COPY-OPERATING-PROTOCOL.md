# NDI Digital Copy Operating Protocol

**Applies to:** `bigunandrey/normative-document-intelligence`  
**Protocol basis:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Product UI Contract:** `docs/PRODUCT-UI-CONTRACT.md`  
**Operational revision:** 2026-09-15

> This document is the NDI implementation/operating supplement to the source protocol. It does not replace or alter the source-derived normative requirements in `docs/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md`.

## 1. Purpose

NDI provides a generic workflow for converting an arbitrary normative PDF into a verified **Digital Copy**.

The generic product foundation is now closed through Phase 10. Real normative documents are the validation corpus for Phase 11 and onward.

## 2. Product boundary

NDI is responsible for the generic evidence and Digital Copy lifecycle:

```text
PDF
→ identity / integrity
→ multi-parser observations
→ canonical structure
→ external-source evidence
→ discrepancy / reconciliation
→ semantic/table/formula/change/dependency artifacts
→ graphical verification
→ revision lock
→ independent verification
→ regression
→ DIGITAL_ACCEPTED
→ export / handoff
```

Domain-specific engineering interpretation and execution consume the accepted Digital Copy downstream.

## 3. User workflow

### 3.1 Create

User selects or uploads a normative PDF and starts **Create Digital Copy**.

The system immediately creates a document workspace and records the source hash. The original source is never silently replaced.

### 3.2 Identify

The user reviews or confirms:

- designation;
- title;
- issuing organization;
- edition/year;
- amendments;
- publication/effective status;
- source URL/source provenance;
- source SHA-256.

Unverified identity fields remain explicitly unverified.

### 3.3 Extract

The system runs the configured parser set and records each parser/version as an observation source.

Extraction output is displayed as **evidence**, never as accepted normative truth.

### 3.4 Reconcile

The system compares independent observations and exposes:

- agreed elements;
- missing observations;
- text mismatches;
- structural mismatches;
- value mismatches;
- revision mismatches;
- unresolved discrepancies.

No discrepancy may disappear through an implicit correction.

### 3.5 Build Digital Copy

The accepted canonical representation links each digital element to source evidence and, where applicable, creates:

- normative units;
- operators/modality;
- conditions/exceptions;
- applicability/type links;
- table/cell records;
- formula records;
- dependencies/cross-references;
- amendment/change actions.

All artifacts remain bound to the document source and digital revision.

### 3.6 Verify graphically

For visually critical elements, the user/AI must be able to inspect the corresponding source page/region and record evidence.

At minimum this covers:

- tables and merged/complex cells;
- formulas and special symbols;
- numbers and units;
- normative comparison operators;
- footnotes/notes;
- numbering;
- amendments and deletions.

If graphical verification is unavailable, the element cannot be silently promoted to verified status.

### 3.7 Verify independently

The acceptance workflow records the required independent verification records, their scope, result and independence basis.

The UI must show the difference between:

- verification not run;
- verification passed;
- verification failed;
- verification blocked.

### 3.8 Accept

The acceptance screen shows the complete evidence chain and all blockers.

`DIGITAL_ACCEPTED` is available only when all required generic acceptance conditions are satisfied.

Otherwise the document remains explicitly blocked/pending with machine-readable reasons.

### 3.9 Export / handoff

The user can export a reproducible Digital Copy package containing the canonical representation, evidence/provenance, revision lock, verification records and manifest.

A handoff is an explicit artifact, not an informal message.

## 4. UI information architecture

The binding product definition is `docs/PRODUCT-UI-CONTRACT.md`.

The production UI contains these views:

1. **Digital Copies** — document list, status, revision, last activity and blockers.
2. **Create Digital Copy** — source selection/upload and intake.
3. **Overview** — identity, source integrity, current revision and lifecycle state.
4. **Extraction** — parser observations and extraction evidence.
5. **Structure** — page tree, sections, paragraphs, lists, tables, cells, formulas and anchors.
6. **Discrepancies** — all unresolved and resolved differences with evidence.
7. **Digital Copy** — normalized source-bound artifacts.
8. **Graphical Verification** — source-page viewer and selected digital element side-by-side.
9. **Verification** — AI/human verification records and independence.
10. **Acceptance** — gate-by-gate result and blockers.
11. **Revision History** — immutable revisions and evidence hashes.
12. **Export / Handoff** — reproducible package and downstream handoff.

## 5. Lifecycle statuses

The product must distinguish processing state from acceptance state. At minimum:

```text
NEW
IDENTIFYING
EXTRACTING
RECONCILING
DIGITALIZING
REVIEW_REQUIRED
GRAPHICAL_VERIFICATION
VERIFICATION_REQUIRED
REGRESSION_REQUIRED
BLOCKED
DIGITAL_ACCEPTED
```

A gate result such as `PASS` is not itself a lifecycle status of `DIGITAL_ACCEPTED`.

## 6. Fail-closed UI rules

The UI must enforce the same rules as the engine:

- unresolved discrepancies are visible and actionable;
- unresolved semantic interpretation is not shown as accepted;
- missing provenance is a blocker;
- missing source evidence is a blocker;
- ambiguous dependency/amendment targets are blockers;
- failed verification is not converted to passed by editing the display;
- a stale revision cannot be presented as the current accepted revision;
- `DIGITAL_ACCEPTED` cannot be manually selected by the user;
- exports must carry the exact accepted revision and evidence manifest.

## 7. Product UI implementation state

The Product UI Contract is closed at the specification level in `docs/PRODUCT-UI-CONTRACT.md`.

The current generic UI implementation is intentionally recorded separately from contract closure. It currently provides the shell, intake, persisted jobs, lifecycle/blocker display, immutable PDF source access, graphical-evidence listing, workflow/archive API boundaries and restart persistence.

The remaining implementation hardening is governed by the closed Product UI Contract: interactive page rendering and source-region overlays, structure explorer, bidirectional spatial selection, discrepancy/evidence workspaces, and rich verification/acceptance/revision/export views.

These are implementation tasks; the product contract and source protocol are not to be weakened to match the shell.

## 8. Generic development policy

Phase 10 has closed the generic Digital Copy regression gate. The closure evidence is `docs/PHASE-10-CLOSURE-2026-09-15.md`.

The final Phase 10 regression implementation head was `98dfd927352a7e10d4c03e37af9cd432884b73f7`, with GitHub Actions run `34984635942` / test job `104433472094` completing successfully. The matrix covers lifecycle failures, reconciliation disagreement/missing observation, external-source discrepancy, graphical verification, critical visual elements, semantic unresolved state, amendment/deletion handling, text-native and OCR-like extraction, tamper detection, independent verification, archive/replay and UI restart persistence.

### Phase 11 — real-document validation

The next step is deliberate corpus validation. A diverse real-document corpus is processed through the generic Digital Copy workflow. Failures are classified by generic subsystem and used to harden the weakest subsystem rather than creating document-specific exceptions.

## 9. Real-document validation corpus

The first corpus should intentionally vary failure modes and formats, including DBN, DSTU/DSTU EN, ISO/IEC, NFPA and legal/regulatory documents, with both text-native and scanned PDFs and documents containing tables, formulas, amendments and complex layouts.

For every corpus item, preserve source identity and SHA-256, edition/amendment status, extraction observations, discrepancies, verification evidence, revision lock, regression result and final accepted/blocked state.

A real-document failure that exposes a generic capability gap must result in a generic engine change plus a regression fixture. A document-specific workaround is not an acceptable substitute.
