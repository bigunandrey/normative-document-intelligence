# Roadmap — Digital Normative Document

**Repository:** `bigunandrey/normative-document-intelligence`
**Protocol:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`
**Roadmap revision:** 2026-09-14

## 1. Target state

The target is not merely a parser that extracts PDF text. The system must produce a **source-bound, independently verified, reproducible digital representation of a normative document** and must fail closed whenever evidence is missing, contradictory, or unresolved.

The target chain is:

```text
USER PDF → identity/revision → integrity → multi-parser observations → external evidence → comparison → reconciliation → graphical verification → canonical representation → revision lock → independent AI verification → regression → DIGITAL_ACCEPTED → downstream normative semantics
```

## 2. Implementation phases

### Phase 0 — CI and baseline recovery — **COMPLETE ✅**

### Phase 1 — Document identity and source registry — **COMPLETE ✅**

### Phase 2 — Complete parser-observation layer — **IN PROGRESS 🔄**

Remaining: complete structural recognition for all configured parser outputs; execute the registered DBN fixture through the real multi-parser path; complete full-DBN structural regression evidence. Fresh DBN execution is not claimed because the complete 22.4 MB fixture is not currently available to the CI execution environment.

### Phase 3 — External Source Discovery & Cross-Check Engine — **COMPLETE FOR CONTRACT SCOPE ✅**

### Phase 4 — Integrated reconciliation — **COMPLETE FOR CONTRACT SCOPE ✅**

### Phase 5 — Structural acceptance / DBN end-to-end gate — **IN PROGRESS ▶️**

Target: **DBN В.2.5-56:2014 зі Зміною №1 та №2**. Fresh 105-page execution, authoritative cross-check evidence and full-DBN regression remain blocked until the complete source bytes are CI-accessible.

### Phase 6 — Graphical verification — **IN PROGRESS 🔄**

Remaining: deterministic page/region evidence references and DBN-specific graphical fixtures once the complete PDF is CI-accessible.

### Phase 7 — Digital representation persistence and revision lock — **COMPLETE FOR CONTRACT SCOPE ✅**

Generic immutable revision lock and reproducibility contract implemented and GitHub-verified.

### Phase 8 — Independent AI verification and final acceptance — **COMPLETE FOR CONTRACT SCOPE ✅**

Generic source/document/revision-bound independent-AI verification contract and final acceptance gate implemented and GitHub-verified. Real-world independent DBN reviews remain evidence-generation work.

### Phase 9 — Downstream normative semantics — **IN PROGRESS ▶️**

Goal: transform the accepted canonical document into deterministic, source-bound normative semantics without altering the locked digital representation.

**Completed and CI-verified:**
- atomic normative-unit decomposition;
- exact normative operators for requirements, prohibitions, recommendations and permissions;
- conditions and exceptions;
- applicability/type links;
- strengthened applicability/type-link validation and explicit target resolution;
- table/formula rule registry primitives;
- strengthened table/formula registry validation and source-expression integrity checks;
- explicit dependency/cross-reference graph;
- deterministic source-bound semantic evaluation model;
- fail-closed handling of unresolved applicability/conditions during evaluation;
- amendment/deletion semantics, with explicit source-bound ADD/REPLACE/DELETE actions and fail-closed ambiguity handling;
- regression coverage for the implemented semantic chain.

**Remaining:**
- dependency/cross-reference target resolution against the document graph;
- complete provenance validation for every semantic artifact back to canonical nodes/source anchors;
- fail-closed handling of unresolved amendment, dependency and semantic interpretation;
- comprehensive regression fixtures for amendments/deletions, resolved dependencies, tables/formulas, and full semantic provenance.

## 3. Priority order

**0. Green CI → 1. Source identity → 2. Parser observations → 3. External Source Engine → 4. Reconciliation → 5. DBN structural gate → 6. Graphical verification → 7. Persistence/revision lock → 8. Independent verification/final acceptance → 9. Downstream semantics.**

## 4. Definition of done

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

## 5. Operational rule for future work

After every code change:

1. commit to GitHub;
2. inspect the new `main` GitHub Actions run;
3. if failed, fix before advancing the roadmap;
4. only treat a commit as verified when GitHub reports a successful test run;
5. do not use an older green commit as evidence that the current head is green.

Historical benchmark results remain explicitly labeled as historical and are never substituted for fresh execution evidence.
