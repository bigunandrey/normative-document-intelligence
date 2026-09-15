from __future__ import annotations

import json
from pathlib import Path

import pytest

from ndi.ai_verification import AIVerificationRecord, build_evidence_hash
from ndi.canonical import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, ParserObservation, SourceAnchor
from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_package import replay_package, verify_package
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.graphical_evidence import GraphicalEvidenceItem, PageRegion, build_graphical_evidence, validate_graphical_evidence_bundle
from ndi.operational_archive import verify_revision_archive
from ndi.reconciliation import reconcile_document
from ndi.revision_lock import RevisionLock


def _job(tmp_path: Path, name: str = "fixture.pdf"):
    source = tmp_path / name
    source.write_bytes(b"%PDF-1.4\nNDI GENERIC E2E FIXTURE\n")
    return new_job("e2e-job", DigitalCopySource.from_file(source))


def _executors():
    def identity(job, root):
        return StageEvidence(
            StageEvidenceKind.IDENTITY,
            True,
            {"identity.json": "{}\n"},
            bindings={"document_id": "doc-e2e", "revision_id": "rev-e2e"},
        )

    return {
        OrchestrationStage.IDENTITY: identity,
        **{
            stage: (
                lambda job, root, stage=stage: StageEvidence(
                    StageEvidenceKind(stage.value),
                    True,
                    {f"{stage.value.lower()}.json": "{}\n"},
                )
            )
            for stage in OrchestrationStage
            if stage != OrchestrationStage.IDENTITY
        },
    }


def _verification(lock: RevisionLock, verifier_id: str, basis: str) -> AIVerificationRecord:
    fields = dict(
        verifier_id=verifier_id,
        model_id="e2e-model",
        document_id=lock.document_id,
        source_sha256=lock.source_sha256,
        digital_revision=lock.digital_revision,
        scope=("all",),
        checks=("identity", "structure", "reconciliation", "graphical"),
        result="PASS",
        verified_at="2026-09-15T10:00:00+03:00",
        independence_basis=basis,
    )
    seed = AIVerificationRecord(evidence_hash="0" * 64, **fields)
    return AIVerificationRecord(evidence_hash=build_evidence_hash(seed), **fields)


def _locked_revision(tmp_path: Path, result):
    lock = RevisionLock(
        revision_id=result.revision_id,
        document_id=result.document_id,
        source_sha256=result.source.sha256,
        digital_revision="digital-e2e",
        protocol_version="2.1",
        parser_versions=(("e2e", "1.0"),),
    )
    lock_dir = tmp_path / "locks" / lock.revision_id
    lock_dir.mkdir(parents=True)
    (lock_dir / "digital-representation.json").write_text("{}\n", encoding="utf-8")
    (lock_dir / "reproducibility-manifest.json").write_text(lock.manifest_json(), encoding="utf-8")
    return lock


def _canonical_with_observations(*texts: str) -> CanonicalDocument:
    document = CanonicalDocument("doc-e2e", "fixture.pdf", "a" * 64, 1)
    node = CanonicalNode("node-e2e", NodeType.PARAGRAPH)
    for index, text in enumerate(texts):
        node.add_observation(
            ParserObservation(
                parser=f"parser-{index + 1}",
                parser_version="1.0",
                observation_id=f"obs-{index + 1}",
                node_type=NodeType.PARAGRAPH,
                text=text,
                anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10)),
            )
        )
    document.add_node(node)
    return document


def _graphical_executor(match: bool):
    def executor(job, root):
        item = GraphicalEvidenceItem(
            evidence_id="gfx-e2e-1",
            source_hash=job.source.sha256,
            node_id="node-e2e",
            element_kind="table",
            region=PageRegion(page=1, x0=1, y0=1, x1=10, y1=10),
            source_text="Table 1",
            observed_text="Table 1" if match else "Table X",
            match=match,
            verifier="e2e-visual-verifier",
            verified_at="2026-09-15T10:00:00+03:00",
        )
        bundle = build_graphical_evidence(
            "doc-e2e",
            job.source.sha256,
            (item,),
            result="PASS" if match else "FAIL",
            verifier="e2e-visual-verifier",
            verified_at="2026-09-15T10:00:00+03:00",
            discrepancies=() if match else ("Table text mismatch",),
        )
        gate = validate_graphical_evidence_bundle(bundle)
        if gate.status.value != "PASS":
            return StageEvidence(
                StageEvidenceKind.GRAPHICAL_VERIFICATION,
                False,
                {"graphical-evidence.json": bundle.to_json()},
                blockers=tuple(gate.issues),
            )
        return StageEvidence(
            StageEvidenceKind.GRAPHICAL_VERIFICATION,
            True,
            {"graphical-evidence.json": bundle.to_json()},
        )

    return executor


