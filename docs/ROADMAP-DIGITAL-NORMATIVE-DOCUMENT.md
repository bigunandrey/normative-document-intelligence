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
### Phase 8 — Revision lock and independent verification — **PARTIAL: CORE + OPERATIONAL ARCHIVE CONTRACT IMPLEMENTED / PRODUCT INTEGRATION OPEN 🔄**

Implemented and CI-verified:

- immutable revision lock and deterministic revision ID;
- reproducibility manifest and package replay;
- independent AI verification records with distinct independence bases;
- fail-closed final acceptance contract;
- immutable `Rev_NNN` operational archive;
- archive source/revision/document binding;
- archived verification evidence and hash validation;
- duplicate archival of the same revision is rejected;
- tamper detection for archive manifest and verification evidence;
- fail-closed archive creation when the locked revision is missing/invalid.

Remaining for full operational closure: orchestration/UI integration of archive creation and archive/status controls, plus production access-control concerns.

### Phase 9 — Generic Digital Copy User Interface — **PARTIAL: GENERIC UI SHELL COMPLETE / OPERATIONAL PRODUCT INTEGRATION OPEN 🔄**

Implemented and CI-covered:

1. Projects / Digital Copies dashboard;
2. Create Digital Copy via PDF upload;
3. Source identity and SHA-256 presentation;
4. persisted lifecycle/status display;
5. machine-readable job API;
6. package-local PDF source viewer;
7. Graphical Verification evidence display consuming Phase 7 page/region records;
8. blocker and acceptance-state presentation;
9. injected workflow-runner boundary;
10. `ndi-ui` launch command.

Remaining: production executors, archive controls, production auth/access control, rich PDF region overlays and complete E2E execution.

### Phase 10 — Generic end-to-end regression suite — **NEXT P1 ⏳**

Create a controlled fixture corpus and exercise the complete generic workflow across text-native/OCR PDFs, complex layouts, tables, formulas, notes, numbering, amendments, disagreements, graphical evidence, revision tampering and final acceptance.

### Phase 11 — Real normative corpus validation — **NOT STARTED BY DESIGN ⏸️**

Only after the generic product foundation is complete should the system be exercised against DBN, DSTU/DSTU EN, ISO/IEC, NFPA and other normative systems.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after generic Digital Copy is stable should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Complete Phase 8 operational integration **← CURRENT STEP**

Connect `Rev_NNN` archive creation and verification to the Digital Copy orchestration/UI lifecycle. Expose archive identity, verification result and tamper/blocker state to the user. Preserve fail-closed behavior and immutable revision semantics.

### P1 — Generic end-to-end regression

Prove the entire workflow on controlled fixtures before using real normative documents as the primary development driver.

### P2 — Real normative corpus

Run DBN plus a diverse set of other normative documents and classify failures by generic subsystem.

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

Phase 8 has an operational archive contract, but the overall product Definition of Done still depends on its UI/orchestration integration and generic E2E regression.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
