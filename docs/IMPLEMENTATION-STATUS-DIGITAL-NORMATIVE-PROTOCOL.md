# Implementation Status — DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1

**Repository:** `bigunandrey/normative-document-intelligence`  
**Checked:** 2026-09-14  
**Protocol source:** migrated from `bigunandrey/fire-protection-engine/docs/normative/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md`  
**Source protocol SHA:** `64338fb906bb5fc3f2d49130ed16b04b1893b3e0`  
**NDI baseline:** `main` at commit `b95ee8174fb59f1cec3183aac9bf19788bf042c7`

## 1. Status vocabulary used here

- **IMPLEMENTED** — requirement is represented by current NDI code/tests/artifacts.
- **PARTIAL** — a material subset is implemented, but the protocol requirement is not closed end-to-end.
- **NOT IMPLEMENTED** — the requirement is not currently implemented in NDI.
- **DOWNSTREAM BY DESIGN** — the protocol requires it, but NDI architecture explicitly assigns the responsibility to downstream domain-specific normative layers rather than to the generic document-intelligence core.
- **HISTORICAL EVIDENCE ONLY** — evidence exists in the migrated DBN benchmark, but NDI does not claim a fresh implementation/execution.

This distinction is important: a requirement being outside NDI's generic boundary is not treated as a defect in the parser-neutral core.

## 2. Executive result

### Closed in NDI

The following core requirements are already implemented:

1. Source identity / SHA-256 handling.
2. PDF extraction evidence via MarkItDown.
3. Parser-neutral canonical structural document model.
4. Stable document/node identifiers.
5. Source anchors, page/geometry fields and provenance model.
6. Parser observations with parser/version/confidence/attributes.
7. Cross-parser matching and discrepancy detection.
8. Reconciliation decisions (`AGREED`, `CONFLICT`, `MISSING_OBSERVATION`).
9. Fail-closed structural recognition quality gate (`PASS`, `PASS_WITH_WARNINGS`, `FAIL`).
10. Unit tests for canonical model, reconciliation and validator failure modes.
11. DBN fixture identity and historical multi-parser benchmark evidence.

### Still open in NDI

The main open implementation blocks are:

1. Full parser-adapter set beyond the existing MarkItDown extraction path.
2. End-to-end construction of canonical structural observations from all benchmark parser outputs.
3. Machine-readable final discrepancy report for the DBN fixture from the current NDI pipeline.
4. Full structural recognition of tables/cells, formulas, headers/footers and reading order from actual parser observations.
5. A complete ingestion pipeline that runs extraction → observation adaptation → canonicalization → reconciliation → quality gate as one production API/CLI workflow.
6. Provenance-complete digital representation persistence/serialization as a first-class artifact of the pipeline.
7. Regression/acceptance tests proving the complete DBN structural gate end-to-end.
8. NDI-native revision/verification artifact machinery and source-hash/revision locking.

### Explicitly downstream by design

The following protocol layers are not defects in NDI merely because they are absent here:

- semantic normative-rule interpretation;
- applicability/type links as engineering semantics;
- normative numeric/formula rule registries;
- dependency graphs for engineering rules;
- domain-specific master normative registers;
- downstream deterministic normative execution.

The NDI architecture explicitly says that it answers what structure and source evidence are present, while downstream domain projects answer what that content means for engineering/compliance decisions.

## 3. Requirement-by-requirement cross-check

