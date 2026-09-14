# Verification Gates A-F

**Protocol:** DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL v2.1
**Scope:** generic NDI verification infrastructure

This document defines the executable boundary of Gates A-F. A gate records evidence; it does not silently repair source content or promote AI inference to normative truth.

## Gate A — Structural observations

Input: one or more parser-specific canonical documents.

Required:
- source SHA-256;
- parser observations;
- requested parser coverage;
- explicit page/geometry/provenance where supplied by the parser.

Implementation: `ndi.gate_a_observations`, `ndi.from_pypdf_pages`, `ndi.from_docling_records`, `ndi.from_opendataloader_records`, `ndi.from_markitdown`.

Important: MarkItDown text-only output is not assigned a fabricated page anchor.

## Gate B — Reconciliation

`ndi.merge_parser_documents` conservatively joins parser observations. Matching uses existing deterministic matching; unmatched nodes remain explicit. `ndi.gate_b_reconciliation` produces `AGREED`, `CONFLICT`, and `MISSING_OBSERVATION` decisions through the existing reconciliation engine.

A conflict is never silently resolved.

## Gate C — Structural acceptance

`ndi.gate_c_structural_acceptance` combines the fail-closed recognition audit with reconciliation. Structural acceptance requires a clean recognition audit and no non-AGREED reconciliation decision.

This is still not normative acceptance.

## Gate D — Digital representation persistence

`ndi.persist_digital_representation` serializes the canonical representation as a deterministic JSON artifact. `ndi.digital_revision` hashes that representation, while the source SHA remains embedded in the artifact.

The digital revision is therefore content-derived and traceable to the source identity.

## Gate E — Revision / verification infrastructure

`RevisionRecord` captures the protocol-required verification metadata and `ndi.write_revision_record` creates an immutable, non-overwriting revision directory. Duplicate revision IDs fail closed.

The record supports reviewer identity, source checks, independent sources, discrepancies, resolution, handoff tasks and links to the digital revision.

## Gate F — Graphical and external verification

`GraphicalVerificationRecord` and `ExternalCrossCheckRecord` are explicit evidence contracts. `ndi.gate_f_verification` passes only when both layers contain a PASS result and recorded scope/evidence.

The framework intentionally does not claim that a graphical check happened merely because a PDF exists. A verifier must create the record after performing the check.

## Final acceptance

`ndi.final_acceptance` is the final fail-closed checklist. `DIGITAL_ACCEPTED` is impossible until all required evidence is explicitly present, including:

- source verification;
- structural verification;
- reconciliation;
- persisted digital representation;
- graphical verification;
- external cross-check;
- change/deletion verification;
- at least two independent AI verification records;
- regression;
- synchronized master registers;
- revision lock.

Therefore the presence of the gate implementation does **not** mean the DBN benchmark is already `DIGITAL_ACCEPTED`. The DBN PDF is not stored in this repository, so fresh execution against that fixture remains an execution task when the licensed fixture is supplied.
