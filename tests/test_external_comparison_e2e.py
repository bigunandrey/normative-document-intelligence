from __future__ import annotations

import json
from pathlib import Path

import pytest

from ndi.canonical import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor
from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.external_comparison import compare_against_external
from ndi.external_sources import ValidatedSource
from ndi.source_registry import Compatibility, DocumentIdentity, SourceCandidate, SourceType

SHA = "a" * 64
IDENTITY = DocumentIdentity("NDI-TEST-001", edition_year=2026)


def _job(tmp_path: Path):
    source = tmp_path / "fixture.pdf"
    source.write_bytes(b"%PDF-1.4\nNDI EXTERNAL E2E\n")
    return new_job("external-e2e", DigitalCopySource.from_file(source))


def _doc(text: str) -> CanonicalDocument:
    return CanonicalDocument(
        "doc-e2e", "fixture.pdf", SHA, 1,
        nodes=[CanonicalNode("n1", NodeType.PARAGRAPH, text=text, order=0, anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10)))],
        parser_versions={"fixture": "1.0"},
    )


def _source() -> ValidatedSource:
    candidate = SourceCandidate(
        "official-e2e", "Official E2E Source", SourceType.OFFICIAL_WEB, IDENTITY,
        authority_verified=True, revision_verified=True,
        evidence=("authority", "revision"),
    )
    return ValidatedSource(candidate, Compatibility.SAME_REVISION, ("authority_verified", "revision_verified"))


def _executors(external_text: str):
    stages = {}

    def identity(job, root):
        return StageEvidence(StageEvidenceKind.IDENTITY, True, {"identity.json": "{}\n"}, bindings={"document_id": "doc-e2e", "revision_id": "rev-e2e"})

    stages[OrchestrationStage.IDENTITY] = identity
    for stage in OrchestrationStage:
        if stage == OrchestrationStage.IDENTITY:
            continue
        stages[stage] = lambda job, root, stage=stage: StageEvidence(
            StageEvidenceKind(stage.value), True, {f"{stage.value.lower()}.json": "{}\n"}
        )

    def external(job, root):
        result = compare_against_external(_doc("supplied"), _doc(external_text), _source())
        payload = {
            "source_id": result.source.candidate.source_id,
            "discrepancies": [
                {"kind": item.kind.value, "description": item.description, "source_ids": item.source_ids}
                for item in result.discrepancies
            ],
        }
        return StageEvidence(
            StageEvidenceKind.RECONCILIATION,
            result.passed,
            {"external-comparison.json": json.dumps(payload, indent=2, sort_keys=True) + "\n"},
            blockers=("Unresolved external-source discrepancy",) if not result.passed else (),
        )

    stages[OrchestrationStage.RECONCILIATION] = external
    return stages


def test_external_discrepancy_blocks_real_orchestration_boundary(tmp_path: Path):
    job = _job(tmp_path)
    with pytest.raises(RuntimeError, match="Unresolved external-source discrepancy"):
        DigitalCopyOrchestrator(tmp_path / "package", _executors("external" )).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_external_same_revision_agreement_allows_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    result = DigitalCopyOrchestrator(tmp_path / "package", _executors("supplied")).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED
    assert (tmp_path / "package" / "artifacts" / "external-comparison.json").is_file()
