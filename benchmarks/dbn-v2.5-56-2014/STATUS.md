# DBN Benchmark Status

## Verified

The registered DBN V.2.5-56:2014 + Changes 1 and 2 fixture was executed locally with the NDI benchmark runner.

- SHA-256 verified
- file size verified
- page count verified
- MarkItDown 0.1.7 executed

## Current phase

The MarkItDown baseline is recorded in `result.json`.

The benchmark is now moving from single-parser extraction metrics to multi-parser structural recognition and reconciliation.

## Important limitation

The recorded MarkItDown `numbered_items` value from the first run must be regenerated after the benchmark metric regex correction. No normative conclusions are based on that metric until the corrected run is recorded.
