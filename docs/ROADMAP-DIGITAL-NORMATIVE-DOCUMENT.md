# Roadmap — Digital Normative Document

**Repository:** `bigunandrey/normative-document-intelligence`
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`
**Roadmap revision:** 2026-09-14

## 1. Target state

The target is not merely a parser that extracts PDF text. The system must produce a **source-bound, independently verified, reproducible digital representation of a normative document** and must fail closed whenever evidence is missing, contradictory, or unresolved.

The target chain is:

```text
USER PDF
  ↓
Document identity / edition / amendments
  ↓
Primary-source integrity
  ↓
Multi-parser extraction
  ↓
Canonical structural observations
  ↓
External authoritative-source discovery
  ↓
External-source validation + retrieval
  ↓
Cross-source / cross-parser comparison
  ↓
Discrepancy detection and evidence package
  ↓
Reconciliation / resolution
  ↓
Graphical verification
  ↓
Canonical digital representation
  ↓
Revision + verification lock
  ↓
Regression
  ↓
DIGITAL_ACCEPTED
  ↓
Downstream normative semantics
```

## 2. Why the previous A–F sequence is being replaced

The previous roadmap treated external cross-checking as a late Gate F activity. That is too late and too weak.

External authoritative sources are not only a final verification layer. They are an **evidence source for structural recognition itself**. They may be needed when a parser:

- misses a paragraph, table, cell, formula, heading or amendment;
- produces conflicting text or numbers;
- loses page/reading-order information;
- misreads decimal separators, operators or symbols;
- cannot distinguish headers/footers from normative content;
- fails to identify an amendment or deletion.

Therefore external-source discovery and validation must be implemented **before structural acceptance is closed**, while the final external cross-check remains part of the acceptance chain.

## 3. New implementation phases

### Phase 0 — CI and baseline recovery — **COMPLETE ✅**

Completed and GitHub-verified. The regression fixes restored a green `main` baseline.

### Phase 1 — Document identity and source registry — **COMPLETE ✅**

Completed for the implemented contract scope. Identity, revision compatibility, source SHA-256 validation and source-candidate evidence are implemented and tested.

### Phase 2 — Complete parser-observation layer — **IN PROGRESS 🔄**

Implemented baseline includes the canonical parser-neutral model, adapters for MarkItDown/pypdf/Docling/OpenDataLoader, deterministic registered ingestion, provenance/geometry/span handling, structural aliases, observation manifests, adapter contract validation and regression coverage.

Remaining: complete structural recognition for all configured parser outputs; execute the registered DBN fixture through the real multi-parser path; complete full-DBN structural regression evidence. Fresh DBN execution is not claimed because the complete 22.4 MB fixture is not currently available to the CI execution environment.

### Phase 3 — External Source Discovery & Cross-Check Engine — **COMPLETE FOR CONTRACT SCOPE ✅**

Implemented provider-neutral discovery → validation → retrieval → independent parsing → aggregation → comparison → discrepancy-evidence chain, including fail-closed source integrity and parser disagreement handling. Real authoritative provider implementations and real DBN execution remain integration work.

### Phase 4 — Integrated reconciliation — **COMPLETE FOR CONTRACT SCOPE ✅**

Implemented integrated parser + external evidence, explicit blocking/resolution, immutable provenance-linked resolution decisions, fail-closed blocker disposition, source-bound canonical preservation and Gate C integration. Resolution never silently rewrites normative content.

### Phase 5 — Structural acceptance / DBN end-to-end gate — **IN PROGRESS ▶️**

Target: **DBN В.2.5-56:2014 зі Зміною №1 та №2**.

Implemented DBN evidence manifest, explicit fresh-vs-historical distinction, fail-closed DBN structural gate and regression coverage. Fresh 105-page execution, authoritative cross-check evidence and full-DBN regression remain blocked until the complete source bytes are CI-accessible.

### Phase 6 — Graphical verification — **IN PROGRESS 🔄**

Implemented fail-closed graphical evidence contract, source/page/verifier/timestamp validation, critical-category coverage and Gate C integration. Remaining: deterministic page/region evidence references and DBN-specific graphical fixtures once the complete PDF is CI-accessible.

### Phase 7 — Digital representation persistence and revision lock — **COMPLETE FOR CONTRACT SCOPE ✅**

Implemented and GitHub-verified:
- immutable deterministic revision IDs;
- source SHA-256 binding;
- canonical digital-revision hash;
- immutable revision-directory persistence;
- reproducibility manifest with protocol/parser/evidence hashes;
- fail-closed duplicate revision protection;
- verification of stored representation against source-bound document and revision hash;
- tamper detection for canonical representation and manifest source binding;
- deterministic evidence-hash ordering.

Latest verified CI run: `34886488863` (#168) — **SUCCESS**, `pytest -q` — **SUCCESS**.

### Phase 8 — Independent AI verification and final acceptance — **IN PROGRESS ▶️**

Goal: implement at least two genuinely independent AI verification records, make independence explicit and machine-checkable, bind each verification to the exact source/revision/evidence chain, and allow `DIGITAL_ACCEPTED` only when all mandatory evidence is present and independently verified.

Required implementation:
- independent verifier identity and verification scope;
- source hash and digital-revision binding;
- immutable verification records;
- explicit independence criteria and duplicate-verifier rejection;
- verification-result aggregation;
- fail-closed requirement for ≥2 independent successful AI verifications;
- final acceptance evidence binding to the locked revision;
- regression tests for missing, duplicate, mismatched and conflicting AI verification records.

### Phase 9 — Downstream normative semantics

Only after the document-intelligence chain is closed: atomic normative-unit decomposition, exact normative operators, table/formula rule registries, applicability/type links, dependency graphs and deterministic normative execution.

## 4. Priority order

**0. Green CI → 1. Source identity → 2. Parser observations → 3. External Source Engine → 4. Reconciliation → 5. DBN structural gate → 6. Graphical verification → 7. Persistence/revision lock → 8. Independent verification/final acceptance → 9. Downstream semantics.**

## 5. Definition of done

The generic NDI layer is complete only when:

1. A supplied normative PDF has immutable source identity.
2. Multiple independent extraction paths produce provenance-complete observations.
3. External authoritative sources can be discovered, validated and retrieved through a provider-neutral interface.
4. Parser and external-source discrepancies are retained and machine-readable.
5. Missing/unrecognized structures are detectable and cannot silently disappear.
6. Graphical verification provides evidence for visually critical structures.
7. A canonical representation is source-bound and revision-locked.
8. The entire chain is reproducible from preserved artifacts.
9. Two independent AI verification records are present where required.
10. Regression passes.
11. Only then can the document receive protocol-level `DIGITAL_ACCEPTED`.

## 6. Operational rule for future work

After every code change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing the roadmap;
4. only treat a commit as verified when GitHub reports a successful test run;
5. do not use an older green commit as evidence that the current head is green.

Historical benchmark results remain explicitly labeled as historical and are never substituted for fresh execution evidence.
