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

Phase 8 and Phase 9 are now closed at the generic contract level. The exact current-head CI run for the latest Phase 10 implementation commit is green. Phase 10 remains the active gate: the controlled E2E regression matrix must be expanded and proven before real normative-corpus validation.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **PARTIAL** | Generic contracts are implemented; complete generic E2E proof is Phase 10. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **PARTIAL** | Generic links exist; complete representative E2E proof remains Phase 10. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical/revision contracts. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations are evidence; canonical acceptance is separate. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation/external comparison retain discrepancies and fail closed. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Exact normative semantic operators and fail-closed ambiguity handling. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic, orchestration, graphical and archive boundaries fail closed. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Source-bound evidence/provenance required. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Domain-level register responsibility. |
| §5 | Isolated per-document package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff package and replay. |
| §6 | AI-Revisions archive | **COMPLETE FOR GENERIC OPERATIONAL CONTRACT** | Immutable `Rev_NNN`, bindings, verification evidence and tamper detection; lifecycle integration is implemented. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol defines it; runtime enforcement remains a product-policy concern. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | Identity/source/revision binding implemented; live legal/current-edition discovery remains provider/workflow dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Package-local source copy + SHA-256 verification. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Typed extraction evidence and persistent extraction log. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Normative-unit contract and validation. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Source-bound semantic fields implemented. |
| §13 | Table decomposition with notes/footnotes/special markers | **PARTIAL** | Generic nodes/registry exist; robust reconstruction is a Phase 10/11 validation concern. |
| §14 | Formula extraction + graphical/machine verification | **PARTIAL** | Generic formula and graphical evidence contracts exist; concrete extraction/reconstruction coverage remains. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | ADD/REPLACE/DELETE actions and validation. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, retrieval, integrity, parsing and comparison. |
| §17 | Graphical verification | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Page/region evidence, UI display and fail-closed validation. |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation. |
| §19 | ≥2 independent AI verification records | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records, acceptance validation and operational archive integration. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Normative-register synchronization is downstream. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is persisted and linked to accepted job state. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **PARTIAL** | Unit coverage is strong; Phase 10 generic E2E matrix remains active. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision/reproducibility bindings. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **PARTIAL** | Orchestration and UI reach the acceptance boundary; Phase 10 must prove representative full-chain execution. |
| §25 | Full digitalization status vocabulary | **COMPLETE FOR GENERIC JOB/UI CONTRACT** | Lifecycle states, blockers, acceptance and archive state are persisted/displayed. |
| §26 | Full reproducibility through preserved artifacts | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Self-contained package, hashes and replay. |
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

Implemented and regression-tested:

- sequential `Rev_001`, `Rev_002`, … identifiers;
- one archive per locked revision;
- source/document/revision binding;
- reproducibility-manifest preservation;
- independent verification evidence preservation;
- verification evidence hash validation;
- duplicate-revision archival rejection;
- manifest tamper detection;
- verification-record tamper detection;
- blocked archive creation when the locked revision is unavailable/invalid;
- orchestrator archive integration;
- UI archive/status integration;
- persisted archive identity/result/verification metadata.

Production authentication/authorization remains outside the generic engine contract.

## 5. Phase 9 closure

Phase 9 is closed for the generic UI contract. The UI provides PDF intake, immutable package-local source storage, SHA-256 visibility, lifecycle/status presentation, job APIs, source viewing, graphical evidence presentation, blocker/acceptance presentation, workflow-runner integration and operational archive status.

Rich PDF overlays and deployment-specific authentication are hardening/deployment concerns, not generic-contract blockers.

## 6. Phase 10 — active gate

The initial generic E2E fixture suite is implemented and CI-verified. It proves:

- successful run → `DIGITAL_ACCEPTED` → revision lock → two independent verifiers → `Rev_001` archive → archive verification;
- missing-stage blocking;
- failed-stage blocking;
- archive binding regression coverage.

The matrix must now be expanded to representative extraction/reconciliation/semantic/graphical/tamper/degraded cases and remain green on the exact current `main` head.

## 7. Current open work — ordered

### P0 — Phase 10 generic E2E regression **CURRENT STEP**

Expand the controlled fixture matrix and close the generic E2E gate.

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
