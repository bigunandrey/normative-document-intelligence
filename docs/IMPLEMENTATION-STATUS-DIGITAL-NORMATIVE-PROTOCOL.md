# Implementation Status — DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1

**Repository:** `normative-document-intelligence`  
**Status basis:** current `main` implementation and CI-verified commits  
**Strategy revision:** 2026-09-15

## 1. Status vocabulary

- **COMPLETE** — generic NDI contract is implemented and covered by tests/CI.
- **PARTIAL** — a material subset is implemented, but the complete generic contract is not closed.
- **OPEN** — not yet implemented or not yet proven end-to-end.
- **DOWNSTREAM BY DESIGN** — belongs to a domain-specific normative/engineering layer.
- **HISTORICAL EVIDENCE ONLY** — evidence migrated from earlier work; not fresh NDI execution.
- **BLOCKED** — validation requires an unavailable external prerequisite.

A `COMPLETE` generic contract does not imply that any particular normative document is already `DIGITAL_ACCEPTED`.

## 2. Executive result — current state

The generic NDI engine has CI-verified contracts for source identity, parser-neutral canonical structure, multi-parser reconciliation, authoritative-source comparison, canonical Digital Copy persistence/replay, typed production orchestration, semantic representation, graphical verification evidence, revision locking, independent verification, operational revision archiving and the generic Digital Copy UI.

Phases 8, 9 and 10 are closed at the generic contract level. Phase 10 closure is documented in `docs/PHASE-10-CLOSURE-2026-09-15.md`. Its final regression implementation head was `98dfd927352a7e10d4c03e37af9cd432884b73f7`; GitHub Actions run `34984635942` / test job `104433472094` completed successfully. Phase 11 is now the active real-corpus validation gate.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **COMPLETE FOR GENERIC CONTRACT** | Generic lifecycle and representative E2E matrix closed; real-corpus generalization is Phase 11. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **COMPLETE FOR GENERIC CONTRACT** | Source-bound artifact contracts plus representative E2E coverage; real-content validation remains Phase 11. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical/revision contracts. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations are evidence; canonical acceptance is separate. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation/external comparison retain discrepancies and fail closed; E2E fixtures are green. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Exact normative semantic operators and fail-closed ambiguity handling. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic, orchestration, graphical and archive boundaries fail closed. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Source-bound evidence/provenance required. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Domain-level register responsibility. |
| §5 | Isolated per-document package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff package and replay. |
| §6 | AI-Revisions archive | **COMPLETE FOR GENERIC OPERATIONAL CONTRACT** | Immutable `Rev_NNN`, bindings, verification evidence and tamper detection; lifecycle integration implemented. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol defines it; runtime enforcement remains a product-policy concern. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | Identity/source/revision binding implemented; live legal/current-edition discovery remains provider/workflow dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Package-local source copy + SHA-256 verification. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Typed extraction evidence and persistent extraction log; text-native/OCR-like boundary fixtures are green. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Normative-unit contract and validation. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Source-bound semantic fields implemented; unresolved-state E2E is green. |
| §13 | Table decomposition with notes/footnotes/special markers | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Critical visual evidence covers tables/notes/footnotes; real table reconstruction remains Phase 11 validation. |
| §14 | Formula extraction + graphical/machine verification | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Formula/graphical contracts and representative visual E2E fixture are green; real extraction/reconstruction remains Phase 11 validation. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | ADD/REPLACE/DELETE actions and fail-closed target validation; representative amendment/deletion E2E coverage is green. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, retrieval, integrity, parsing and comparison; discrepancy/agreement E2E fixture is green. |
| §17 | Graphical verification | **COMPLETE FOR GENERIC EVIDENCE + ORCHESTRATION CONTRACT** | Page/region evidence, UI display, fail-closed validation and orchestration E2E success/mismatch. |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation. |
| §19 | ≥2 independent AI verification records | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records, acceptance validation and operational archive integration; insufficient-count E2E fixture is green. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Normative-register synchronization is downstream. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is persisted and linked to accepted job state. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **COMPLETE FOR GENERIC REGRESSION CONTRACT** | Phase 10 matrix closed; real-document rule interaction is Phase 11. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision/reproducibility bindings and tamper tests. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **COMPLETE FOR GENERIC CONTRACT** | Acceptance/archive/replay path and representative fail-closed matrix are green. |
| §25 | Full digitalization status vocabulary | **COMPLETE FOR GENERIC JOB/UI CONTRACT** | Lifecycle states, blockers, acceptance and archive state are persisted/displayed. |
| §26 | Full reproducibility through preserved artifacts | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Self-contained package, hashes and replay; source/artifact tamper E2E coverage is green. |
| §27 | AI must execute to factual result and leave explicit handoff if blocked | **PARTIAL** | Fail-closed orchestration and handoff artifact exist; runtime policy enforcement remains open. |

## 4. Phase 10 closure

Phase 10 is closed for the generic Digital Copy contract. The closure matrix is recorded in `docs/PHASE-10-CLOSURE-2026-09-15.md` and includes lifecycle, reconciliation, external-source, graphical, semantic, critical visual, amendment/deletion, extraction, tamper, verification, archive/replay and UI persistence cases.

The closure does not claim completion of any real normative document.

## 5. Phase 11 — real normative corpus validation

Phase 11 is the active validation gate. The engine should now be exercised against a deliberately diverse authoritative corpus including DBN, DSTU/DSTU EN, ISO/IEC, NFPA and legal/regulatory sources where available.

The corpus must include text-native and scanned PDFs, tables, formulas, notes/footnotes, amendments/deletions and complex layouts. Each failure is classified by generic subsystem. Generic capability gaps are fixed in the engine and added to regression coverage; document-specific exceptions are not used as substitutes for generic fixes.

## 6. Phase 12 — downstream integration

After Phase 11 establishes generalization, accepted Digital Copies can be consumed by normative registers, SPZ semantics and engineering calculation/execution layers.

## 7. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
