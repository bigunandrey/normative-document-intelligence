# DBN V.2.5-56:2014 benchmark

## Fixture identity

The benchmark fixture is the DBN V.2.5-56:2014 PDF with Changes 1 and 2.

Expected source identity from the established baseline:

- SHA-256: `fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056`
- Size: `23,532,218` bytes
- Pages: `105`

The source PDF is not committed to this public repository. A benchmark run must verify the SHA-256 before accepting results.

## Execution

From the repository root:

```text
python tools/dbn_benchmark.py path/to/DBN.pdf -o benchmarks/dbn-v2.5-56-2014/result.json
```

The runner records source provenance and MarkItDown extraction metrics. Future parser adapters must add their own observation block without replacing existing parser evidence.

## Established baseline (old repository)

These values are retained as a migration reference, not as a new-repository run:

| Parser | Version | Time (s) | Characters | Lines | Headings | Table-like lines | Numbered items |
|---|---:|---:|---:|---:|---:|---:|---:|
| MarkItDown | 0.1.7 | 8.898 | 491,675 | 6,388 | 0 | 3,351 | 16 |
| Docling | 2.127.0 | 1438.329 | 328,429 | 3,637 | 262 | 659 | 98 |
| OpenDataLoader | 2.5.8 | 6.787 | 243,067 | 5,320 | 40 | 0 | 14 |

These numbers must not be presented as benchmark results produced by this repository until the fixture has been run here.
