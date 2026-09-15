# Roadmap — Digital Normative Document / Generic Digital Copy

**Repository:** `bigunandrey/normative-document-intelligence`  
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Roadmap revision:** 2026-09-15

## 1. Strategic target

The immediate target is to finish the complete generic product block that converts an arbitrary normative PDF into a verified, reproducible **Digital Copy** and gives a user a normal, understandable way to operate that process.

Real normative documents remain validation corpus, not the development driver, until the generic product foundation is complete.

Target chain:

```text
USER PDF
  ↓
USER-FACING DIGITAL COPY WORKSPACE
  ↓
DOCUMENT IDENTITY / EDITION / AMENDMENTS
  ↓
PRIMARY-SOURCE INTEGRITY
  ↓
MULTI-PARSER OBSERVATIONS
  ↓
CANONICAL STRUCTURE
  ↓
EXTERNAL AUTHORITATIVE-SOURCE CHECK
  ↓
DISCREPANCY / RECONCILIATION
  ↓
SEMANTIC / TABLE / FORMULA / CHANGE / DEPENDENCY ARTIFACTS
  ↓
GRAPHICAL VERIFICATION
  ↓
REVISION LOCK
  ↓
INDEPENDENT VERIFICATION
  ↓
REGRESSION
  ↓
DIGITAL_ACCEPTED
  ↓
EXPORT / HANDOFF / DOWNSTREAM DOMAIN USE
```

## 2. Phase status

### Phase 0 — CI and baseline recovery — **COMPLETE ✅**

### Phase 1 — Document identity and source registry — **COMPLETE ✅**

Generic source identity, SHA-256 binding, document identity and source-candidate validation are implemented.

### Phase 2 — Parser observation and canonical structural layer — **COMPLETE FOR GENERIC CONTRACT ✅**

Canonical document/node model, stable source anchors, parser observations/provenance, adapter registry/contracts, multi-parser adaptation, matching/reconciliation and fail-closed structural validation are implemented and CI-verified.

### Phase 3 — External source discovery, retrieval and comparison — **COMPLETE FOR GENERIC CONTRACT ✅**

Provider-neutral discovery, source/revision validation, retrieval integrity, independent external parsing, observation aggregation and discrepancy comparison are implemented.

### Phase 4 — Integrated reconciliation — **COMPLETE FOR GENERIC CONTRACT ✅**

Integrated parser/external reconciliation and explicit resolution outcomes are supported by the verification gates.

### Phase 5 — Canonical Digital Copy and persistence — **COMPLETE FOR GENERIC CONTRACT ✅**

Implemented and CI-verified: deterministic job persistence, stage-evidence contract, production orchestration boundary, per-stage evidence history, extraction log, canonical Digital Copy persistence, immutable package-local source copy, manifest/hash binding, self-contained package creation, fail-closed verification, replay/path rebinding and handoff artifact.

Concrete document executors and UI remain outside this phase.

### Phase 6 — Semantic Digital Copy layer — **COMPLETE FOR GENERIC CONTRACT ✅ / PRODUCT INTEGRATION OPEN**

Atomic normative units, exact operators, conditions/exceptions, applicability/type links, table/formula registry primitives, dependency graph/resolution, source-bound evaluation, amendment actions, semantic provenance and fail-closed semantic acceptance are implemented.

### Phase 7 — Graphical verification — **COMPLETE FOR GENERIC EVIDENCE CONTRACT ✅**

The generic graphical-verification evidence layer is now closed.

Implemented and CI-verified:

- explicit page/region model with validated coordinates;
- source-bound graphical evidence items;
- critical-element taxonomy covering tables, formulas, operators, numeric values, units, notes, footnotes, numbering, amendments and deletions;
- source-text vs observed-text evidence;
- per-item match result;
- verifier and timestamp binding;
- bundle-level validation and fail-closed PASS semantics;
- unresolved-discrepancy blocking;
- deterministic JSON evidence artifact and SHA-256;
- persistence helper for `graphical-evidence.json`;
- regression fixtures for valid evidence, mismatch, source-hash mismatch, invalid regions and deterministic persistence.

**Explicit boundary:** this closes the **generic evidence-producing engine contract**, not the human-facing PDF page viewer. Viewer/UI integration belongs to Phase 9. Real-document visual execution remains Phase 11 validation.

### Phase 8 — Revision lock and independent verification — **COMPLETE FOR CORE CONTRACT / OPERATIONAL WORKFLOW OPEN ▶️**

Implemented and CI-verified: immutable revision lock, deterministic revision ID, reproducibility manifest, package replay, independent AI verification records, distinct independence bases and final acceptance validation.

Remaining operational work: `Rev_<NNN>` archive workflow, operational verification archive and user-visible status.

### Phase 9 — Generic Digital Copy User Interface — **CURRENT P0 🔄**

Build the normal user-facing workflow around the generic engine contracts.

Minimum screens/states:

1. Projects / Digital Copies;
2. Create Digital Copy;
3. Source Identity;
4. Extraction;
5. Structure;
6. Discrepancies;
7. Semantics;
8. Graphical Verification — render source PDF page/region next to the digital element and record the Phase 7 evidence;
9. Verification;
10. Acceptance;
11. Export / Handoff.

The UI must never display unresolved content as accepted normative truth.

### Phase 10 — Generic end-to-end regression suite — **OPEN ⏳**

Create a controlled fixture corpus and exercise the complete generic workflow across text-native/OCR PDFs, complex layouts, tables, formulas, notes, numbering, amendments, disagreements, graphical evidence, revision tampering and final acceptance.

### Phase 11 — Real normative corpus validation — **NOT STARTED BY DESIGN ⏸️**

Only after the generic product foundation is complete should the system be exercised against DBN, DSTU/DSTU EN, ISO/IEC, NFPA and other normative systems.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after generic Digital Copy is stable should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Generic Digital Copy UI **← CURRENT STEP**

Expose the complete lifecycle and the Phase 7 page/region evidence workflow to users.

### P0 — Operational verification / revision / handoff

Complete `Rev_NNN` archive lifecycle and operational independent-verification archive.

### P1 — Generic end-to-end regression

Prove the entire workflow on controlled fixtures before using real normative documents as the primary development driver.

### P2 — Real normative corpus

Run DBN plus a diverse set of other normative documents and classify failures by generic subsystem.

## 4. Definition of Done — generic Digital Copy block

The generic block is complete when a user can provide a normative PDF and obtain, through the normal UI:

- immutable source identity and integrity hash;
- multi-parser extraction evidence;
- canonical structural representation;
- retained parser/external discrepancies;
- source-bound semantic/table/formula/change/dependency artifacts;
- graphical verification evidence or an explicit blocked state;
- immutable revision lock;
- independent verification records;
- regression result;
- reproducibility manifest;
- complete export/handoff package;
- final status that is either `DIGITAL_ACCEPTED` or explicitly blocked with machine-readable reasons.

Phase 7 is now a completed generic engine contract, but the overall product Definition of Done still depends on UI, operational verification and generic E2E regression.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
