# Benchmark tools

The benchmark layer will execute multiple document parsers against the same source and compare their outputs through the NDI canonical contract.

The initial implementation intentionally keeps heavyweight parser dependencies optional. This allows the core package and CI tests to stay lightweight while real-document parser benchmarks run in dedicated workflows.
