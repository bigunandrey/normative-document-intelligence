from pathlib import Path

import pytest

from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.digital_copy_package import replay_package


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
