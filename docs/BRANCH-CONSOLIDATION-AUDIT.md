# Branch Consolidation Audit

**Repository:** `bigunandrey/normative-document-intelligence`
**Date:** 2026-09-14
**Target branch:** `main`

## Result

The repository should have a single permanent development branch: `main`.
The other branches are historical task branches, superseded branches, or duplicate refs. They do not represent separate product lines.

Before deletion, all material unique content from the non-main branches was checked against `main`.

## Branch-by-branch disposition

| Branch | Finding | Disposition |
|---|---|---|
| `main` | Current integrated line. Contains canonical model, adapters, validator, reconciliation, benchmark artifacts, protocol and implementation audit. | KEEP |
| `feature/ndi-core` | Two commits beyond an old common base, limited to early `__init__.py` / canonical API evolution. Current `main` contains later integrated versions. | DELETE |
| `feat/ingestion-core` | One unique commit at its branch tip changing `pyproject.toml` for MarkItDown/pypdf and `ndi-ingest`. Current `main` contains the later integrated version. | DELETE |
| `feat/migrate-dbn-artifacts` | Historical migration branch. Its unique baseline artifacts were superseded by the current `MIGRATED-BASELINE.json` plus migration notes/status/benchmark documentation on `main`. Full source provenance from its baseline was restored to `main`. | DELETE |
| `feat/dbn-migration-final` | No file changes relative to `main`; it is an ancestor/superseded line ending at commit `b9cb640`. | DELETE |
| `fix/dbn-benchmark-metrics` | Same effective branch tip as `feat/dbn-migration-final`; no changes relative to `main`. | DELETE |
| `bench/dbn-v2.5-56-2014-markitdown` | Historical benchmark branch. Its unique `result.json` was superseded by the current benchmark result/status structure on `main`. | DELETE |
| `Fix` | Diverged from `main`: 11 commits ahead and 32 behind. Most implementation files are older versions of code already superseded by `main`. One unique useful artifact, `tests/test_adapters.py`, was not present on `main` and has been consolidated into `main`. | DELETE after consolidation |

## `Fix` consolidation

The branch `Fix` contained a useful adapter regression test file covering:

- explicit parent relationship preservation;
- source/provenance handling;
- parser coverage accounting;
- prevention of fabricated page anchors in MarkItDown-derived observations.

The exact test file was copied into `main` without semantic modification.

The remaining `Fix` implementation files are older branch versions of functionality for which `main` contains later integrated versions. Replacing current `main` files with those older versions would regress the repository.

## Historical benchmark consolidation

The earlier `feat/migrate-dbn-artifacts` branch contained richer provenance in `BASELINE-MIGRATED.json`, including:

- original repository;
- original branch;
- fixture path;
- fixture blob SHA-1;
- source SHA-256;
- source size;
- page count;
- original ingestion and parser benchmark run IDs;
- MarkItDown, Docling and OpenDataLoader measurements.

The current `main` baseline retained the measurements but had omitted part of that provenance. The full provenance has now been restored into `benchmarks/dbn-v2.5-56-2014/MIGRATED-BASELINE.json`.

The old `BASELINE-MIGRATED.md` is not required as a separate artifact because its factual content is represented by the authoritative JSON baseline, `README.md`, `STATUS.md`, and `MULTI-PARSER-BENCHMARK.md`.

## Branching policy after consolidation

Use `main` as the only permanent branch.

Short-lived branches may be created for substantial isolated changes using:

- `feat/<short-description>`
- `fix/<short-description>`
- `bench/<short-description>` only when a benchmark genuinely needs isolation.

Such branches should be merged back into `main` and deleted after integration. Benchmark evidence belongs in repository artifacts, not in a permanent branch.

## Final state

After the user deletes the obsolete branches, the intended branch topology is:

```text
main  ← single permanent branch
```

No implementation work should continue on the obsolete branches.