def test_generic_e2e_accept_archive_and_replay(tmp_path: Path):
    job = _job(tmp_path)
    package = tmp_path / "package"
    orchestrator = DigitalCopyOrchestrator(package, _executors())
    result = orchestrator.run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED

    lock = _locked_revision(tmp_path, result)
    records = (
        _verification(lock, "verifier-a", "independent-model"),
        _verification(lock, "verifier-b", "independent-run"),
    )

    archive = orchestrator.archive_revision(
        result,
        lock,
        records,
        lock_root=tmp_path / "locks",
        archive_root=tmp_path / "archive",
        created_at="2026-09-15T10:01:00+03:00",
    )
    assert archive.archive_id == "Rev_001"
    valid, issues = verify_revision_archive(tmp_path / "archive", "Rev_001")
    assert valid, issues

    replayed_job, replay_issues = replay_package(package)
    assert replay_issues == []
    assert replayed_job is not None
    assert replayed_job.status == DigitalCopyStatus.DIGITAL_ACCEPTED
    assert replayed_job.metadata["operational_archive"]["verified"] is True


def test_generic_e2e_blocks_missing_stage(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    del executors[OrchestrationStage.GRAPHICAL_VERIFICATION]
    with pytest.raises(RuntimeError, match="Missing executor"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED
    assert "GRAPHICAL_VERIFICATION" in job.blockers[-1]


def test_generic_e2e_blocks_failed_reconciliation(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    executors[OrchestrationStage.RECONCILIATION] = lambda job, root: StageEvidence(
        StageEvidenceKind.RECONCILIATION, False, blockers=("fixture discrepancy unresolved",)
    )
    with pytest.raises(RuntimeError, match="fixture discrepancy unresolved"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED
    assert DigitalCopyStatus.DIGITAL_ACCEPTED != job.status


def test_generic_e2e_reconciliation_conflict_through_engine(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()

    def reconciliation(job, root):
        report = reconcile_document(_canonical_with_observations("first", "second"))
        conflicts = report.conflicts
        return StageEvidence(
            StageEvidenceKind.RECONCILIATION,
            not conflicts,
            {"reconciliation.json": json.dumps([d.__dict__ for d in report.decisions], indent=2, sort_keys=True) + "\n"},
            blockers=("Unresolved parser conflict",) if conflicts else (),
        )

    executors[OrchestrationStage.RECONCILIATION] = reconciliation
    with pytest.raises(RuntimeError, match="Unresolved parser conflict"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_generic_e2e_missing_observation_through_engine(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()

    def reconciliation(job, root):
        report = reconcile_document(_canonical_with_observations())
        missing = [d for d in report.decisions if d.status == "MISSING_OBSERVATION"]
        return StageEvidence(
            StageEvidenceKind.RECONCILIATION,
            not missing,
            {"reconciliation.json": json.dumps([d.__dict__ for d in report.decisions], indent=2, sort_keys=True) + "\n"},
            blockers=("Missing parser observation",) if missing else (),
        )

    executors[OrchestrationStage.RECONCILIATION] = reconciliation
    with pytest.raises(RuntimeError, match="Missing parser observation"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_generic_e2e_graphical_verification_success_through_orchestration(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    executors[OrchestrationStage.GRAPHICAL_VERIFICATION] = _graphical_executor(True)
    result = DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED
    assert (tmp_path / "package" / "artifacts" / "graphical-evidence.json").is_file()


def test_generic_e2e_graphical_verification_mismatch_blocks(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    executors[OrchestrationStage.GRAPHICAL_VERIFICATION] = _graphical_executor(False)
    with pytest.raises(RuntimeError, match="does not match|not PASS|unresolved discrepancies"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_generic_e2e_archive_verification_blocks_digital_revision_mismatch(tmp_path: Path):
    job = _job(tmp_path)
    orchestrator = DigitalCopyOrchestrator(tmp_path / "package", _executors())
    result = orchestrator.run(job)
    lock = _locked_revision(tmp_path, result)
    record = _verification(lock, "verifier-a", "independent-model")
    orchestrator.archive_revision(
        result,
        lock,
        (record,),
        lock_root=tmp_path / "locks",
        archive_root=tmp_path / "archive",
        created_at="2026-09-15T10:01:00+03:00",
        result="BLOCKED",
    )
    verification_path = next((tmp_path / "archive" / "Rev_001" / "verification").glob("*.json"))
    data = json.loads(verification_path.read_text(encoding="utf-8"))
    data["digital_revision"] = "wrong-revision"
    verification_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    valid, issues = verify_revision_archive(tmp_path / "archive", "Rev_001")
    assert not valid
    assert any("revision binding mismatch" in issue for issue in issues)


@pytest.mark.parametrize("stage", tuple(OrchestrationStage))
def test_generic_e2e_every_stage_failure_is_fail_closed(tmp_path: Path, stage: OrchestrationStage):
    job = _job(tmp_path, f"failure-{stage.value.lower()}.pdf")
    executors = _executors()
    executors[stage] = lambda job, root, stage=stage: StageEvidence(
        StageEvidenceKind(stage.value),
        False,
        blockers=(f"fixture failure at {stage.value}",),
    )
    with pytest.raises(RuntimeError, match=f"fixture failure at {stage.value}"):
        DigitalCopyOrchestrator(tmp_path / f"package-{stage.value.lower()}", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED
    assert DigitalCopyStatus.DIGITAL_ACCEPTED != job.status


def test_generic_e2e_failed_evidence_without_blocker_is_rejected(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    executors[OrchestrationStage.EXTRACTION] = lambda job, root: StageEvidence(
        StageEvidenceKind.EXTRACTION, False
    )
    with pytest.raises(ValueError, match="must contain blockers"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_generic_e2e_unknown_stage_binding_is_rejected(tmp_path: Path):
    job = _job(tmp_path)
    executors = _executors()
    executors[OrchestrationStage.IDENTITY] = lambda job, root: StageEvidence(
        StageEvidenceKind.IDENTITY,
        True,
        {"identity.json": "{}\n"},
        bindings={"unsupported": "value"},
    )
    with pytest.raises(ValueError, match="Unsupported Digital Copy job bindings"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED


def test_generic_e2e_package_artifact_tamper_blocks_replay(tmp_path: Path):
    job = _job(tmp_path)
    package = tmp_path / "package"
    result = DigitalCopyOrchestrator(package, _executors()).run(job)
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED

    artifact = package / "artifacts" / "stage-evidence.json"
    artifact.write_text("tampered\n", encoding="utf-8")
    valid, issues = verify_package(result, package)
    assert not valid
    assert any("artifact hash mismatch" in issue for issue in issues)
    replayed_job, replay_issues = replay_package(package)
    assert replayed_job is None
    assert any("artifact hash mismatch" in issue for issue in replay_issues)


def test_generic_e2e_packaged_source_tamper_blocks_replay(tmp_path: Path):
    job = _job(tmp_path)
    package = tmp_path / "package"
    result = DigitalCopyOrchestrator(package, _executors()).run(job)
    packaged_source = package / "source" / result.source.filename
    packaged_source.write_bytes(packaged_source.read_bytes() + b"tampered")

    valid, issues = verify_package(result, package)
    assert not valid
    assert any("Packaged intake source SHA-256" in issue for issue in issues)
    replayed_job, replay_issues = replay_package(package)
    assert replayed_job is None
    assert any("Packaged intake source SHA-256" in issue for issue in replay_issues)


def test_generic_e2e_archive_requires_two_independent_verifiers(tmp_path: Path):
    job = _job(tmp_path)
    orchestrator = DigitalCopyOrchestrator(tmp_path / "package", _executors())
    result = orchestrator.run(job)
    lock = _locked_revision(tmp_path, result)
    record = _verification(lock, "verifier-a", "independent-model")

    with pytest.raises(ValueError, match="At least two independent AI verification records"):
        orchestrator.archive_revision(
            result,
            lock,
            (record,),
            lock_root=tmp_path / "locks",
            archive_root=tmp_path / "archive",
            created_at="2026-09-15T10:01:00+03:00",
        )