| Protocol | Requirement | NDI status | Evidence / gap |
|---|---|---|---|
| §1 | Convert normative source into machine-readable, traceable representation | PARTIAL | Structural representation exists; full semantic digital-copy chain is not closed. |
| §2 | `source_anchor → source_text → semantic/table/formula → operator → dependencies → verification/change` | PARTIAL | Source/structural side exists; semantic/operator/dependency/change layers are downstream/open. |
| §3.1 | Source of truth + metadata + SHA-256 | IMPLEMENTED | Canonical document requires source SHA-256; stable document identity derives from it. |
| §3.2 | Extraction is evidence, not normative truth | IMPLEMENTED | README and architecture explicitly enforce this boundary. |
| §3.3 | No silent correction; discrepancies retained | IMPLEMENTED | Reconciliation and discrepancy layers retain conflicts instead of silently resolving them. |
| §3.4 | Preserve normative operators exactly | DOWNSTREAM BY DESIGN | Operator semantics belong to normative semantic decomposition; NDI preserves raw/source text but does not yet implement normative operator extraction. |
| §3.5 | Fail-closed on missing evidence | IMPLEMENTED | Recognition validator is explicitly fail-closed. |
| §3.6 | AI inference cannot become normative truth | IMPLEMENTED | NDI architecture explicitly separates recognition from normative acceptance. |
| §4 | Two master normative-register files | DOWNSTREAM BY DESIGN | SPZ Ukraine register is domain/project-level, not generic NDI core. |
| §5 | Isolated `reference-data/<DOCUMENT_ID>` package | PARTIAL | DBN benchmark package exists under `benchmarks/`; generic per-document `reference-data` production structure is not yet implemented. |
| §6 | AI-Revisions archive | NOT IMPLEMENTED | No NDI-native revision archive/workflow exists yet. |
| §7 | Mandatory pre-work protocol reading/state inspection | NOT IMPLEMENTED | Protocol is now present in NDI, but no runtime enforcement exists. |
| §8 | Source identification metadata + current edition/amendments | PARTIAL | Source hash and fixture identity exist; generic validity/edition/amendment register workflow is absent. |
| §9 | Capture immutable primary source | PARTIAL | Source identity/hash is supported; NDI does not itself manage a generic source archive. |
| §10 | Full extraction + extraction log | PARTIAL | MarkItDown extraction exists and CLI reports parser/hash/output; persistent extraction-log artifact is not yet a complete NDI contract. |
| §11 | One-to-one decomposition into atomic normative units | PARTIAL | Canonical structural nodes exist, including paragraphs/lists/tables/formulas; full normative atomic decomposition is not closed. |
| §12 | Semantic normalization fields | DOWNSTREAM BY DESIGN | Normative semantics are explicitly outside generic NDI scope. |
| §13 | Table decomposition with notes/footnotes/special markers | PARTIAL | Canonical table/row/cell node types exist; actual parser-to-table reconstruction and verification are not closed. |
| §14 | Formula extraction + graphical/machine-normalized verification | PARTIAL | `FORMULA` node type exists; actual formula parser adapters and graphical verification are not closed. |
| §15 | Changes/deletions represented and traceable | NOT IMPLEMENTED | No generic change/deletion registry or revision-lock implementation exists in NDI. |
| §16 | Open-source cross-check and discrepancy resolution | PARTIAL | Parser discrepancy machinery exists; external normative-source cross-check workflow does not. |
| §17 | Graphical verification | NOT IMPLEMENTED | No NDI graphical/PDF visual verification gate is currently implemented. Historical DBN artifacts exist only in the former repository. |
| §18 | Dependency mapping | DOWNSTREAM BY DESIGN / NOT IMPLEMENTED IN NDI | Generic source/dependency metadata can be carried, but normative dependency mapping is not implemented. |
| §19 | ≥2 independent AI verification records for `DIGITAL_ACCEPTED` | NOT IMPLEMENTED | No independent-AI verification workflow exists in NDI. |
| §20 | Update master MD/XLSX after verification | DOWNSTREAM BY DESIGN | Domain register synchronization is outside generic NDI. |
| §21 | Explicit handoff protocol | NOT IMPLEMENTED | No NDI handoff artifact/schema/runtime. |
| §22 | Regression of related rules/tables/formulas/downstream logic | PARTIAL | Unit tests and benchmark metric tests exist; full digital-copy regression gate does not. |
| §23 | Source hash / digital revision lock | PARTIAL | Source SHA-256 is implemented; digital-revision invalidation/lock semantics are not. |
| §24 | Final `DIGITAL_ACCEPTED` acceptance chain | NOT IMPLEMENTED | Structural recognition gate exists, but the full normative acceptance chain does not. |
| §25 | Full digitalization status vocabulary | PARTIAL | NDI has `PASS/PASS_WITH_WARNINGS/FAIL`; the protocol's digitalization status lifecycle is not implemented. |
| §26 | Full reproducibility through preserved artifacts | PARTIAL | Parser evidence/provenance and benchmark provenance exist; complete verification/revision artifact lineage does not. |
| §27 | AI must execute to factual result and leave explicit handoff if blocked | NOT IMPLEMENTED | No runtime operating-policy enforcement. |

