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

The generic NDI engine has CI-verified contracts for source identity, parser-neutral canonical structure, multi-parser reconciliation, authoritative-source comparison, canonical Digital Copy persistence/replay, typed production orchestration, semantic representation and graphical verification evidence.

The latest completed implementation step is **Phase 7 — Graphical Verification generic evidence contract**. It now records source-bound page/region evidence for critical visual elements, validates source hash/coordinates/verifier/time, blocks mismatches and unresolved discrepancies, and persists a deterministic evidence artifact with SHA-256.

Remaining gaps are product/operational: user-facing PDF viewer/UI, operational independent-verification archive, generic full-pipeline E2E fixtures and real-document validation.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | Current NDI status | Evidence / remaining work |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | **PARTIAL** | Generic engine contracts are substantial; user-facing production product remains open. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | **PARTIAL** | Generic links exist; complete concrete end-to-end pipeline remains open. |
| §3.1 | Source of truth + metadata + SHA-256 | **COMPLETE** | Source-bound canonical/revision contracts. |
| §3.2 | Extraction is evidence, not normative truth | **COMPLETE** | Parser observations are evidence; canonical acceptance is separate. |
| §3.3 | No silent correction; discrepancies retained | **COMPLETE** | Reconciliation/external comparison retain discrepancies and fail closed. |
| §3.4 | Preserve normative operators exactly | **COMPLETE** | Exact normative semantic operators and fail-closed ambiguity handling. |
| §3.5 | Fail-closed on missing evidence | **COMPLETE** | Structural, semantic, orchestration and graphical evidence boundaries fail closed. |
| §3.6 | AI inference ≠ normative requirement | **COMPLETE** | Source-bound evidence/provenance required. |
| §4 | Two master normative-register files | **DOWNSTREAM BY DESIGN** | Domain-level register responsibility. |
| §5 | Isolated per-document package | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Source/job/manifest/stage evidence/extraction log/handoff package and replay. |
| §6 | AI-Revisions archive | **PARTIAL** | Core revision/verification primitives exist; operational `Rev_NNN` archive remains open. |
| §7 | Mandatory pre-work protocol reading/state inspection | **PARTIAL** | Protocol defines it; runtime enforcement remains open. |
| §8 | Source identification + edition/amendments | **COMPLETE FOR CORE IDENTITY** | Identity/source/revision binding implemented; live legal/current-edition discovery remains provider/workflow dependent. |
| §9 | Capture immutable primary source | **COMPLETE** | Package-local source copy + SHA-256 verification. |
| §10 | Full extraction + extraction log | **COMPLETE FOR GENERIC WORKFLOW CONTRACT** | Typed extraction evidence and persistent extraction log. |
| §11 | Atomic normative decomposition | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Normative-unit contract and validation. |
| §12 | Semantic normalization fields | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Source-bound semantic fields implemented. |
| §13 | Table decomposition with notes/footnotes/special markers | **PARTIAL** | Generic nodes/registry exist; robust document reconstruction remains validation work. |
| §14 | Formula extraction + graphical/machine verification | **PARTIAL** | Generic formula contracts and graphical evidence exist; concrete extraction/reconstruction remains open. |
| §15 | Changes/deletions represented and traceable | **COMPLETE FOR GENERIC ACTION CONTRACT** | ADD/REPLACE/DELETE actions and validation. |
| §16 | External cross-check and discrepancy resolution | **COMPLETE FOR GENERIC ENGINE CONTRACT** | Discovery, retrieval, integrity, parsing and comparison. |
| §17 | Graphical verification | **COMPLETE FOR GENERIC EVIDENCE CONTRACT** | Page/region evidence model, critical-element taxonomy, source binding, source/observed text, match result, verifier/time, deterministic persistence and fail-closed validation. **PDF viewer/UI remains Phase 9.** |
| §18 | Dependency mapping | **COMPLETE FOR GENERIC SEMANTIC CONTRACT** | Dependency graph, exact target resolution and fail-closed validation. |
| §19 | ≥2 independent AI verification records | **COMPLETE FOR GENERIC ACCEPTANCE CONTRACT** | Independent records and final acceptance validation. Operational archive/workflow remains open. |
| §20 | Update master MD/XLSX after verification | **DOWNSTREAM BY DESIGN** | Normative-register synchronization is downstream. |
| §21 | Explicit handoff protocol | **COMPLETE FOR GENERIC ARTIFACT CONTRACT** | Handoff artifact is persisted; downstream execution remains open. |
| §22 | Regression of related rules/tables/formulas/downstream logic | **PARTIAL** | Unit/regression coverage exists; full generic E2E workflow remains open. |
| §23 | Source hash / digital revision lock | **COMPLETE FOR GENERIC CONTRACT** | Immutable revision/reproducibility bindings. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | **PARTIAL** | Orchestration reaches acceptance boundary; complete evidence-driven production chain remains open. |
| §25 | Full digitalization status vocabulary | **PARTIAL** | Job lifecycle exists; user-facing lifecycle remains open. |
| §26 | Full reproducibility through preserved artifacts | **COMPLETE FOR GENERIC PACKAGE CONTRACT** | Self-contained package, hashes and replay. |
| §27 | AI must execute to factual result and leave explicit handoff if blocked | **PARTIAL** | Fail-closed orchestration and handoff artifact exist; runtime policy enforcement remains open. |

