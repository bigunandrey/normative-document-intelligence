# NDI Product UI Contract

**Repository:** `bigunandrey/normative-document-intelligence`  
**Protocol basis:** `DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1`  
**Contract revision:** 2026-09-15  
**Status:** CLOSED — normative product/UI contract

## 1. Purpose

This document closes the generic Product UI Contract for the NDI Digital Copy product. It defines what the user-facing product must expose, how the UI is bound to the Digital Copy engine, and which actions are presentation/navigation actions versus engine decisions.

The UI is not a second rules engine. It is a controlled presentation and interaction layer over source-bound engine artifacts.

## 2. Product principle

The central object is the **Digital Copy Workspace** for one immutable source revision.

The workspace maintains three synchronized representations:

```text
SOURCE PDF
    ↕
CANONICAL STRUCTURE
    ↕
DIGITAL COPY
```

Evidence, discrepancies, verification records and acceptance state are attached to these representations but are never silently substituted for source content.

The original PDF is immutable. The UI may highlight, annotate and navigate evidence, but it must never rewrite the source document.

## 3. Required views

The product exposes the following views for every document workspace:

1. **Digital Copies** — document list, lifecycle state, revision, activity, blockers.
2. **Create Digital Copy** — source intake and immutable source creation.
3. **Overview** — identity, source integrity, revision and lifecycle state.
4. **Extraction** — parser observations, parser/version metadata and extraction evidence.
5. **Structure** — hierarchical document structure and source anchors.
6. **Discrepancies** — parser/external/semantic/verification discrepancies and their evidence.
7. **Digital Copy** — canonical normalized representation and source bindings.
8. **Graphical Verification** — source-page viewer, overlays, evidence and selected element.
9. **Verification** — independent verification records, scope, result and independence basis.
10. **Acceptance** — gate-by-gate acceptance state and blockers.
11. **Revision History** — immutable revisions, archive records and evidence hashes.
12. **Export / Handoff** — reproducible package, manifest and downstream handoff.

Views may be implemented as routes, tabs or panels, but their information responsibilities are mandatory.

## 4. Workspace model

The workspace is organized around a selected document element.

```text
┌──────────────────────────────────────────────────────────────┐
│ NDI — Digital Copy Workspace                  STATUS          │
├──────────────┬──────────────────────────────┬───────────────┤
│ STRUCTURE    │ SOURCE PDF                   │ DIGITAL COPY  │
│              │                              │               │
│ §1           │ page N                       │ selected node │
│ §1.1         │ [highlighted region]         │ source text   │
│ Table 1      │                              │ normalized    │
│ Formula 3    │                              │ semantics     │
├──────────────┴──────────────────────────────┴───────────────┤
│ Evidence / provenance / discrepancy / verification details  │
└──────────────────────────────────────────────────────────────┘
```

A selected element is represented by a stable canonical `node_id`. The UI resolves that node to its source anchors and evidence.

## 5. Navigation contract

Navigation is bidirectional.

### 5.1 Digital Copy → PDF

```text
select digital element
→ node_id
→ source anchor
→ page + region
→ open page
→ zoom to region
→ highlight region
→ show evidence
```

### 5.2 Structure → PDF

```text
select structural node
→ source anchor
→ page + region
→ viewer navigation + highlight
```

### 5.3 PDF → Digital Copy

The source viewer can select a page region. Where a spatial index exists, the UI resolves the region to the canonical node(s) whose source bounding boxes contain/intersect the selection and selects the corresponding Digital Copy element.

If the mapping is ambiguous, the UI must show all candidates and must not choose a normative interpretation automatically.

## 6. Graphical verification viewer

The graphical viewer renders the **original immutable PDF** and places evidence overlays above the rendered page.

It does not redraw the normative document.

Each overlay is derived from source-bound evidence containing at minimum:

```text
source_hash
node_id
element_kind
page
x0, y0, x1, y1
source_text
observed_text
match
verifier
verified_at
```

The viewer must support:

- page navigation;
- zoom in/out;
- fit-to-page and fit-to-width;
- overlay visibility;
- selected-element highlighting;
- navigation from selected node to its page/region;
- navigation from a selected visual region back to the mapped node when unambiguous;
- evidence detail display;
- visual discrepancy indication.

### 6.1 Coordinate model

Source evidence coordinates are expressed in source-page coordinates. The viewer maps them into the current viewport using page scale and viewport offset:

```text
viewport_x = page_offset_x + source_x × scale_x
viewport_y = page_offset_y + source_y × scale_y
```

The mapping must be recalculated on page resize, zoom, rotation or viewport changes so that an overlay remains attached to the same source region.

### 6.2 Critical visual elements

The UI must make critical evidence distinguishable for:

- tables and complex/merged cells;
- formulas and special symbols;
- numbers;
- units;
- comparison operators;
- notes and footnotes;
- numbering;
- amendments;
- deletions.

Where cell-level or token-level geometry is available, the UI should prefer the most specific source region rather than only the enclosing table/formula region.

## 7. Evidence panel

For the selected element the UI presents, without rewriting:

