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

CI evidence:
- GitHub Actions run `34875875689` — **SUCCESS**;
- `pytest -q` — **SUCCESS**.

Integration work remains deferred to the ingestion/external-source phases.

### Phase 2 — Complete parser-observation layer — **IN PROGRESS 🔄**

**Goal:** convert every supported parser result into the same evidence model without treating parser output as truth.

Implemented baseline:
- canonical parser-neutral observation model;
- adapters for MarkItDown, pypdf, Docling and OpenDataLoader;
- stable `ParserAdapter` contract and deterministic registered parser set;
- `adapt_registered()` / `adapt_all()` fail-closed execution;
- adapter capability validation;
- page-aware pypdf extraction;
- provenance, geometry and character-span handling;
- structural aliases for tables/rows/cells, formulas, headers/footers, notes/footnotes and figures;
- local structural parent references separated from global input parent references;
- regression coverage for nested tables/lists, parent references, provenance aliases, geometry and parser attributes;
- deterministic source-bound observation manifests and SHA-256 addressing;
- deterministic `ingest_parser_outputs()` orchestration from complete parser-output sets;
- adapter-output contract validation for source binding, parser provenance, ordering, anchors, spans, confidence and parent references;
- CI regression coverage for complete parser coverage, source binding, determinism, fail-closed behavior and adapter contract violations.

**Milestone recorded:** deterministic multi-parser observation ingestion and adapter-contract hardening are implemented and covered by green GitHub Actions runs. The latest verified pre-external-comparison baseline is run `34881838208` (#113), **SUCCESS**, with `pytest -q` SUCCESS.

**Remaining Phase 2 work:**
1. complete structural recognition for all configured parser outputs;
2. execute the registered DBN fixture through the real multi-parser path;
3. add/verify structural regression coverage for the full DBN fixture.

**Important limitation:** fresh execution of the 105-page DBN fixture is not yet claimed. The full 22.4 MB fixture is available in Dropbox, but the current Dropbox retrieval path cannot fetch the complete binary; historical parser benchmark data therefore remains historical evidence only.

Exit criterion: the registered DBN fixture can produce parser observations from the configured parser set through one reproducible API/CLI path, with provenance-complete observations and structural regression coverage.

### Phase 3 — External Source Discovery & Cross-Check Engine — **IN PROGRESS 🔄**

Implement a provider-neutral engine with separate stages:

```text
Document identity
  → candidate discovery
  → candidate ranking
  → authority validation
  → edition/amendment validation
  → retrieval
  → independent parsing
  → comparison
  → discrepancy evidence
```

Implemented:
- `ExternalSourceProvider` provider contract;
- `SourceCandidate` / `ValidatedSource` source-validation contracts;
- `ExternalDocument` and `ExternalObservationSet` evidence contracts;
- `CrossCheckResult` and typed `DiscrepancyEvidence`;
- fail-closed authoritative same-revision discovery;
- deterministic comparison of supplied canonical observations against validated external canonical observations;
- conversion of comparison differences into provenance-bound discrepancy evidence;
- detection of missing observations, text differences, structural differences and anchor differences;
- rejection of external comparison against a non-same-revision source;
- fail-closed retrieval of external byte content with SHA-256 integrity verification;
- independent external parser contract for verified retrieved bytes;
- source-bound `ExternalParserObservation` artifacts with parser/version provenance;
- fail-closed rejection of empty/duplicate parser configurations, tampered retrieved bytes, invalid parser output, wrong source binding and mismatched parser provenance;
- public export of the independent external parsing API.

**Milestones recorded:** external-source discovery/validation, executable cross-document comparison, integrity-checked retrieval, and independent source parsing contracts are implemented and covered by regression tests. The independent parser provenance regression was corrected and the resulting commit is `768416966142d0ed9e0c5c023a2794cd86dfd175`.

**Next Phase 3 work:** connect independently parsed external observations into `ExternalObservationSet` and feed the resulting source-bound canonical representation directly into the comparison engine, with deterministic multi-parser aggregation and fail-closed disagreement handling.

Exit criterion: given a document identity, the engine can return validated source candidates and explicit reasons when no authoritative match is available, then retrieve a validated source and produce independently parsed comparison evidence.

### Phase 4 — Integrated reconciliation

Combine parser evidence and external-source evidence without silent correction. Every discrepancy must remain machine-readable and provenance-linked; unresolved discrepancies block structural acceptance.

### Phase 5 — Structural acceptance / DBN end-to-end gate

Run the complete chain against **DBN В.2.5-56:2014 зі Зміною №1 та №2**. Fresh execution must be separately recorded from historical benchmark evidence.

### Phase 6 — Graphical verification

Verify visually critical information: tables/merged cells, formulas, numerical values, symbols/operators, notes, numbering, headers/footers, amendments/deletions, page breaks/reading order and structurally relevant figures.

### Phase 7 — Digital representation persistence and revision lock

Implement immutable revision IDs, source-hash lock, digital-revision hash, verification archive, reproducibility manifest and explicit handoff artifact.

### Phase 8 — Independent AI verification and final acceptance

Implement the requirement for at least two independent AI verification records and make independence explicit in the evidence model. Only the complete evidence chain can produce `DIGITAL_ACCEPTED`.

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