## 4. Phase 7 closure

Phase 7 is **COMPLETE FOR GENERIC EVIDENCE CONTRACT**.

The closed contract is:

```text
Source SHA-256
      ↓
Page / Region
      ↓
Critical Element Kind
      ↓
Source Text ↔ Observed Text
      ↓
Per-item Match
      ↓
Verifier + Timestamp
      ↓
Bundle Validation
      ↓
Deterministic graphical-evidence.json + SHA-256
```

Critical visual categories covered by the generic taxonomy:

- tables;
- formulas;
- normative operators;
- numeric values;
- units;
- notes;
- footnotes;
- numbering;
- amendments;
- deletions.

A PASS bundle cannot contain an unresolved discrepancy or an unmatched visual item. Invalid page/region data and source-hash mismatches are rejected.

### Explicit non-claims

Phase 7 does **not** claim:

- a PDF renderer/viewer;
- human click-through UI;
- automatic screenshot/region acquisition from arbitrary PDFs;
- document-specific visual correctness;
- real normative-document validation.

Those belong to Phase 9/UI and Phase 11/real-corpus validation respectively.

## 5. Current open work — ordered

### P0 — Generic Digital Copy UI **CURRENT STEP**

Implement the user-facing Digital Copy workspace and source-page viewer. The viewer must consume Phase 7 page/region evidence without bypassing the source hash or fail-closed state.

### P0 — Operational verification / revision / handoff

Complete `Rev_NNN` archive lifecycle and operational independent-verification archive.

### P1 — Generic end-to-end regression

Create controlled fixtures proving the entire PDF → Digital Copy lifecycle, including graphical evidence.

### P2 — Real normative corpus validation

Run DBN and a diverse normative corpus only after the generic product foundation is ready.

### P3 — Downstream domain integration

Connect accepted Digital Copies to normative registers, SPZ semantics and engineering calculation/execution layers.

## 6. Definition of generic Digital Copy completion

The generic product is complete only when a user can submit a normative PDF and, through the normal UI, obtain immutable identity, multi-parser evidence, canonical structure, discrepancy resolution, semantic/table/formula/change/dependency artifacts, graphical evidence, revision lock, independent verification, regression, reproducibility manifest and a final accepted/blocked state.

Phase 7 closes the graphical **engine evidence contract**, not this overall product definition.

## 7. Operational rule

After every implementation change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing;
4. only a successful current-head run is verification evidence;
5. never use an older green commit as evidence for the current head.
