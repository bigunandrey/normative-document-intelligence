from __future__ import annotations

"""Production-facing orchestration boundary for one generic Digital Copy job.

The orchestrator composes already-implemented NDI contracts through injected stage
executors. It deliberately does not invent normative content: a missing executor,
failed stage, or missing stage evidence blocks the job and prevents later stages.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Mapping

from .digital_copy_package import persist_package, write_artifact
from .digital_copy_workflow import (
    DigitalCopyJob,
    DigitalCopyStatus,
    JobStage,
    accept_job,
    persist_job_file,
)


class OrchestrationStage(StrEnum):
    IDENTITY = "IDENTITY"
    EXTRACTION = "EXTRACTION"
    RECONCILIATION = "RECONCILIATION"
    DIGITALIZATION = "DIGITALIZATION"
    GRAPHICAL_VERIFICATION = "GRAPHICAL_VERIFICATION"
    VERIFICATION = "VERIFICATION"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True)
class StageResult:
    """Deterministic result returned by one injected stage executor."""

    passed: bool
    artifacts: Mapping[str, str | bytes] = ()
    blockers: tuple[str, ...] = ()


StageExecutor = Callable[[DigitalCopyJob, Path], StageResult]


_STAGE_TARGETS: dict[OrchestrationStage, tuple[JobStage, DigitalCopyStatus]] = {
    OrchestrationStage.IDENTITY: (JobStage.IDENTITY, DigitalCopyStatus.IDENTIFYING),
    OrchestrationStage.EXTRACTION: (JobStage.EXTRACTION, DigitalCopyStatus.EXTRACTING),
    OrchestrationStage.RECONCILIATION: (JobStage.RECONCILIATION, DigitalCopyStatus.RECONCILING),
    OrchestrationStage.DIGITALIZATION: (JobStage.DIGITALIZATION, DigitalCopyStatus.DIGITALIZING),
    OrchestrationStage.GRAPHICAL_VERIFICATION: (
        JobStage.GRAPHICAL_VERIFICATION,
        DigitalCopyStatus.GRAPHICAL_VERIFICATION,
    ),
    OrchestrationStage.VERIFICATION: (JobStage.VERIFICATION, DigitalCopyStatus.VERIFICATION_REQUIRED),
    OrchestrationStage.REGRESSION: (JobStage.REGRESSION, DigitalCopyStatus.REGRESSION_REQUIRED),
}


class DigitalCopyOrchestrator:
    """Run the generic lifecycle and persist a replayable package after each stage."""

    def __init__(self, package_root: Path, executors: Mapping[OrchestrationStage, StageExecutor]):
        self.package_root = package_root.resolve()
        self.executors = dict(executors)

    def _persist(self, job: DigitalCopyJob) -> None:
        persist_job_file(job, self.package_root / "job.json")
        persist_package(job, self.package_root)

    def _run_stage(self, job: DigitalCopyJob, stage: OrchestrationStage) -> None:
        if job.blockers:
            raise RuntimeError("Cannot run a stage for a blocked Digital Copy job")
        executor = self.executors.get(stage)
        if executor is None:
            job.block(f"Missing executor for orchestration stage: {stage.value}")
            self._persist(job)
            raise RuntimeError(job.blockers[-1])

        target_stage, target_status = _STAGE_TARGETS[stage]
        job.advance(target_stage, target_status)
        self._persist(job)

        try:
            result = executor(job, self.package_root)
        except Exception as exc:  # noqa: BLE001 - stage boundary must fail closed.
            job.block(f"Stage {stage.value} failed with exception: {type(exc).__name__}: {exc}")
            self._persist(job)
            raise

        if not result.passed:
            reasons = result.blockers or (f"Stage {stage.value} failed.",)
            for reason in reasons:
                job.block(reason)
            self._persist(job)
            raise RuntimeError(job.blockers[-1])

        for name, content in sorted(result.artifacts.items()):
            relative = name if name.startswith("artifacts/") else f"artifacts/{name}"
            path = write_artifact(self.package_root, relative, content)
            job.artifacts[name] = str(path)

        self._persist(job)

    def run(self, job: DigitalCopyJob) -> DigitalCopyJob:
        """Run all configured stages and fail closed on the first missing/failed stage."""
        self.package_root.mkdir(parents=True, exist_ok=True)
        self._persist(job)
        for stage in OrchestrationStage:
            self._run_stage(job, stage)

        job = accept_job(job, final_gate_passed=True, regression_passed=True)
        self._persist(job)
        return job
