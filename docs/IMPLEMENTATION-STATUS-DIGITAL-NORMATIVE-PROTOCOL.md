# Implementation Status — DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1

**Repository:** `bigunandrey/normative-document-intelligence`  
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

Phase 8 and Phase 9 are closed at the generic contract level. Phase 10 is active. The current green Phase 10 head is `ed758a9e8a6a17640b9b0401f10cda5a7e0130fe` (GitHub Actions run `34982088833`). The expanded regression milestone adds package/source tamper detection and insufficient-verifier archive blocking to the end-to-end matrix.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **PARTIAL** | Generic contracts are implemented; complete generic E2E proof is Phase 10. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **PARTIAL** | Generic links exist; representative E2E proof remains Phase 10. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical/revision contracts. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations are evidence; canonical acceptance is separate. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation/external comparison retain discrepancies and fail closed. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Exact normative semantic operators and fail-closed ambiguity handling. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic, orchestration, graphical and archive boundaries fail closed. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Source-bound evidence/provenance required. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Domain-level register responsibility. |
| §5 | Isolated per-document package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff package and replay. |
| §6 | AI-Revisions archive | **COMPLETE FOR GENERIC OPERATIONAL CONTRACT** | Immutable `Rev_NNN`, bindings, verification evidence and tamper detection; lifecycle integration implemented. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol defines it; runtime enforcement remains a product-policy concern. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | Identity/source/revision binding implemented; live legal/current-edition discovery remains provider/workflow dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Package-local source copy + SHA-256 verification. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Typed extraction evidence and persistent extraction log. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Normative-unit contract and validation. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Source-bound semantic fields implemented. |
| §13 | Table decomposition with notes/footnotes/special markers | **PARTIAL** | Generic nodes/registry exist; robust reconstruction remains a Phase 10/11 validation concern. |
| §14 | Formula extraction + graphical/machine verification | **PARTIAL** | Generic formula and graphical evidence contracts exist; concrete extraction/reconstruction coverage remains. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | ADD/REPLACE/DELETE actions and validation. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, retrieval, integrity, parsing and comparison. |
| §17 | Graphical verification | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Page/region evidence, UI display and fail-closed validation; orchestration integration remains P10. |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation. |
| §19 | ≥2 independent AI verification records | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records, acceptance validation and operational archive integration; insufficient-count E2E fixture now verified. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Normative-register synchronization is downstream. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is persisted and linked to accepted job state. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **PARTIAL** | Unit coverage is strong; complete Phase 10 generic E2E matrix remains active. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision/reproducibility bindings and tamper tests. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **PARTIAL** | Full acceptance path is E2E-proven; broader representative matrix remains Phase 10 gate. |
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

Phase 9 is closed for the generic UI contract. The UI provides PDF intake, immutable package-local source storage, SHA-256 visibility, lifecycle/status presentation, job APIs, source viewing, graphical evidence presentation, blocker/acceptance presentation, workflow-runner integration and operational archive status.

Rich PDF overlays and deployment-specific authentication are hardening/deployment concerns, not generic-contract blockers.

## 6. Phase 10 — active gate

The current CI-green fixture matrix proves:

- successful run → `DIGITAL_ACCEPTED` → revision lock → two independent verifiers → `Rev_001` archive → archive verification;
- missing-stage blocking;
- every orchestration-stage failure blocks acceptance;
- failed evidence without blockers is rejected;
- unsupported stage bindings are rejected;
- archive revision-binding tamper is detected;
- packaged artifact tamper is detected during replay;
- packaged source tamper is detected during replay;
- insufficient independent-verifier archive input is blocked;
- accepted package replay restores the accepted job state and verified archive metadata.

The remaining P0 work is to wire the existing isolated evidence contracts into the actual E2E boundaries and add representative content fixtures rather than only lifecycle fixtures.

## 7. Current open work — ordered

### P0 — Phase 10 generic E2E regression **CURRENT STEP**

Next block:

1. graphical verification success/mismatch through orchestration;
2. parser disagreement and missing-observation states through reconciliation;
3. external-source discrepancy/reconciliation;
4. semantic unresolved/ambiguous resolution blocking;
5. table/formula/note/footnote/numbering and amendment/deletion representative fixtures;
6. UI accepted/blocked persistence E2E;
7. final matrix evidence and Phase 10 closure.

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
