# Roadmap — Digital Normative Document / Generic Digital Copy

**Repository:** `bigunandrey/normative-document-intelligence`  
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Roadmap revision:** 2026-09-15

## 1. Strategic target

The immediate target is **not** to process DBN or any other real normative corpus prematurely.

The immediate target is to finish the complete generic product block that converts an arbitrary normative PDF into a verified, reproducible **Digital Copy** and gives a user a normal, understandable way to operate that process.

Only after this block is complete will real documents be used as a broad validation corpus. The corpus must include DBN and other normative systems so that document-specific failures reveal which generic sub-blocks still need hardening.

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

Implemented and CI-verified:

- canonical document/node model;
- stable IDs and source anchors;
- parser observations and provenance;
- parser adapter registry;
- adapter output contract validation;
- multi-parser adaptation;
- cross-parser matching/reconciliation;
- retained discrepancies;
- fail-closed structural validation.

Real-document execution is deliberately deferred to the validation phase.

### Phase 3 — External source discovery, retrieval and comparison — **COMPLETE FOR GENERIC CONTRACT ✅**

Implemented:

- provider-neutral discovery;
- source identity/revision validation;
- retrieved-content integrity verification;
- independent external parsing;
- external observation aggregation;
- source-bound comparison and discrepancy evidence.

Real authoritative-source evidence remains document-specific validation work.

### Phase 4 — Integrated reconciliation — **COMPLETE FOR GENERIC CONTRACT ✅**

Integrated parser/reconciliation results and explicit resolution outcomes are supported by the verification gates.

### Phase 5 — Canonical Digital Copy and persistence — **COMPLETE FOR GENERIC CONTRACT ✅**

Phase 5 is closed at the generic engine/workflow-contract level.

Implemented and CI-verified:

- deterministic Digital Copy job persistence;
- explicit stage-evidence contract and fail-closed stage boundary;
- production orchestration boundary covering identity → extraction → reconciliation → digitalization → graphical verification → verification → regression → acceptance;
- accepted-stage evidence with controlled job bindings (`document_id`, `revision_id`);
- per-stage evidence history persisted in the job/package;
- persistent extraction-log artifact;
- canonical Digital Copy artifact carried through the digitalization stage contract;
- immutable package-local source copy with SHA-256 verification;
- package manifest with source/artifact SHA-256 bindings;
- self-contained `persist_package()` creation;
- fail-closed package verification;
- package-local path rebinding on replay;
- replay independent of original source/artifact locations;
- first-class handoff artifact containing document/revision/package state and downstream handoff target.

Phase 5 does **not** claim that the concrete document-specific executors, graphical evidence service, UI, independent verification workflow or generic E2E fixture corpus are complete. Those remain later phases and are deliberately not hidden behind the orchestration contract.

### Phase 6 — Semantic Digital Copy layer — **COMPLETE FOR GENERIC CONTRACT ✅ / PRODUCT INTEGRATION OPEN**

Implemented and CI-verified:

- atomic normative units;
- exact normative operators;
- conditions and exceptions;
- applicability/type links;
- table/formula rule registry primitives and validation;
- dependency/cross-reference graph;
- deterministic target resolution (`RESOLVED`, `UNRESOLVED`, `AMBIGUOUS`);
- deterministic source-bound semantic evaluation;
- amendment/deletion actions (`ADD`, `REPLACE`, `DELETE`);
- complete semantic provenance validation;
- fail-closed semantic acceptance.

Remaining at product level: integrate these artifacts into one coherent Digital Copy workflow and expose their state/evidence through the user interface.

### Phase 7 — Graphical verification — **IN PROGRESS 🔄**

Generic graphical verification must become an explicit evidence-producing workflow, not merely a validator.

Remaining:

- page/region evidence model;
- source-page viewer integration;
- critical-element verification workflow;
- evidence records for tables, formulas, operators, numbers, units, notes, footnotes, numbering and amendments/deletions;
- fail-closed handling when visual verification is unavailable;
- regression fixtures for graphical verification.

### Phase 8 — Revision lock and independent verification — **COMPLETE FOR CORE CONTRACT / OPERATIONAL WORKFLOW OPEN ▶️**

Implemented and CI-verified:

- immutable revision lock;
- deterministic revision ID;
- reproducibility manifest;
- self-contained package creation and replay;
- independent AI verification records;
- distinct independence bases;
- final acceptance validation.

Remaining operational work:

- integrate these artifacts into the end-to-end Digital Copy lifecycle;
- complete `Rev_<NNN>_<DOCUMENT_ID>_<DATE>` archive workflow;
- explicit operational verification archive;
- user-visible verification/acceptance status.

### Phase 9 — Generic Digital Copy User Interface — **OPEN ⏳**

Build the normal user-facing workflow around the already implemented engine contracts.

Minimum screens/states:

1. **Projects / Digital Copies** — list documents, lifecycle status, revision and blockers.
2. **Create Digital Copy** — upload/select PDF and start a run.
3. **Source Identity** — designation, title, edition, amendments, issuer, source URL, hash and source status.
4. **Extraction** — parser progress/results and evidence-only warning.
5. **Structure** — page/section/paragraph/list/table/cell/formula/anchor inspection.
6. **Discrepancies** — parser/external differences, evidence and resolution state.
7. **Semantics** — normative operators, conditions, applicability, dependencies, tables/formulas, amendments.
8. **Graphical Verification** — source page/region alongside the digital element and verification action.
9. **Verification** — independent AI records, scope, result and evidence.
10. **Acceptance** — complete acceptance chain, blockers and exact reason for `DIGITAL_ACCEPTED` or blocked status.
11. **Export / Handoff** — package, manifest, revision lock and downstream handoff.

The UI must never display unresolved content as accepted normative truth.

### Phase 10 — Generic end-to-end regression suite — **OPEN ⏳**

Before real normative-document validation, create a synthetic/controlled fixture corpus covering:

- text-native PDFs;
- scanned/OCR PDFs;
- multi-column layouts;
- complex tables and merged cells;
- formulas and special symbols;
- headers/footers and numbering;
- footnotes/notes;
- amendments/deletions;
- cross-references and ambiguous targets;
- parser disagreement;
- external-source disagreement;
- missing evidence and fail-closed cases;
- graphical verification evidence;
- revision-lock tampering;
- independent verification and final acceptance.

The objective is to prove the **generic block**, not to optimize for one document.

### Phase 11 — Real normative corpus validation — **NOT STARTED BY DESIGN ⏸️**

Only after Phases 5, 7, 8, 9 and 10 are closed should the system be exercised against real documents.

The validation corpus should include materially different document classes, for example:

- DBN;
- DSTU / DSTU EN;
- ISO / IEC;
- NFPA;
- laws, orders and technical regulations;
- scanned and text-native sources;
- table-heavy and formula-heavy sources;
- amended documents.

Each failure is classified by generic sub-block. The weakest sub-blocks become the next hardening targets.

### Phase 12 — Downstream domain integration — **AFTER GENERIC BLOCK ⏸️**

Only after the generic Digital Copy block is stable should the accepted representation be consumed by SPZ/engineering-specific normative registers, calculations and deterministic domain execution.

## 3. Current open work — priority order

### P0 — Graphical verification **← CURRENT STEP**

Turn visual checking into a first-class evidence-producing stage.

### P0 — User interface

Make the complete process operable by a user without manipulating internal Python artifacts.

### P1 — Operational verification / revision / handoff

Complete `Rev_NNN` archive lifecycle and operational independent-verification archive. The generic handoff artifact and package persistence contract are already present.

### P1 — Generic end-to-end regression

Prove the entire workflow on controlled fixtures before using real normative documents as the primary development driver.

### P2 — Real normative corpus

Run DBN plus a diverse set of other normative documents. Use the observed failure distribution to reprioritize generic hardening.

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

Phase 5 completion does not by itself satisfy this full product Definition of Done; it closes the canonicalization/persistence/workflow foundation required by the later phases.

## 5. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results remain historical and are not substituted for fresh execution.
