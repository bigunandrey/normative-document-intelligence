# Implementation Status — DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1

**Repository:** `bigunandrey/normative-document-intelligence`  
**Status basis:** current `main` implementation and CI-verified commits  
**Strategy revision:** 2026-09-15

## 1. Status vocabulary

- **COMPLETE** — generic NDI contract is implemented and covered by tests/CI.
- **PARTIAL** — a material subset is implemented, but the complete generic contract is not closed.
- **OPEN** — not yet implemented or not yet proven end-to-end.
- **DOWNSTREAM BY DESIGN** — belongs to a domain-specific normative/engineering layer, not the generic PDF → Digital Copy engine.
- **HISTORICAL EVIDENCE ONLY** — evidence migrated from earlier work; not fresh NDI execution.
- **BLOCKED** — implementation may exist, but validation is blocked by unavailable real-document bytes or another external prerequisite.

A `COMPLETE` generic contract does not imply that any particular normative document is already `DIGITAL_ACCEPTED`.

## 2. Executive result — current state

The generic NDI engine has progressed substantially beyond the former structural-only boundary. The following blocks are implemented and CI-verified:

1. Source identity, metadata and SHA-256 binding.
2. Parser-neutral canonical structural document model.
3. Multi-parser adapter/observation contract with provenance validation.
4. Cross-parser matching, reconciliation and retained discrepancies.
5. Fail-closed structural verification gates A–C.
6. External authoritative-source discovery, retrieval, integrity verification and multi-parser external comparison.
7. Digital representation persistence, self-contained package creation/replay and immutable revision lock.
8. Stage-evidence contract and production Digital Copy orchestration boundary with deterministic persistence after each material stage.
9. Persistent extraction log, stage-evidence history and first-class handoff artifact.
10. Independent AI verification records and final acceptance contract.
11. Atomic normative semantic decomposition with exact normative operators.
12. Conditions, exceptions and applicability/type links.
13. Table/formula rule registry primitives and validation.
14. Dependency/cross-reference graph and deterministic target resolution.
15. Deterministic semantic evaluation with fail-closed unresolved states.
16. Amendment/deletion actions with explicit ADD/REPLACE/DELETE semantics.
17. Complete semantic provenance validation back to canonical nodes/source evidence.
18. Fail-closed semantic acceptance validation.

Phase 5 — Canonical Digital Copy and persistence — is now **COMPLETE FOR GENERIC CONTRACT**. The next implementation priority is graphical verification; UI and end-to-end fixture work follow as product-level requirements.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **PARTIAL** | Generic orchestration/persistence foundation is complete; user-facing workflow and all concrete document-stage integrations remain open. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **PARTIAL** | Generic artifacts for all major links exist; complete concrete end-to-end pipeline remains open. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical model, registry and revision-lock checks. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations remain evidence; canonical acceptance is separated from extraction. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation and external comparison retain discrepancies and fail closed. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Normative semantic decomposition supports exact requirement/prohibition/recommendation/permission operators; ambiguous modalities fail closed. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic and orchestration boundaries fail closed. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Semantic acceptance/provenance chain requires source-bound evidence. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Master SPZ register is domain/project-level. Generic NDI defines the evidence needed to update it. |
| §5 | Isolated per-document `reference-data/<DOCUMENT_ID>` package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Self-contained package, source copy, manifest, stage evidence, extraction log and handoff artifact are persisted and replayable. Concrete reference-data archive naming remains operational work. |
| §6 | AI-Revisions archive | **PARTIAL** | Immutable revision-lock/verification primitives exist; complete `Rev_NNN` operational archive workflow remains open. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol exists and defines the rule; runtime enforcement/checklist is not yet implemented. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | `DocumentIdentity`, source registry and revision binding implemented; legal/current-edition discovery remains workflow/provider dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Source SHA-256 binding plus package-local source persistence and verification are implemented. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Extraction stage is orchestrated through typed evidence and a persistent extraction-log artifact; concrete parser execution remains injected/document-specific. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | `NormativeUnit` decomposition and validation are implemented. Real-document coverage remains validation work. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Subject/predicate/condition/exception/modality and related source-bound fields implemented. |
| §13 | Table decomposition with notes/footnotes/special markers | **PARTIAL** | Canonical table/cell model and registry exist; robust parser-specific reconstruction + graphical verification are open. |
| §14 | Formula extraction + graphical/machine verification | **PARTIAL** | Formula node/registry contracts exist; full formula extraction and visual verification are open. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | Explicit source-bound ADD/REPLACE/DELETE actions and validation implemented. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, validation, retrieval, independent parsing and comparison implemented; real-source evidence is document-specific. |
| §17 | Graphical verification | **PARTIAL** | Validator exists and is fail-closed, but page/region evidence capture and user workflow remain open. |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation implemented. |
| §19 | ≥2 independent AI verification records for `DIGITAL_ACCEPTED` | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records, distinct independence bases and final acceptance validation implemented. Operational orchestration is not yet the final production evidence chain. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Synchronization belongs to the normative register layer; NDI exposes handoff state. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is generated from the accepted/blocked package state and points to the downstream normative-domain handoff. Operational downstream integration remains open. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **PARTIAL** | Strong unit/regression coverage exists; complete document-package regression workflow remains open. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision lock, deterministic revision ID and reproducibility manifest implemented. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **PARTIAL** | Orchestrator now reaches the acceptance boundary and persists its state; complete evidence-driven final gate integration remains open. |
| §25 | Full digitalization status vocabulary | **PARTIAL** | Gate statuses and deterministic job lifecycle exist; user-facing lifecycle remains open. |
| §26 | Full reproducibility through preserved artifacts | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff are persisted, hashes are verified and replay uses package-local paths. Full pipeline artifact population remains document-stage dependent. |
| §27 | AI must execute to factual result and leave explicit handoff if blocked | **PARTIAL** | Fail-closed orchestration and handoff artifact exist; runtime operating-policy enforcement remains open. |