```text
ELEMENT
source / canonical identifier

SOURCE TEXT
exact source-bound text

OBSERVED TEXT
parser/external observation

PROVENANCE
source hash / parser / source / anchor

VERIFICATION
verifier / timestamp / result

DISCREPANCY
type / status / evidence
```

The UI must preserve the distinction between source text, observation and normalized representation.

## 8. Extraction view

The extraction view exposes parser observations as evidence.

For each observation the user can inspect:

- parser name/version;
- observation artifact;
- confidence where available;
- source/page binding;
- agreement/conflict/missing-observation status.

The UI must never label an un-reconciled parser result as authoritative normative text.

## 9. Structure view

The structure explorer displays the canonical hierarchy and allows selection of:

- pages;
- sections/headings;
- paragraphs;
- lists/items;
- tables/cells;
- formulas;
- headers/footers;
- notes/footnotes;
- other source-bound nodes.

Every selectable node should expose its stable ID and source anchor where available.

## 10. Discrepancy view

Every discrepancy is a first-class object in the UI.

Minimum fields:

```text
id
type
status
severity
affected node(s)
source(s)
source evidence
observed values/text
resolution
blocker state
```

The UI may display a proposed resolution, but only the engine may establish an accepted resolution.

Unresolved critical discrepancies remain visible and actionable.

## 11. Digital Copy view

The Digital Copy view exposes the normalized source-bound representation.

For a normative unit it must be possible to inspect, where present:

```text
source anchor
source text
operator / modality
predicate
conditions
exceptions
applicability/type links
numeric values / units
formula links
dependencies
change/deletion action
verification state
```

`UNRESOLVED` and `AMBIGUOUS` states are displayed explicitly and are never rendered as accepted normative meaning.

## 12. Verification view

The verification view separates:

- not run;
- passed;
- failed;
- blocked.

Each record exposes scope, result, independence basis, reviewer identity and evidence binding.

The UI cannot edit a failed verification into a passed verification.

## 13. Acceptance view

Acceptance is a derived engine state.

The UI displays the acceptance chain, including at minimum:

```text
identity
source integrity
extraction
reconciliation
canonical/digitalization
semantic integrity
external evidence
graphical verification
independent verification
regression
revision lock
reproducibility
archive/handoff readiness
```

`DIGITAL_ACCEPTED` cannot be selected manually. A user action may request/re-run a stage, resolve an explicitly supported workflow item, or start a new revision, but acceptance is determined by the engine.

## 14. Revision History and Export

Revision History is immutable and shows:

- revision ID;
- source SHA-256;
- digital revision;
- archive ID;
- verification evidence hashes;
- creation time;
- acceptance/block state.

Export/Handoff exposes the exact accepted revision and its reproducibility manifest. Export cannot silently substitute a newer, older or unverified source.

## 15. API / engine boundary

The UI is a thin client over typed engine artifacts and workflow operations.

The UI may:

- create intake jobs;
- request workflow execution;
- request supported verification/archive operations;
- read persisted artifacts;
- navigate between source-bound representations;
- display blockers and evidence.

The UI must not:

- calculate normative results independently;
- invent missing values;
- silently correct source text;
- resolve an ambiguity by presentation logic;
- mutate immutable source files;
- manually assign `DIGITAL_ACCEPTED`.

## 16. Fail-closed UI behavior

If an artifact cannot be loaded, is hash-inconsistent, lacks required provenance, has an unresolved critical discrepancy, or has an invalid state transition, the UI shows an explicit blocked/error state.

It must never fall back to silently displaying stale or inferred content as accepted content.

## 17. Security and integrity

Every source-view operation is bound to the package-local immutable source revision. The UI displays the source SHA-256 and current digital revision where available.

User annotations/highlights are metadata only. They do not modify the source PDF or its hash.

Paths are resolved inside the job/package root and traversal outside the workspace is rejected.

## 18. Test contract

The UI contract is considered implementation-complete only when tests cover at least:

1. create/upload and immutable source binding;
2. lifecycle and blocker display;
3. all required view responsibilities;
4. node-to-source navigation;
5. source-region-to-node navigation where unambiguous;
6. overlay coordinate transformation across zoom/resize;
7. critical-element graphical evidence;
8. discrepancy visibility and fail-closed behavior;
9. verification state distinction;
10. acceptance cannot be manually forced;
11. revision/history integrity;
12. export/handoff exact-revision binding;
13. restart persistence;
14. stale/tampered artifact handling.

## 19. Contract closure versus implementation maturity

This contract is closed at the specification level. Closing the contract does not falsely claim that every visual interaction is already implemented in the current shell.

The current UI implementation must be measured against this contract. Any missing interaction is a concrete implementation item, not a change to the product definition.

## 20. Completion criterion

The Product UI implementation is production-ready when a user can take one real normative PDF through the complete workflow in the UI and, for every accepted element, move reliably between:

```text
Digital Copy
    ↕
Canonical Node
    ↕
Source PDF region
    ↕
Evidence / Verification
```

without losing source identity, provenance, revision binding or fail-closed semantics.
