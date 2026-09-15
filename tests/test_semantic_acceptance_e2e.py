from __future__ import annotations

from pathlib import Path

import pytest

from ndi.canonical import CanonicalDocument, CanonicalNode, NodeType
from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.normative_semantics import NormativeUnit
from ndi.revision_lock import RevisionLock
from ndi.semantic_acceptance import validate_semantic_fail_closed


def _job(tmp_path: Path):
    source = tmp_path / "fixture.pdf"
    source.write_bytes(b"%PDF-1.4\nNDI SEMANTIC E2E\n")
    return new_job("semantic-e2e", DigitalCopySource.from_file(source))


def _executors(semantic_block: bool):
    stages = {}
    for stage in OrchestrationStage:
        stages[stage] = lambda job, root, stage=stage: StageEvidence(
            StageEvidenceKind(stage.value), True, {f"{stage.value.lower()}.json": "{}\n"}
        )

    def identity(job, root):
        return StageEvidence(
            StageEvidenceKind.IDENTITY, True, {"identity.json": "{}\n"},
            bindings={"document_id": "doc-e2e", "revision_id": "rev-e2e"},
        )

    stages[OrchestrationStage.IDENTITY] = identity

    def semantic(job, root):
        document = CanonicalDocument("doc-e2e", "fixture.pdf", job.source.sha256, 1)
        node = CanonicalNode("node-e2e", NodeType.PARAGRAPH, text="A requirement")
        document.add_node(node)
        lock = RevisionLock(
            revision_id="rev-e2e",
            document_id="doc-e2e",
            source_sha256=job.source.sha256,
            digital_revision="semantic-e2e",
            protocol_version="2.1",
            parser_versions=(("fixture", "1.0"),),
        )
        unit = NormativeUnit(
            unit_id="unit-e2e",
            document_id="doc-e2e",
            source_sha256=job.source.sha256,
            digital_revision="semantic-e2e",
            node_id="node-e2e",
            anchor_page=None,
            operator="" if semantic_block else "shall",
            modality="UNRESOLVED" if semantic_block else "REQUIREMENT",
            subject="A",
            predicate="" if semantic_block else "be protected",
            source_text="A requirement",
        )
        ok, issues = validate_semantic_fail_closed(document, lock, units=(unit,))
        return StageEvidence(
            StageEvidenceKind.DIGITALIZATION,
            ok,
            {"semantic-validation.json": "\n".join(issues) + "\n"},
            blockers=tuple(issues),
        )

    stages[OrchestrationStage.DIGITALIZATION] = semantic
    return stages


def test_semantic_unresolved_state_blocks_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    with pytest.raises(RuntimeError, match="unresolved"):
        DigitalCopyOrchestrator(tmp_path / "package", _executors(True)).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_semantic_resolved_state_does_not_block_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    result = DigitalCopyOrchestrator(tmp_path / "package", _executors(False)).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED
