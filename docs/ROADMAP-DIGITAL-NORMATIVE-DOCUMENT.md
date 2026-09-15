# Roadmap — Digital Normative Document / Generic Digital Copy

**Repository:** `normative-document-intelligence`  
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Product UI Contract:** `docs/PRODUCT-UI-CONTRACT.md`  
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
### Phase 9 — Generic Digital Copy User Interface — **CONTRACT CLOSED ✅ / IMPLEMENTATION HARDENING PARTIAL ⚠️**
### Phase 10 — Generic end-to-end regression suite — **COMPLETE FOR GENERIC DIGITAL COPY CONTRACT ✅**

Phase 10 is closed by the E2E regression matrix documented in `docs/PHASE-10-CLOSURE-2026-09-15.md`. The final regression implementation head was `98dfd927352a7e10d4c03e37af9cd432884b73f7`, with GitHub Actions run `34984635942` / test job `104433472094` completing successfully. The closure matrix includes lifecycle fail-closed behavior, reconciliation disagreement/missing observation, external-source discrepancy, graphical verification, critical visual elements, semantic unresolved state, amendments/deletions, text-native and OCR-like extraction, revision/package/source tamper, independent verification, archive/replay and UI restart persistence.

### Phase 11 — Real normative corpus validation — **CURRENT P0 ▶️**

Process a diverse real normative corpus through the now-closed generic Digital Copy workflow. Use DBN, DSTU/DSTU EN, ISO/IEC, NFPA and legal/regulatory documents where authoritative copies are available. Include text-native and scanned PDFs, tables, formulas, notes/footnotes, amendments/deletions and complex layouts.

Failures are classified by generic subsystem. Generic capability gaps are fixed in the engine and converted into regression fixtures; document-specific exceptions are not used as a substitute for generic fixes.

### Phase 12 — Downstream domain integration — **AFTER PHASE 11**

Only after real-corpus validation should accepted representations be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Phase 11 real normative corpus validation **← CURRENT STEP**

1. select a deliberately diverse authoritative corpus;
2. run each document through the generic Digital Copy workflow;
3. classify failures by subsystem and severity;
4. convert generic capability gaps into regression fixtures;
5. repeat until the corpus demonstrates that the generic contract generalizes beyond controlled fixtures.

### P1 — Product UI implementation hardening

The Product UI Contract is closed in `docs/PRODUCT-UI-CONTRACT.md`. Remaining implementation work is measured against that contract and includes:

1. interactive native PDF page rendering;
2. source-region overlays tied to `page + bbox` evidence;
3. bidirectional `PDF ↔ Canonical Node ↔ Digital Copy` selection;
4. Structure Explorer;
5. Discrepancy and Evidence workspaces;
6. Verification and Acceptance workspaces;
7. Revision History and Export/Handoff views;
8. production deployment and accessibility hardening;
9. stronger atomic persistence where justified.

UI hardening must not change the source protocol or weaken fail-closed behavior.

### P2 — Downstream domain integration

Connect accepted Digital Copies to normative registers, SPZ semantics and engineering calculation/execution layers after real-corpus validation establishes generic robustness.

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

The Product UI Contract is closed as a specification; UI implementation hardening and Phase 11 real-document validation remain separate execution tracks.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
