# Phase 9 Closure Record — Generic Digital Copy UI

**Date:** 2026-09-15  
**Repository:** `bigunandrey/normative-document-intelligence`  
**Status:** PARTIAL — GENERIC UI SHELL COMPLETE / OPERATIONAL PRODUCT INTEGRATION OPEN

## Result

Phase 9 now has a dependency-free user-facing Digital Copy workspace that consumes the existing generic job/package contracts without introducing a second state model.

## Implemented

- Digital Copy project/dashboard view;
- PDF upload intake with a package-local immutable source copy;
- source SHA-256 exposed in the user-facing job view;
- persisted job/status/stage/revision information;
- lifecycle state display including blocked and `DIGITAL_ACCEPTED` states;
- machine-readable `/api/jobs` and `/api/jobs/<job_id>` endpoints;
- browser PDF source-page viewer bound to the package-local source;
- graphical-verification evidence display with page/region, source text, observed text and match result;
- blocker display so unresolved content is not presented as accepted truth;
- optional injected workflow runner boundary;
- explicit refusal to execute when no runner is configured;
- launchable `ndi-ui` console entry point;
- regression tests for dashboard, creation, immutable source persistence, PDF-only intake, source serving and runner behavior.

## Security / integrity boundary

The UI does not alter the source hash, revision lock, evidence records or acceptance rules. It only presents persisted state and delegates workflow execution to the existing orchestration boundary.

The source viewer serves only the package-local source for the selected job and rejects path traversal outside that package.

## Verification

The implementation is covered by the repository regression suite and GitHub Actions. The exact current-head run must be green before this phase record is treated as verified.

## Explicit boundary

This phase does **not** close the full product UI. The current generic UI does not yet provide concrete document executors, a production authentication/authorization layer, rich PDF region overlays, operational revision/verification archive management, or the complete generic E2E workflow.

Those gaps remain intentionally separated from the generic engine contracts.

## Next step

**P0 — Operational verification / revision / handoff**, followed by **Phase 10 — Generic end-to-end regression**. After those are closed, the generic product can proceed to real normative-corpus validation.
