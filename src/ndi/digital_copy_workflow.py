from __future__ import annotations

"""Generic Digital Copy job lifecycle orchestration primitives.

This module deliberately orchestrates existing NDI contracts rather than introducing
normative-domain interpretation. It is the service-layer boundary used by a future
API/UI and provides a deterministic, fail-closed job state model.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
import json

from .canonical import CanonicalDocument
from .hashing import sha256_file
from .ingestion import ObservationPackage
from .revision_lock import RevisionLock


class DigitalCopyStatus(StrEnum):
    NEW = "NEW"
    IDENTIFYING = "IDENTIFYING"
    EXTRACTING = "EXTRACTING"
    RECONCILING = "RECONCILING"
    DIGITALIZING = "DIGITALIZING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    GRAPHICAL_VERIFICATION = "GRAPHICAL_VERIFICATION"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
    REGRESSION_REQUIRED = "REGRESSION_REQUIRED"
    BLOCKED = "BLOCKED"
    DIGITAL_ACCEPTED = "DIGITAL_ACCEPTED"


class JobStage(StrEnum):
    INTAKE = "INTAKE"
    IDENTITY = "IDENTITY"
    EXTRACTION = "EXTRACTION"
    RECONCILIATION = "RECONCILIATION"
    DIGITALIZATION = "DIGITALIZATION"
    GRAPHICAL_VERIFICATION = "GRAPHICAL_VERIFICATION"
    VERIFICATION = "VERIFICATION"
    REGRESSION = "REGRESSION"
    ACCEPTANCE = "ACCEPTANCE"
    EXPORT = "EXPORT"


@dataclass(frozen=True)
class DigitalCopySource:
    path: str
    filename: str
    sha256: str

    @classmethod
    def from_file(cls, path: Path) -> "DigitalCopySource":
        resolved = path.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        return cls(str(resolved), resolved.name, sha256_file(resolved))


@dataclass
class DigitalCopyJob:
    job_id: str
    source: DigitalCopySource
    status: DigitalCopyStatus = DigitalCopyStatus.NEW
    stage: JobStage = JobStage.INTAKE
    document_id: str | None = None
    revision_id: str | None = None
    artifact_root: str | None = None
    parser_names: tuple[str, ...] = ()
    blockers: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def block(self, reason: str, *, status: DigitalCopyStatus = DigitalCopyStatus.BLOCKED) -> None:
        if reason not in self.blockers:
            self.blockers.append(reason)
        self.status = status

    def advance(self, stage: JobStage, status: DigitalCopyStatus) -> None:
        if self.blockers:
            raise RuntimeError("Cannot advance a blocked Digital Copy job")
        self.stage = stage
        self.status = status

    @property
    def accepted(self) -> bool:
        return self.status == DigitalCopyStatus.DIGITAL_ACCEPTED and not self.blockers

    def as_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "source": self.source.__dict__,
            "status": self.status.value,
            "stage": self.stage.value,
            "document_id": self.document_id,
            "revision_id": self.revision_id,
            "artifact_root": self.artifact_root,
            "parser_names": list(self.parser_names),
            "blockers": list(self.blockers),
            "artifacts": dict(sorted(self.artifacts.items())),
            "metadata": self.metadata,
        }


def new_job(job_id: str, source: DigitalCopySource) -> DigitalCopyJob:
    if not job_id.strip():
        raise ValueError("job_id must not be empty")
    return DigitalCopyJob(job_id=job_id, source=source)


def persist_job(job: DigitalCopyJob, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / job.job_id / "job.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(job.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_job(path: Path) -> DigitalCopyJob:
    """Load a persisted job without trusting persisted enum or binding values."""
    data = json.loads(path.read_text(encoding="utf-8"))
    source_data = data["source"]
    source = DigitalCopySource(
        path=str(source_data["path"]),
        filename=str(source_data["filename"]),
        sha256=str(source_data["sha256"]),
    )
    return DigitalCopyJob(
        job_id=str(data["job_id"]),
        source=source,
        status=DigitalCopyStatus(data["status"]),
        stage=JobStage(data["stage"]),
        document_id=data.get("document_id"),
        revision_id=data.get("revision_id"),
        artifact_root=data.get("artifact_root"),
        parser_names=tuple(data.get("parser_names", [])),
        blockers=list(data.get("blockers", [])),
        artifacts=dict(data.get("artifacts", {})),
        metadata=dict(data.get("metadata", {})),
    )


def attach_observations(job: DigitalCopyJob, package: ObservationPackage, root: Path) -> DigitalCopyJob:
    if package.source_sha256 != job.source.sha256:
        job.block("Observation package source hash does not match intake source.")
        return job
    job.document_id = package.parsers[0].document.document_id if package.parsers else None
    job.parser_names = package.parser_names
    job.artifact_root = str(root / job.job_id)
    job.advance(JobStage.EXTRACTION, DigitalCopyStatus.EXTRACTING)
    return job


def attach_canonical(job: DigitalCopyJob, document: CanonicalDocument, *, artifact_path: Path) -> DigitalCopyJob:
    if document.source_sha256 != job.source.sha256:
        job.block("Canonical document source hash does not match intake source.")
        return job
    job.document_id = document.document_id
    job.artifacts["canonical_document"] = str(artifact_path)
    job.advance(JobStage.RECONCILIATION, DigitalCopyStatus.RECONCILING)
    return job


def attach_revision_lock(job: DigitalCopyJob, lock: RevisionLock) -> DigitalCopyJob:
    if lock.source_sha256 != job.source.sha256:
        job.block("Revision lock source hash does not match intake source.")
        return job
    if job.document_id and lock.document_id != job.document_id:
        job.block("Revision lock document identity does not match job identity.")
        return job
    job.revision_id = lock.revision_id
    job.advance(JobStage.VERIFICATION, DigitalCopyStatus.VERIFICATION_REQUIRED)
    return job


def accept_job(job: DigitalCopyJob, *, final_gate_passed: bool, regression_passed: bool) -> DigitalCopyJob:
    if not regression_passed:
        job.block("Regression evidence is missing or failed.", status=DigitalCopyStatus.REGRESSION_REQUIRED)
        return job
    if not final_gate_passed:
        job.block("Final acceptance gate is not satisfied.")
        return job
    if not job.revision_id or not job.document_id:
        job.block("DIGITAL_ACCEPTED requires document identity and revision lock.")
        return job
    job.stage = JobStage.ACCEPTANCE
    job.status = DigitalCopyStatus.DIGITAL_ACCEPTED
    return job
