# Migration Notes

The generic document-ingestion core is being separated from Fire Protection Engine.

Initial source components identified for migration from `bigunandrey/fire-protection-engine` branch `feature/document-ingestion`:

- `canonical.py` — canonical structural document model;
- `adapters.py` — parser-neutral evidence adapters;
- `matching.py` — conservative cross-parser reconciliation;
- supporting hashing, manifest, observations and pipeline components to be migrated after the canonical contract is stabilized.

Fire-protection-specific normative models are intentionally excluded from this repository.

The first migration preserves the parser-neutral architecture and removes the `Fire Protection System` namespace from the public generic package.
