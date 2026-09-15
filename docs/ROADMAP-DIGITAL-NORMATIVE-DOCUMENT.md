# Roadmap — Digital Normative Document / Generic Digital Copy

**Repository:** `bigunandrey/normative-document-intelligence`  
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

Phase 10 has now passed two consecutive current-head CI milestones covering the core acceptance path and expanded fail-closed/tamper behavior. The latest green commit is `ed758a9e8a6a17640b9b0401f10cda5a7e0130fe` (GitHub Actions run `34982088833`).

Implemented and CI-verified in the current matrix:

- complete generic acceptance path;
- missing-stage and every-stage failure fail-closed behavior;
- failed evidence without blockers rejected;
- unsupported stage bindings rejected;
- archive revision-binding tamper detection;
- packaged artifact tamper detection;
- packaged source tamper detection;
- insufficient independent-verifier archive rejection;
- operational archive verification;
- package replay after successful acceptance/archive.

Still required before Phase 10 closure:

- parser disagreement / missing-observation fixtures wired through the real reconciliation boundary;
- text-native and OCR-like extraction fixtures;
- tables, formulas, notes, footnotes and numbering fixtures wired end-to-end;
- amendment/deletion fixtures;
- external-source discrepancy/reconciliation fixture;
- graphical verification success/mismatch integrated into orchestration;
- semantic unresolved/ambiguous fixture;
- UI accepted/blocked persistence end-to-end;
- final complete-matrix evidence document.

### Phase 11 — Real normative corpus validation — **BLOCKED BY DESIGN UNTIL PHASE 10 CLOSES ⏸️**

After Phase 10 closure, exercise the generic engine against DBN, DSTU/DSTU EN, ISO/IEC, NFPA and other normative systems. Failures must be classified by generic subsystem and converted into regression fixtures where appropriate.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after generic Digital Copy is stable should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Phase 10 generic E2E regression **← CURRENT STEP**

Expand the controlled fixture matrix until the complete generic acceptance path and representative fail-closed paths are proven end-to-end. Every implementation change must be verified by the exact current-head GitHub Actions run.

**Next P0 block:** wire graphical verification evidence and reconciliation disagreement/missing-observation states into the actual orchestration E2E boundary, rather than testing them only as isolated contracts.

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
