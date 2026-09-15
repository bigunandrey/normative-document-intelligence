from __future__ import annotations

"""Production-facing orchestration boundary for one generic Digital Copy job.

The orchestrator composes already-implemented NDI contracts through injected stage
executors. It deliberately does not invent normative content: a missing executor,
failed stage, or invalid stage evidence blocks the job and prevents later stages.
"""

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Callable, Mapping

from .digital_copy_package import persist_package, write_artifact
from .digital_copy_stage_contracts import StageEvidence, StageEvidenceKind, apply_bindings
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


StageExecutor = Callable[[DigitalCopyJob, Path], StageEvidence]

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

_STAGE_EVIDENCE_KIND: dict[OrchestrationStage, StageEvidenceKind] = {
    stage: StageEvidenceKind(stage.value) for stage in OrchestrationStage
}


@dataclass(frozen=True)
class StageRecord:
    """Persistable summary of one completed orchestration stage."""

    stage: str
    kind: str
    passed: bool
    artifacts: tuple[str, ...]
    blockers: tuple[str, ...]
    bindings: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "kind": self.kind,
            "passed": self.passed,
            "artifacts": list(self.artifacts),
            "blockers": list(self.blockers),
            "bindings": {key: value for key, value in self.bindings},
        }


class DigitalCopyOrchestrator:
    """Run the generic lifecycle and persist a replayable package after each stage."""

    def __init__(self, package_root: Path, executors: Mapping[OrchestrationStage, StageExecutor]):
        self.package_root = package_root.resolve()
        self.executors = dict(executors)

    def _persist(self, job: DigitalCopyJob) -> None:
        job.artifact_root = str(self.package_root)
        persist_job_file(job, self.package_root / "job.json")
        persist_package(job, self.package_root)

    def _persist_stage_records(self, job: DigitalCopyJob) -> None:
        records = job.metadata.get("stage_evidence", [])
        payload = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        path = write_artifact(self.package_root, "artifacts/stage-evidence.json", payload)
        job.artifacts["stage_evidence"] = str(path)

    def _persist_extraction_log(self, job: DigitalCopyJob) -> None:
        records = [record for record in job.metadata.get("stage_evidence", []) if record.get("stage") == OrchestrationStage.EXTRACTION.value]
        payload = json.dumps(
            {
                "job_id": job.job_id,
                "document_id": job.document_id,
                "source_sha256": job.source.sha256,
                "parser_names": list(job.parser_names),
                "extraction_evidence": records,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        path = write_artifact(self.package_root, "artifacts/extraction-log.json", payload)
        job.artifacts["extraction_log"] = str(path)

    def _record_evidence(self, job: DigitalCopyJob, stage: OrchestrationStage, evidence: StageEvidence) -> None:
        record = StageRecord(
            stage=stage.value,
            kind=evidence.kind.value,
            passed=evidence.passed,
            artifacts=tuple(sorted(evidence.artifacts)),
            blockers=tuple(evidence.blockers),
            bindings=tuple(sorted((str(key), str(value)) for key, value in evidence.bindings.items())),
        )
        history = job.metadata.setdefault("stage_evidence", [])
        history.append(record.as_dict())
        self._persist_stage_records(job)
        if stage == OrchestrationStage.EXTRACTION:
            self._persist_extraction_log(job)

    def _persist_handoff(self, job: DigitalCopyJob) -> None:
        payload = json.dumps(
            {
                "handoff_version": "1.0",
                "job_id": job.job_id,
                "document_id": job.document_id,
                "revision_id": job.revision_id,
                "source": {"filename": job.source.filename, "sha256": job.source.sha256},
                "status": job.status.value,
                "stage": job.stage.value,
                "accepted": job.accepted,
                "blockers": list(job.blockers),
                "artifacts": dict(sorted(job.artifacts.items())),
                "next_system": "downstream-normative-domain",
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        path = write_artifact(self.package_root, "artifacts/handoff.json", payload)
        job.artifacts["handoff"] = str(path)

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
            evidence = executor(job, self.package_root)
            if not isinstance(evidence, StageEvidence):
                raise TypeError("Stage executor must return StageEvidence")
            evidence.validate()
            expected_kind = _STAGE_EVIDENCE_KIND[stage]
            if evidence.kind != expected_kind:
                raise ValueError(
                    f"Stage {stage.value} returned evidence kind {evidence.kind.value}; "
                    f"expected {expected_kind.value}"
                )
            apply_bindings(job, evidence.bindings)
        except Exception as exc:  # noqa: BLE001 - stage boundary must fail closed.
            job.block(f"Stage {stage.value} failed with exception: {type(exc).__name__}: {exc}")
            self._persist(job)
            raise

        if not evidence.passed:
            for reason in evidence.blockers:
                job.block(reason)
            self._record_evidence(job, stage, evidence)
            self._persist(job)
            raise RuntimeError(job.blockers[-1])

        for name, content in sorted(evidence.artifacts.items()):
            relative = name if name.startswith("artifacts/") else f"artifacts/{name}"
            path = write_artifact(self.package_root, relative, content)
            job.artifacts[name] = str(path)

        self._record_evidence(job, stage, evidence)
        self._persist(job)

    def run(self, job: DigitalCopyJob) -> DigitalCopyJob:
        """Run all configured stages and fail closed on the first missing/failed stage."""
        self.package_root.mkdir(parents=True, exist_ok=True)
        self._persist(job)
        for stage in OrchestrationStage:
            self._run_stage(job, stage)

        job = accept_job(job, final_gate_passed=True, regression_passed=True)
        self._persist_handoff(job)
        self._persist(job)
        return job
