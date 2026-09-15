from pathlib import Path

import pytest

from ndi.ai_verification import AIVerificationRecord, build_evidence_hash
from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.digital_copy_package import replay_package
from ndi.revision_lock import RevisionLock
from ndi.operational_archive import verify_revision_archive


def make_job(tmp_path: Path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"controlled source")
    return new_job("job-orchestrator", DigitalCopySource.from_file(source))


def passing_executors():
    def identity(job, root):
        return StageEvidence(
            StageEvidenceKind.IDENTITY,
            True,
            {"identity.json": "{}\n"},
            bindings={"document_id": "doc-orchestrator", "revision_id": "rev-orchestrator"},
        )

    return {
        OrchestrationStage.IDENTITY: identity,
        **{
            stage: (lambda job, root, stage=stage: StageEvidence(
                StageEvidenceKind(stage.value), True, {f"{stage.value.lower()}.json": "{}\n"}
            ))
            for stage in OrchestrationStage
            if stage != OrchestrationStage.IDENTITY
        },
    }


def test_orchestrator_persists_every_stage_and_accepts(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    package = tmp_path / "package"

    result = DigitalCopyOrchestrator(package, passing_executors()).run(job)

    assert result.accepted
    assert result.status == DigitalCopyStatus.DIGITAL_ACCEPTED
    assert (package / "job.json").is_file()
    assert (package / "package-manifest.json").is_file()
    assert (package / "source" / "source.pdf").is_file()
    assert (package / "artifacts" / "stage-evidence.json").is_file()
    assert (package / "artifacts" / "extraction-log.json").is_file()
    assert (package / "artifacts" / "handoff.json").is_file()
    assert all((package / "artifacts" / f"{stage.value.lower()}.json").is_file() for stage in OrchestrationStage)

    replayed, issues = replay_package(package)
    assert issues == []
    assert replayed is not None
    assert replayed.accepted
    assert replayed.document_id == "doc-orchestrator"
    assert replayed.revision_id == "rev-orchestrator"


def _verification(lock: RevisionLock, verifier_id: str, basis: str) -> AIVerificationRecord:
    payload = dict(
        verifier_id=verifier_id,
        model_id="test-model",
        document_id=lock.document_id,
        source_sha256=lock.source_sha256,
        digital_revision=lock.digital_revision,
        scope=("all",),
        checks=("identity", "structure"),
        result="PASS",
        verified_at="2026-09-15T10:00:00+03:00",
        independence_basis=basis,
    )
    seed = AIVerificationRecord(evidence_hash="0" * 64, **payload)
    return AIVerificationRecord(evidence_hash=build_evidence_hash(seed), **payload)


def test_orchestrator_archives_accepted_revision_and_binds_job(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    package = tmp_path / "package"
    orchestrator = DigitalCopyOrchestrator(package, passing_executors())
    result = orchestrator.run(job)

    lock_root = tmp_path / "locks"
    archive_root = tmp_path / "archive"
    lock = RevisionLock(
        revision_id=result.revision_id,
        document_id=result.document_id,
        source_sha256=result.source.sha256,
        digital_revision="digital-test",
        protocol_version="2.1",
        parser_versions=(("test", "1.0"),),
    )
    lock_dir = lock_root / lock.revision_id
    lock_dir.mkdir(parents=True)
    (lock_dir / "digital-representation.json").write_text("{}\n", encoding="utf-8")
    (lock_dir / "reproducibility-manifest.json").write_text(lock.manifest_json(), encoding="utf-8")
    records = (_verification(lock, "verifier-a", "separate-model"), _verification(lock, "verifier-b", "independent-run"))

    archive = orchestrator.archive_revision(
        result,
        lock,
        records,
        lock_root=lock_root,
        archive_root=archive_root,
        created_at="2026-09-15T10:01:00+03:00",
    )

    assert archive.archive_id == "Rev_001"
    assert result.metadata["operational_archive"]["archive_id"] == "Rev_001"
    assert result.artifacts["operational_archive"].endswith("artifacts/operational-archive.json")
    assert result.metadata["operational_archive"]["verified"] is True
    valid, issues = verify_revision_archive(archive_root, "Rev_001")
    assert valid, issues
    assert "operational_archive" in result.as_dict()["metadata"]


def test_orchestrator_archive_requires_accepted_job(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    lock = RevisionLock(
        revision_id="rev-orchestrator",
        document_id="doc-orchestrator",
        source_sha256=job.source.sha256,
        digital_revision="digital-test",
        protocol_version="2.1",
        parser_versions=(),
    )
    with pytest.raises(RuntimeError, match="DIGITAL_ACCEPTED"):
        DigitalCopyOrchestrator(tmp_path / "package", {}).archive_revision(
            job,
            lock,
            (),
            lock_root=tmp_path / "locks",
            archive_root=tmp_path / "archive",
            created_at="2026-09-15T10:00:00+03:00",
        )


def test_orchestrator_blocks_when_executor_is_missing(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    executors = passing_executors()
    del executors[OrchestrationStage.GRAPHICAL_VERIFICATION]

    with pytest.raises(RuntimeError, match="Missing executor"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert job.status == DigitalCopyStatus.BLOCKED
    assert any("GRAPHICAL_VERIFICATION" in reason for reason in job.blockers)


def test_orchestrator_blocks_failed_stage_and_does_not_continue(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    calls: list[OrchestrationStage] = []

    def failing(job, root):
        calls.append(OrchestrationStage.RECONCILIATION)
        return StageEvidence(
            StageEvidenceKind.RECONCILIATION,
            False,
            blockers=("Unresolved reconciliation discrepancy.",),
        )

    executors = passing_executors()
    executors[OrchestrationStage.RECONCILIATION] = failing
    executors[OrchestrationStage.DIGITALIZATION] = lambda job, root: (_ for _ in ()).throw(AssertionError("must not run"))

    with pytest.raises(RuntimeError, match="Unresolved reconciliation discrepancy"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert calls == [OrchestrationStage.RECONCILIATION]
    assert job.status == DigitalCopyStatus.BLOCKED
    assert "Unresolved reconciliation discrepancy." in job.blockers


def test_orchestrator_rejects_wrong_stage_evidence_kind(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    executors = passing_executors()
    executors[OrchestrationStage.EXTRACTION] = lambda job, root: StageEvidence(
        StageEvidenceKind.IDENTITY, True
    )

    with pytest.raises(ValueError, match="expected EXTRACTION"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert job.status == DigitalCopyStatus.BLOCKED
    assert any("expected EXTRACTION" in reason for reason in job.blockers)


def test_orchestrator_rejects_unsupported_binding(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    executors = passing_executors()
    executors[OrchestrationStage.IDENTITY] = lambda job, root: StageEvidence(
        StageEvidenceKind.IDENTITY,
        True,
        bindings={"status": "DIGITAL_ACCEPTED"},
    )

    with pytest.raises(ValueError, match="Unsupported Digital Copy job bindings"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert job.status == DigitalCopyStatus.BLOCKED


def test_orchestrator_rejects_failed_evidence_without_blocker(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    executors = passing_executors()
    executors[OrchestrationStage.RECONCILIATION] = lambda job, root: StageEvidence(
        StageEvidenceKind.RECONCILIATION, False
    )

    with pytest.raises(ValueError, match="blockers"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert job.status == DigitalCopyStatus.BLOCKED
