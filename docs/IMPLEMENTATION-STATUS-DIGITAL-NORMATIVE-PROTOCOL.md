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

Phase 8 and Phase 9 are closed at the generic contract level. Phase 10 is active. The current `main` head is `76701b3f60f344ae1651d0b48521dc8b0cc10327`; its CI run is `34984461609` and is the documentation-only follow-up to the green regression head `58654902e82596e66a0e81d1e950c1f04bac5547` / run `34984364656`. The expanded regression milestone covers graphical verification, reconciliation conflict/missing observation, external-source discrepancy, semantic unresolved state, critical visual elements, amendment handling, package/source tamper, insufficient verification and UI restart persistence.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **PARTIAL** | Generic contracts are implemented; final generic E2E matrix/closure is Phase 10. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **PARTIAL** | Generic links exist; final content-fixture matrix remains Phase 10. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical/revision contracts. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations are evidence; canonical acceptance is separate. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation/external comparison retain discrepancies and fail closed; E2E conflict/missing/external fixtures are green. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Exact normative semantic operators and fail-closed ambiguity handling. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic, orchestration, graphical and archive boundaries fail closed; current E2E matrix is green. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Source-bound evidence/provenance required. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Domain-level register responsibility. |
| §5 | Isolated per-document package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff package and replay. |
| §6 | AI-Revisions archive | **COMPLETE FOR GENERIC OPERATIONAL CONTRACT** | Immutable `Rev_NNN`, bindings, verification evidence and tamper detection; lifecycle integration implemented. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol defines it; runtime enforcement remains a product-policy concern. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | Identity/source/revision binding implemented; live legal/current-edition discovery remains provider/workflow dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Package-local source copy + SHA-256 verification. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Typed extraction evidence and persistent extraction log. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Normative-unit contract and validation. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Source-bound semantic fields implemented; unresolved-state E2E is green. |
| §13 | Table decomposition with notes/footnotes/special markers | **PARTIAL** | Generic nodes/registry and critical visual evidence are covered; concrete table reconstruction remains a real-content validation concern. |
| §14 | Formula extraction + graphical/machine verification | **PARTIAL** | Generic formula and graphical evidence contracts are covered; concrete extraction/reconstruction remains a real-content validation concern. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | ADD/REPLACE/DELETE actions and validation; representative replacement and unresolved deletion-target E2E fixtures are green. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, retrieval, integrity, parsing and comparison; discrepancy/agreement E2E fixture is green. |
| §17 | Graphical verification | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Page/region evidence, UI display, fail-closed validation and orchestration E2E success/mismatch. |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation. |
| §19 | ≥2 independent AI verification records | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records, acceptance validation and operational archive integration; insufficient-count E2E fixture is green. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Normative-register synchronization is downstream. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is persisted and linked to accepted job state. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **PARTIAL** | Representative generic E2E coverage is now broad; final matrix and real-corpus validation remain. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision/reproducibility bindings and tamper tests. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **PARTIAL** | Complete lifecycle path plus representative fail-closed/content fixtures is green; final closure evidence remains. |
| §25 | Full digitalization status vocabulary | **COMPLETE FOR GENERIC JOB/UI CONTRACT** | Lifecycle states, blockers, acceptance and archive state are persisted/displayed. |
| §26 | Full reproducibility through preserved artifacts | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Self-contained package, hashes and replay; source/artifact tamper E2E coverage is green. |
| §27 | AI must execute to factual result and leave explicit handoff if blocked | **PARTIAL** | Fail-closed orchestration and handoff artifact exist; runtime policy enforcement remains open. |

## 4. Phase 8 closure

Phase 8 is closed for the generic operational contract:

```text
Immutable source
      ↓
Revision Lock
      ↓
Reproducibility Manifest
      ↓
≥2 Independent Verification Records
      ↓
Rev_NNN immutable archive
      ↓
Archive binding + hash verification
      ↓
Tamper detection / fail-closed result
      ↓
Digital Copy job + handoff integration
```

## 5. Phase 9 closure

Phase 9 is closed for the generic UI contract. The UI provides PDF intake, immutable package-local source storage, SHA-256 visibility, lifecycle/status presentation, job APIs, source viewing, graphical evidence presentation, blocker/acceptance presentation, workflow-runner integration and operational archive status. Accepted/archive state is also covered across a UI restart.

Rich PDF overlays and deployment-specific authentication are hardening/deployment concerns, not generic-contract blockers.

## 6. Phase 10 — active gate

The CI-green fixture matrix currently proves:

- successful run → `DIGITAL_ACCEPTED` → revision lock → two independent verifiers → `Rev_001` archive → archive verification;
- missing-stage blocking;
- every orchestration-stage failure blocks acceptance;
- failed evidence without blockers is rejected;
- unsupported stage bindings are rejected;
- parser disagreement and missing-observation states through reconciliation;
- external-source discrepancy blocks while same-revision agreement permits progression;
- graphical verification success/mismatch through orchestration;
- critical visual evidence for tables, formulas, notes, footnotes and numbering;
- semantic unresolved-state blocking;
- amendment replacement resolution and unresolved deletion target blocking;
- archive revision-binding tamper detection;
- packaged artifact/source tamper detection during replay;
- insufficient independent-verifier archive input is blocked;
- accepted/archive state persists across UI restart.

The remaining P0 work is limited to extraction-content fixtures (text-native and OCR-like/scanned) and the final complete-matrix closure evidence.

## 7. Current open work — ordered

### P0 — Phase 10 generic E2E regression **CURRENT STEP**

1. text-native extraction fixture through the configured parser/extraction boundary;
2. OCR-like/scanned extraction fixture with explicit evidence/fail-closed behavior;
3. final complete-matrix evidence document and Phase 10 closure review.

### P1 — Generic product hardening

Non-blocking robustness and UX improvements discovered during Phase 10.

### P2 — Real normative corpus validation

DBN plus a diverse normative corpus, only after Phase 10 closes. Failures become generic regression fixtures where appropriate.

### P3 — Downstream domain integration

Connect accepted Digital Copies to normative registers, SPZ semantics and engineering calculation/execution layers.

## 8. Definition of generic Digital Copy completion

The generic product is complete only when a user can submit a normative PDF and, through the normal UI, obtain immutable identity, multi-parser evidence, canonical structure, discrepancy resolution, semantic/table/formula/change/dependency artifacts, graphical evidence, revision lock, independent verification, operational revision archive, regression, reproducibility manifest, handoff and a final accepted/blocked state.

Phase 8 and Phase 9 satisfy their generic contracts. Phase 10 is the remaining generic completion gate.

## 9. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.

Historical DBN benchmark results are not substituted for fresh execution.
