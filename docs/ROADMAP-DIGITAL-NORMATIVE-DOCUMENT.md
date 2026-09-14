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

**Goal:** never advance the architecture on a red repository.

Completed:
1. Diagnosed the failing GitHub Actions regression on `main`.
2. Restored the repository to a green baseline.
3. Corrected repository-local `tools` importability and pytest path configuration.
4. Corrected the unmatched-parser regression fixture so it tests a genuinely unmatched node rather than an anchor-matched text conflict.
5. Confirmed GitHub Actions run `34875625916` for commit `755833052ff21d15018562800b6e6a39e36f0744` completed successfully, including `pytest -q`.

Exit criterion: **satisfied** — `main` has a confirmed successful GitHub Actions test run after the regression fixes.

---

### Phase 1 — Document identity and source registry — **COMPLETE ✅**

**Goal:** establish exactly what document the user supplied before interpreting its contents.

Completed:
- immutable `DocumentIdentity` contract;
- designation/title;
- edition/year;
- amendments and revisions;
- publication/status metadata;
- issuing/authoritative organization;
- source URL/type;
- source SHA-256 validation;
- source acquisition timestamp;
- `SourceRecord` and `SourceRegistry`;
- `SourceCandidate` authority/revision evidence fields;
- explicit compatibility states: `SAME_REVISION`, `DIFFERENT_REVISION`, `UNVERIFIED`;
- fail-closed rejection of an unverified source candidate;
- unit-test coverage for identity, SHA-256 validation, duplicate source IDs and revision compatibility;
- production-facing exports from `ndi`.

CI evidence:
- GitHub Actions run `34875875689` — **SUCCESS**;
- `pytest -q` step — **SUCCESS**.

Exit criterion: **satisfied for the implemented Phase 1 scope** — the engine can distinguish same-document/same-revision, different-revision and unverified candidates at the source-registry contract level, with the decision preserved as evidence.

Remaining integration work is explicitly deferred to the ingestion/external-source phases rather than silently treated as complete:
- deterministic extraction of identity metadata from supplied-document observations;
- persistent source-registry artifact;
- authoritative-source registry configuration;
- ingestion-pipeline integration;
- DBN end-to-end identity execution.

---

### Phase 2 — Complete parser-observation layer — **IN PROGRESS 🔄**

**Goal:** convert every supported parser result into the same evidence model without treating parser output as truth.

Implement and test adapters for:
- MarkItDown;
- pypdf;
- Docling;
- OpenDataLoader;
- future parsers through a stable adapter contract.

Observation coverage:
- pages;
- reading order;
- headings/sections;
- paragraphs and numbered items;
- lists;
- tables/rows/cells;
- formulas;
- headers/footers;
- footnotes/notes;
- figures/graphics;
- bounding boxes and character spans;
- parser/version/confidence/provenance.

Current baseline:
- parser-neutral canonical model exists;
- adapters exist for MarkItDown, pypdf, Docling and OpenDataLoader;
- page-aware pypdf extraction exists;
- parser observations and provenance structures exist;
- cross-parser matching/reconciliation exists;
- structural quality validation and verification gates exist;
- stable `ParserAdapter` contract exists;
- deterministic registered parser set exists for MarkItDown, pypdf, Docling and OpenDataLoader;
- `adapt_registered()` provides a common execution contract;
- `adapt_all()` provides a single deterministic multi-parser execution path and fails closed when a configured parser output is missing or unknown;
- adapter capability manifest is validated before execution;
- regression tests cover parser registration, identity, provenance and page-boundary preservation;
- parent references are now explicitly separated into local structural references and global input references, preventing ordinal-offset corruption across multiple top-level records;
- regression coverage includes multiple structural records plus explicit global parent references;
- deterministic source-bound observation manifests are JSON-safe, canonicalized and SHA-256 addressable;
- `ingest_parser_outputs()` now provides one deterministic API path from a complete configured parser-output set to source-bound observation artifacts;
- ingestion regression coverage verifies complete parser coverage, source binding, determinism and fail-closed behavior.

Remaining Phase 2 work:
- audit and harden each adapter against the full canonical observation contract;
- complete structural recognition for tables/rows/cells, formulas, headers/footers, footnotes and figures;
- preserve reading order and geometry consistently across adapters;
- execute the registered DBN fixture through the multi-parser path;
- add structural regression tests for the configured parser set.