## 4. Current NDI architecture versus protocol boundary

NDI currently implements the generic part of the protocol up to this boundary:

```text
PRIMARY SOURCE
    ↓
SOURCE IDENTITY / SHA-256
    ↓
PARSER EXTRACTION
    ↓
PARSER OBSERVATIONS
    ↓
CANONICAL STRUCTURAL MODEL
    ↓
RECONCILIATION
    ↓
STRUCTURAL QUALITY GATE
    ↓
[DOWNSTREAM NORMATIVE DIGITALIZATION]
```

The repository's own architecture defines the same boundary: NDI determines what structure and source evidence are present; downstream projects determine what the content means for engineering/compliance decisions.

## 5. DBN V.2.5-56:2014 benchmark status

The DBN fixture is registered with SHA-256:

`fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056`

The migrated historical baseline records MarkItDown 0.1.7, Docling 2.127.0 and OpenDataLoader 2.5.8 measurements. Those measurements are explicitly marked historical evidence reused from the completed Fire Protection Engine benchmark; they are not claimed as fresh NDI executions.

Therefore:

- **fixture identity:** IMPLEMENTED;
- **historical parser benchmark evidence:** HISTORICAL EVIDENCE ONLY;
- **fresh NDI multi-parser structural execution:** OPEN;
- **fresh NDI discrepancy report:** OPEN;
- **fresh NDI full structural acceptance:** OPEN.

## 6. Priority closure sequence

The protocol-driven implementation order should be:

### Gate A — Structural observation completion

Implement/adapt parser outputs for the registered DBN fixture into `ParserObservation` records, including page boundaries, reading order, headings/sections, paragraphs/numbered items, tables/cells, formulas, headers/footers and provenance.

### Gate B — Reconciliation report

Run the current canonical matching/reconciliation machinery against the real multi-parser observations and produce a machine-readable discrepancy report.

### Gate C — Structural acceptance

Run the fail-closed recognition audit over the resulting canonical document and make the DBN benchmark pass/fail reproducible in CI.

### Gate D — Digital representation persistence

Persist the verified structural representation and provenance as a stable artifact with source hash and digital revision identity.

### Gate E — Verification/revision infrastructure

Add revision records, verification artifacts, source/revision locking and reproducibility metadata required by §§6, 19, 21, 23 and 26.

### Gate F — Graphical verification

Add a controlled graphical verification layer for tables, formulas, critical numbers/operators, footnotes, numbering, amendments and deletions.

### Gate G — Normative semantic downstream layer

Only after the generic recognition chain is closed should downstream normative semantic decomposition, table/formula rule registries, applicability, dependencies and deterministic execution consume the verified evidence.

## 7. Important non-equivalence

A `PASS` from the current NDI `audit_document()` is **not** equivalent to protocol status `DIGITAL_ACCEPTED`.

Current `PASS` means that the canonical structural representation passes NDI's structural/provenance integrity gate. Protocol `DIGITAL_ACCEPTED` additionally requires semantic/table/formula completion, change/deletion handling, graphical verification or explicit unavailability, cross-check, two independent AI verification records, synchronized master registers, regression and preserved revision artifacts.

Confusing these two statuses would violate the protocol.