## 4. Phase 5 closure record

Phase 5 closes the canonical Digital Copy/persistence foundation, not the entire product.

The closed generic contract now provides:

```text
DigitalCopyJob
   ↓
Typed StageEvidence
   ↓
Stage binding validation
   ↓
Per-stage job persistence
   ↓
Self-contained source + artifact package
   ↓
Stage-evidence history + extraction log
   ↓
Revision/package bindings
   ↓
Replay with package-local paths
   ↓
Acceptance state
   ↓
Handoff artifact
```

The implementation deliberately leaves concrete graphical evidence capture, user interface, independent verification workflow integration and generic E2E fixture execution to their dedicated phases. No unresolved capability is hidden by declaring Phase 5 complete.

## 5. What is deliberately NOT the next priority

**Do not make a single DBN benchmark the development driver at this stage.**

The DBN fixture remains useful as an eventual acceptance/regression document, but running it now would mostly reveal document-specific gaps before the generic product workflow is finished. The same applies to immediately processing other normative PDFs.

The preferred sequence is:

```text
GENERIC PDF
   ↓
USER WORKFLOW / UI
   ↓
IDENTITY + SOURCE INTEGRITY
   ↓
MULTI-PARSER OBSERVATIONS
   ↓
RECONCILIATION / DISCREPANCIES
   ↓
EXTERNAL SOURCE CHECK
   ↓
CANONICAL DIGITAL COPY
   ↓
TABLES / FORMULAS / CHANGES / DEPENDENCIES
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
ONLY THEN: RUN A DIVERSE SET OF REAL NORMATIVE DOCUMENTS
```

## 6. User-facing product requirement — Digital Copy workspace

The generic engine needs a normal user workflow, not a collection of internal Python contracts.

Minimum user journey:

1. **Create Digital Copy** — upload/select a normative PDF.
2. **Identify source** — designation, title, edition, amendments, issuer, date/status, source URL and SHA-256.
3. **Inspect extraction** — show parser status and extraction evidence without presenting it as accepted truth.
4. **Review structure** — pages, sections, paragraphs, lists, tables, cells, formulas, headers/footers and anchors.
5. **Review discrepancies** — show parser/external conflicts with source evidence and explicit resolution states.
6. **Review semantic layer** — normative operators, conditions, exceptions, applicability, dependencies, tables/formulas and amendments.
7. **Graphical verification** — open the source page/region next to the digital element and record verification evidence.
8. **Verification** — show required independent AI reviews and their scope/results.
9. **Acceptance** — display exactly why the document is or is not `DIGITAL_ACCEPTED`.
10. **Export/package** — produce the reproducible digital-copy package, revision lock and evidence manifest.

The UI must be **fail-closed by presentation as well as by code**: unresolved items cannot be visually represented as accepted facts.

## 7. Real-document validation strategy after the generic block is complete

Validation should use a deliberately diverse corpus rather than only DBN:

- text-native PDF;
- scanned/OCR PDF;
- complex tables;
- formula-heavy document;
- document with footnotes/endnotes;
- document with amendments/deletions;
- multi-column layout;
- headers/footers and numbering-heavy document;
- documents from different normative systems (e.g. DBN, DSTU, ISO/IEC, NFPA, laws/regulations).

The corpus should be selected to exercise different failure modes. DBN is one acceptance document, not the definition of the generic engine.

## 8. Current open work — ordered

### P0 — Graphical verification **CURRENT STEP**

- Implement source-page/region evidence capture.
- Add critical-element verification workflow.
- Persist graphical evidence and fail closed when visual evidence is unavailable.

### P0 — Generic Digital Copy UI

- Define and implement the user-facing Digital Copy workspace.
- Expose gate states, discrepancies, evidence and unresolved blockers.

### P1 — Operational verification / revision / handoff

- Complete `Rev_NNN` archive lifecycle and operational independent-verification archive.
- Connect the existing handoff artifact to downstream workflows.

### P1 — Generic regression / fixtures

- Build controlled fixtures and E2E tests across the complete generic pipeline.

### P2 — Real normative corpus validation

Only after P0/P1 are closed, run a diverse real-document corpus including DBN and other normative systems. Use failures to identify the weakest generic sub-blocks and return those blocks to P0/P1 for hardening.

### P3 — Downstream domain integration

Only after generic Digital Copy is stable, connect the accepted representation to domain-specific normative registers, SPZ engineering semantics and calculation/execution engines.

## 9. Definition of generic Digital Copy completion

The generic block is considered complete when a user can submit a normative PDF and, without manually manipulating internal implementation artifacts, obtain:

- immutable source identity;
- multi-parser evidence;
- reconciled canonical structure;
- explicit discrepancy register;
- source-bound semantic/table/formula/change/dependency artifacts;
- graphical verification evidence;
- revision-locked digital representation;
- independent verification evidence;
- regression result;
- reproducibility manifest;
- a clear final status: accepted or blocked, with every blocker explicit.

Phase 5 is a prerequisite foundation for this final product definition; it is not itself the final product definition.

## 10. Important status distinction

`PASS` from an individual gate is not equivalent to protocol-level `DIGITAL_ACCEPTED`.

`DIGITAL_ACCEPTED` is a lifecycle result produced only when the complete required evidence chain is present and valid. A document-specific benchmark cannot close generic implementation gaps by itself.