CI evidence:
- GitHub Actions run `34880086115` (#98) for commit `7b384719b46353e5501fa754fbd0e86921e03274` — **SUCCESS**;
- `pytest -q` step — **SUCCESS**.

The roadmap remains in Phase 2 until the DBN fixture can be executed through the complete registered parser path with provenance-complete observations.

Exit criterion: the registered DBN fixture can produce parser observations from the configured parser set through one reproducible API/CLI path.

---

### Phase 3 — External Source Discovery & Cross-Check Engine

**This is the newly elevated priority.**

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

Core contracts:
- `ExternalSourceProvider`;
- `SourceCandidate`;
- `ValidatedSource`;
- `ExternalDocument`;
- `ExternalObservationSet`;
- `CrossCheckResult`;
- `DiscrepancyEvidence`.

The engine must support configured authoritative registries/web sources without coupling the NDI core to one website or search provider.

Important distinction:
- **discovery** finds candidates;
- **validation** establishes authority and revision identity;
- **retrieval** obtains the source;
- **comparison** identifies differences;
- **resolution** records what evidence resolved the discrepancy.

No external source may be promoted to PASS merely because its title looks similar.

Exit criterion: given a document identity, the engine can return validated source candidates and explicit reasons when no authoritative match is available.

---

### Phase 4 — Integrated reconciliation

**Goal:** combine parser evidence and external-source evidence without silent correction.

Implement:
- multi-parser reconciliation;
- external-source reconciliation;
- unmatched-node detection;
- missing-observation detection;
- table/formula discrepancy comparison;
- source-text discrepancy comparison;
- amendment/deletion discrepancy comparison;
- machine-readable discrepancy report;
- evidence links from every discrepancy to source/parser/page/geometry.

Resolution states must distinguish at least:
- `AGREED`;
- `CONFLICT`;
- `MISSING_OBSERVATION`;
- `EXTERNAL_SOURCE_UNAVAILABLE`;
- `EXTERNAL_SOURCE_UNVERIFIED`;
- `RESOLVED_BY_SOURCE`;
- `RESOLVED_BY_GRAPHICAL_VERIFICATION`;
- `UNRESOLVED`.

Exit criterion: no discrepancy can disappear during reconciliation; every unresolved discrepancy blocks structural acceptance.

---

### Phase 5 — Structural acceptance / DBN end-to-end gate

Run the complete chain against **DBN В.2.5-56:2014 зі Зміною №1 та №2**.

Required outputs:
- canonical document;
- parser observation package;
- external-source evidence package;
- reconciliation report;
- structural acceptance report;
- complete discrepancy inventory;
- source/provenance manifest.

The historical benchmark remains historical evidence only. Fresh NDI execution must be recorded separately.

Exit criterion: fresh DBN execution is reproducible and its structural status is explicitly `PASS`, `PASS_WITH_WARNINGS`, or `FAIL` with machine-readable reasons.

---

### Phase 6 — Graphical verification

**Goal:** verify visual fidelity for information that text extraction cannot prove reliably.

Priority checks:
- tables and merged cells;
- formulas and mathematical symbols;
- decimal separators and operators;
- critical numerical values;
- footnotes/notes;
- numbering;
- headers/footers;
- amendment/deletion marks;
- page breaks and reading order;
- diagrams/figures where structurally relevant.

Graphical verification is evidence-producing, not a generic human approval checkbox.

Exit criterion: every graphical check has page/region provenance, verifier identity, result and discrepancy linkage.

---

### Phase 7 — Digital representation persistence and revision lock

Implement the first-class artifact chain:

```text
source hash
+ canonical representation
+ evidence manifest
+ verification records
+ discrepancy/resolution records
+ digital revision hash
+ previous revision
```

Implement:
- immutable revision IDs;
- source-hash lock;
- digital-revision hash;
- verification archive;
- reproducibility manifest;
- explicit handoff artifact.

Exit criterion: changing the source or canonical representation necessarily produces a new revision and invalidates prior acceptance evidence.

---

### Phase 8 — Independent AI verification and final acceptance

Implement the protocol's requirement for at least two independent AI verification records.

Independence must be explicit in the artifact model; two records generated by the same unchecked path must not automatically count as independent verification.

Final acceptance requires all applicable evidence:
- source verified;
- structural recognition verified;
- reconciliation verified;
- digital representation persisted;
- graphical verification completed or explicitly unavailable with protocol-compliant handling;
- external cross-check completed or explicitly unavailable with protocol-compliant handling;
- changes/deletions verified;
- ≥2 independent AI verifications;
- regression passed;
- required downstream register synchronization completed;
- revision locked.

Exit criterion: only the complete evidence chain can produce `DIGITAL_ACCEPTED`.

---

### Phase 9 — Downstream normative semantics

Only after the document-intelligence chain is closed:
- atomic normative-unit semantic decomposition;
- exact normative operators;
- table/formula rule registries;
- applicability/type links;
- dependency graphs;
- master normative registers;
- deterministic normative execution.

These remain downstream of generic NDI by design.

## 4. Priority order

The new order is:

**0. Green CI → 1. Source identity → 2. Parser observations → 3. External Source Engine → 4. Reconciliation → 5. DBN structural gate → 6. Graphical verification → 7. Persistence/revision lock → 8. Independent verification/final acceptance → 9. Downstream semantics.**

This replaces the previous linear assumption that Gate F should be implemented only after A–E. External-source infrastructure is now a shared capability used by Phases 1–6 and represented in the final acceptance chain.

## 5. Definition of done

The project is not considered complete merely because unit tests pass.

The generic NDI layer is complete when:

1. A supplied normative PDF has an immutable source identity.
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
