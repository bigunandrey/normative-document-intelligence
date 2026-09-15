from __future__ import annotations

from pathlib import Path

import pytest

from ndi.amendment_semantics import AmendmentAction
from ndi.canonical import CanonicalDocument, CanonicalNode, NodeType
from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.graphical_evidence import (
    GraphicalEvidenceItem,
    PageRegion,
    build_graphical_evidence,
    validate_graphical_evidence_bundle,
)
from ndi.revision_lock import RevisionLock
from ndi.semantic_acceptance import validate_semantic_fail_closed


CRITICAL_ELEMENTS = ("table", "formula", "note", "footnote", "numbering")


def _job(tmp_path: Path):
    source = tmp_path / "fixture.pdf"
    source.write_bytes(b"%PDF-1.4\nNDI STRUCTURAL SEMANTICS E2E\n")
    return new_job("structural-e2e", DigitalCopySource.from_file(source))


def _executors(graphical_items: tuple[GraphicalEvidenceItem, ...], amendments=()):
    stages = {
        stage: lambda job, root, stage=stage: StageEvidence(
            StageEvidenceKind(stage.value), True, {f"{stage.value.lower()}.json": "{}\n"}
        )
        for stage in OrchestrationStage
    }
    stages[OrchestrationStage.IDENTITY] = lambda job, root: StageEvidence(
        StageEvidenceKind.IDENTITY,
        True,
        {"identity.json": "{}\n"},
        bindings={"document_id": "doc-e2e", "revision_id": "rev-e2e"},
    )

    def graphical(job, root):
        bundle = build_graphical_evidence(
            "doc-e2e",
            job.source.sha256,
            graphical_items,
            result="PASS",
            verifier="structural-e2e-verifier",
            verified_at="2026-09-15T10:00:00+03:00",
        )
        gate = validate_graphical_evidence_bundle(bundle)
        return StageEvidence(
            StageEvidenceKind.GRAPHICAL_VERIFICATION,
            gate.status.value == "PASS",
            {"graphical-evidence.json": bundle.to_json()},
            blockers=tuple(gate.issues),
        )

    stages[OrchestrationStage.GRAPHICAL_VERIFICATION] = graphical

    def digitalization(job, root):
        document = CanonicalDocument("doc-e2e", "fixture.pdf", job.source.sha256, 1)
        target = CanonicalNode("clause-1", NodeType.PARAGRAPH, text="Original clause")
        target.attributes["number"] = "1"
        amendment_node = CanonicalNode("amendment-1", NodeType.PARAGRAPH, text="Replace clause 1")
        amendment_node.attributes["replaces"] = "1"
        amendment_node.attributes["replacement_text"] = "Updated clause"
        document.add_node(target)
        document.add_node(amendment_node)
        lock = RevisionLock(
            revision_id="rev-e2e",
            document_id="doc-e2e",
            source_sha256=job.source.sha256,
            digital_revision="semantic-e2e",
            protocol_version="2.1",
            parser_versions=(("fixture", "1.0"),),
        )
        actions = tuple(amendments) if amendments else ()
        ok, issues = validate_semantic_fail_closed(document, lock, amendments=actions)
        return StageEvidence(
            StageEvidenceKind.DIGITALIZATION,
            ok,
            {"semantic-validation.json": "\n".join(issues) + "\n"},
            blockers=tuple(issues),
        )

    stages[OrchestrationStage.DIGITALIZATION] = digitalization
    return stages


def _graphical_items(source_hash: str):
    return tuple(
        GraphicalEvidenceItem(
            evidence_id=f"gfx-{kind}",
            source_hash=source_hash,
            node_id=f"node-{kind}",
            element_kind=kind,
            region=PageRegion(page=1, x0=1, y0=1, x1=20, y1=20),
            source_text=f"{kind} source",
            observed_text=f"{kind} source",
            match=True,
            verifier="structural-e2e-verifier",
            verified_at="2026-09-15T10:00:00+03:00",
        )
        for kind in CRITICAL_ELEMENTS
    )


def test_critical_graphical_elements_pass_through_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    items = _graphical_items(job.source.sha256)
    result = DigitalCopyOrchestrator(tmp_path / "package", _executors(items)).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED


def test_critical_graphical_mismatch_blocks_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    items = list(_graphical_items(job.source.sha256))
    items[-1] = GraphicalEvidenceItem(
        evidence_id=items[-1].evidence_id,
        source_hash=items[-1].source_hash,
        node_id=items[-1].node_id,
        element_kind=items[-1].element_kind,
        region=items[-1].region,
        source_text=items[-1].source_text,
        observed_text="wrong numbering",
        match=False,
        verifier=items[-1].verifier,
        verified_at=items[-1].verified_at,
    )
    with pytest.raises(RuntimeError):
        DigitalCopyOrchestrator(tmp_path / "package", _executors(tuple(items))).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_amendment_replace_is_resolved_through_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    action = AmendmentAction(
        action_id="amend-e2e",
        document_id="doc-e2e",
        source_sha256=job.source.sha256,
        digital_revision="semantic-e2e",
        source_node_id="amendment-1",
        anchor_page=None,
        action="REPLACE",
        target="1",
        replacement_text="Updated clause",
        source_text="Replace clause 1",
    )
    result = DigitalCopyOrchestrator(
        tmp_path / "package", _executors(_graphical_items(job.source.sha256), (action,))
    ).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED


def test_unresolved_amendment_target_blocks_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    action = AmendmentAction(
        action_id="amend-e2e-unresolved",
        document_id="doc-e2e",
        source_sha256=job.source.sha256,
        digital_revision="semantic-e2e",
        source_node_id="amendment-1",
        anchor_page=None,
        action="DELETE",
        target="999",
        replacement_text="",
        source_text="Delete clause 999",
    )
    with pytest.raises(RuntimeError, match="Amendment target is unresolved"):
        DigitalCopyOrchestrator(
            tmp_path / "package", _executors(_graphical_items(job.source.sha256), (action,))
        ).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED
