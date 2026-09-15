# Phase 11 — Real Normative Corpus Register

**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Status:** `IN PROGRESS`  
**Started:** 2026-09-15

## Purpose

Phase 11 validates the generic Digital Copy workflow against real normative documents. Controlled fixtures and historical benchmark evidence are not treated as substitutes for fresh real-document execution.

## Corpus rules

Each corpus item must record:

- document identity and edition;
- authoritative source;
- source form (PDF, scanned/text-native where known);
- revision/amendment state;
- local source SHA-256 after acquisition;
- extraction characteristics;
- tables/formulas/notes/footnotes/change markers present;
- workflow result;
- discrepancies and blockers;
- subsystem classification of every generic capability gap;
- regression fixture created for every generic fix.

A document is not marked `DIGITAL_ACCEPTED` merely because an older benchmark or another repository already processed it.

## Corpus item 001 — DBN V.2.5-56:2014

### Identity

- **Document:** ДБН В.2.5-56:2014 «Системи протипожежного захисту»
- **Target revision:** latest edition with Changes №1 and №2, effective state after Change №2
- **Authoritative registry:** Єдина державна електронна система у сфері будівництва (ЄДЕССБ)
- **Authoritative document page:** `https://e-construction.gov.ua/laws_detail/3778939933176104875?doc_type=2`
- **Authoritative current consolidated text:** 2025 controlled-state consolidated text with Changes №1 and №2
- **Change №2:** effective 2026-03-01

### Available project source

A File Library copy of the consolidated document is available as:

`ДБН В.2.5-56_2014 Системи протипожежного захисту зі Зміною № 1 та 2.pdf`

The indexed copy identifies itself as the 2025 consolidated text with Changes №1 and №2 and contains amendment markers such as additions and deletions introduced by Change №2.

### Historical evidence

A previous NDI benchmark exists under `benchmarks/dbn-v2.5-56-2014/`. Its historical SHA-256 is:

`fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056`

That evidence remains historical evidence only. It is not reused as fresh Phase 11 execution evidence.

### Phase 11 execution state

`SOURCE_IDENTIFIED` → `AUTHORITATIVE_SOURCE_VERIFIED` → `ACQUISITION_PENDING`

Fresh execution requires acquisition of the authoritative PDF bytes into the execution environment so the current source can be hashed and passed through the current generic workflow. No current-head Phase 11 acceptance is claimed until that execution is completed.

## Planned diversity after item 001

The next corpus items should deliberately add:

1. a text-native DSTU/DSTU EN normative document;
2. a scanned/OCR-heavy normative document;
3. a document with dense numerical/formula tables;
4. a document with extensive amendments/deletions;
5. an international normative document (ISO/IEC or NFPA) where an authoritative copy is legally available to the project.

The exact document is selected only after authoritative source availability and revision identity are established.

## Failure policy

- Generic parser/extraction/reconciliation/verification defects become regression fixtures.
- Document-specific source anomalies remain document-specific evidence and do not weaken the generic contract.
- No silent fallback from authoritative source to an uncontrolled copy.
- No `DIGITAL_ACCEPTED` on incomplete evidence.
