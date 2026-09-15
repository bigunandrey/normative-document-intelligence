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

Implemented:

- immutable revision lock and deterministic revision ID;
- reproducibility manifest and package replay;
- independent AI verification records with distinct independence bases;
- fail-closed final acceptance contract;
- immutable `Rev_NNN` operational archive;
- archive source/document/revision binding;
- archived verification evidence and hash validation;
- duplicate archival of the same revision is rejected;
- manifest and verification-evidence tamper detection;
- fail-closed archive creation when the locked revision is missing/invalid;
- orchestration integration for archive creation;
- UI archive/status integration;
- archive identity, result and verification state persisted into the Digital Copy job/handoff.

Production authentication/authorization remains a deployment-layer concern and is not required for generic engine closure.

### Phase 9 — Generic Digital Copy User Interface — **COMPLETE FOR GENERIC UI CONTRACT ✅**

Implemented:

1. Projects / Digital Copies dashboard;
2. PDF upload intake;
3. package-local immutable source copy;
4. source SHA-256 presentation;
5. persisted lifecycle/status display;
6. machine-readable job API;
7. package-local PDF source viewer;
8. Graphical Verification evidence display;
9. blocker and acceptance-state presentation;
10. workflow-runner boundary;
11. operational archive controls;
12. archive identity/result/verification display;
13. `ndi-ui` launch command;
14. regression coverage for the UI lifecycle.

Remaining UI enhancements such as rich PDF region overlays are not blockers for the generic contract; they belong to later product hardening/document-specific UX work.

### Phase 10 — Generic end-to-end regression suite — **IN PROGRESS 🔄 / CURRENT P0**

Prove the complete generic lifecycle using a controlled fixture matrix. The matrix must cover:

- successful end-to-end acceptance;
- missing-stage and failed-stage fail-closed behavior;
- parser disagreement and missing observation states;
- text-native and OCR-like extraction conditions;
- tables, formulas, notes, footnotes and numbering;
- amendments and deletions;
- external-source discrepancy/reconciliation;
- graphical verification mismatch and success;
- revision-lock binding and tamper detection;
- insufficient independent verification;
- operational archive creation and verification;
- package replay/reproducibility;
- UI persistence of final accepted and blocked states.

Phase 10 closes only when the matrix is green on the current `main` head and the resulting evidence is documented.

### Phase 11 — Real normative corpus validation — **BLOCKED BY DESIGN UNTIL PHASE 10 CLOSES ⏸️**

After Phase 10 closure, exercise the generic engine against DBN, DSTU/DSTU EN, ISO/IEC, NFPA and other normative systems. Failures must be classified by generic subsystem and converted into regression fixtures where appropriate.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after generic Digital Copy is stable should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Phase 10 generic E2E regression **← CURRENT STEP**

Expand the controlled fixture matrix until the complete generic acceptance path and representative fail-closed paths are proven end-to-end. Every implementation change must be verified by the exact current-head GitHub Actions run.

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

Phase 8 and Phase 9 are now closed at the generic contract level. Phase 10 is the remaining gate before real normative-corpus validation.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
