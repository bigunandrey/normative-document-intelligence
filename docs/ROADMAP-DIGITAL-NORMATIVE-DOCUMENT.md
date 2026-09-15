# Roadmap — Digital Normative Document / Generic Digital Copy

**Repository:** `normative-document-intelligence`  
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Roadmap revision:** 2026-09-15

## 1. Strategic target

Finish the complete generic product block that converts an arbitrary normative PDF into a verified, reproducible **Digital Copy** and gives a user a normal, understandable way to operate that process.

Real normative documents remain validation corpus, not the development driver, until the generic product foundation is complete.

## 2. Phase status

### Phase 0 — CI and baseline recovery — **COMPLETE ✅**
### Phase 1 — Document identity and source registry — **COMPLETE ✅**
### Phase 2 — Parser observation and canonical structural layer — **COMPLETE FOR GENERIC CONTRACT ✅**
### Phase 3 — External source discovery, retrieval and comparison — **COMPLETE FOR GENERIC CONTRACT ✅**
### Phase 4 — Integrated reconciliation — **COMPLETE FOR GENERIC CONTRACT ✅**
### Phase 5 — Canonical Digital Copy and persistence — **COMPLETE FOR GENERIC CONTRACT ✅**
### Phase 6 — Semantic Digital Copy layer — **COMPLETE FOR GENERIC CONTRACT ✅ / PRODUCT INTEGRATION OPEN**
### Phase 7 — Graphical verification — **COMPLETE FOR GENERIC EVIDENCE CONTRACT ✅**
### Phase 8 — Revision lock, independent verification and operational archive — **COMPLETE FOR GENERIC OPERATIONAL CONTRACT ✅**
### Phase 9 — Generic Digital Copy User Interface — **COMPLETE FOR GENERIC UI CONTRACT ✅**
### Phase 10 — Generic end-to-end regression suite — **IN PROGRESS 🔄 / CURRENT P0**

The current `main` head is CI-green through commit `58654902e82596e66a0e81d1e950c1f04bac5547` (GitHub Actions run `34984364656`). The latest regression additions cover graphical verification, reconciliation conflict/missing observation, external-source discrepancy, semantic unresolved state, critical visual elements, amendment handling, package/source tamper, insufficient verification, and UI restart persistence.

Implemented and CI-verified in the current matrix:

- complete generic acceptance path;
- missing-stage and every-stage failure fail-closed behavior;
- failed evidence without blockers rejected;
- unsupported stage bindings rejected;
- parser disagreement and missing-observation states through reconciliation;
- external-source discrepancy blocking and same-revision agreement;
- graphical verification success/mismatch through orchestration;
- table/formula/note/footnote/numbering representative visual evidence;
- semantic unresolved-state blocking;
- amendment replacement resolution and unresolved deletion target blocking;
- archive revision-binding tamper detection;
- packaged artifact/source tamper detection;
- insufficient independent-verifier archive rejection;
- operational archive verification;
- package replay after successful acceptance/archive;
- accepted/archive state persistence across UI restart.

Still required before Phase 10 closure:

- text-native extraction fixture through the configured parser boundary;
- OCR-like/scanned extraction fixture and corresponding fail-closed evidence behavior;
- final complete-matrix evidence document and closure review.

### Phase 11 — Real normative corpus validation — **BLOCKED BY DESIGN UNTIL PHASE 10 CLOSES ⏸️**

After Phase 10 closure, exercise the generic engine against DBN, DSTU/DSTU EN, ISO/IEC, NFPA and other normative systems. Failures must be classified by generic subsystem and converted into regression fixtures where appropriate.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after generic Digital Copy is stable should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Phase 10 generic E2E regression **← CURRENT STEP**

Expand the controlled fixture matrix until the complete generic acceptance path and representative fail-closed paths are proven end-to-end. Every implementation change must be verified by the exact current-head GitHub Actions run.

**Next P0 block:** add text-native and OCR-like extraction fixtures through the parser/extraction boundary, then produce the final Phase 10 matrix evidence and closure record.

### P1 — Generic product hardening

Address non-blocking hardening discovered during Phase 10: richer graphical overlays, production deployment concerns, stronger atomic persistence where justified, and other robustness gaps that do not alter the generic evidence model.

### P2 — Real normative corpus

Validate against a diverse real corpus only after Phase 10 closes.

### P3 — Downstream domain integration

Connect accepted Digital Copies to normative registers, SPZ semantics and engineering calculation/execution layers.

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
- operational `Rev_NNN` archive;
- regression result;
- reproducibility manifest;
- complete export/handoff package;
- final status that is either `DIGITAL_ACCEPTED` or explicitly blocked with machine-readable reasons.

Phase 8 and Phase 9 are closed at the generic contract level. Phase 10 remains the final generic completion gate before real normative-corpus validation.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
