from pathlib import Path

import pytest

from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage, StageResult
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job


def make_job(tmp_path: Path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"controlled source")
    return new_job("job-orchestrator", DigitalCopySource.from_file(source))


def passing_executors():
    def identity(job, root):
        # Identity establishes the bindings required by the final acceptance gate.
        job.document_id = "doc-orchestrator"
        job.revision_id = "rev-orchestrator"
        return StageResult(True, {"identity.json": "{}\n"})

    return {
        OrchestrationStage.IDENTITY: identity,
        **{
            stage: (lambda job, root, stage=stage: StageResult(True, {f"{stage.value.lower()}.json": "{}\n"}))
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
    assert all((package / "artifacts" / f"{stage.value.lower()}.json").is_file() for stage in OrchestrationStage)


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
        return StageResult(False, blockers=("Unresolved reconciliation discrepancy.",))

    executors = passing_executors()
    executors[OrchestrationStage.RECONCILIATION] = failing
    executors[OrchestrationStage.DIGITALIZATION] = lambda job, root: (_ for _ in ()).throw(AssertionError("must not run"))

    with pytest.raises(RuntimeError, match="Unresolved reconciliation discrepancy"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)

    assert calls == [OrchestrationStage.RECONCILIATION]
    assert job.status == DigitalCopyStatus.BLOCKED
    assert "Unresolved reconciliation discrepancy." in job.blockers
