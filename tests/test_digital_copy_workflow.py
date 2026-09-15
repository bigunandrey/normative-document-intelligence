from pathlib import Path

import pytest

from ndi.canonical import CanonicalDocument
from ndi.digital_copy_workflow import (
    DigitalCopySource,
    DigitalCopyStatus,
    JobStage,
    accept_job,
    attach_canonical,
    attach_revision_lock,
    new_job,
    persist_job,
)
from ndi.revision_lock import build_revision_lock


SHA = "a" * 64


def test_new_job_binds_source_hash(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-001", DigitalCopySource.from_file(source))

    assert job.status == DigitalCopyStatus.NEW
    assert job.stage == JobStage.INTAKE
    assert len(job.source.sha256) == 64


def test_persist_job_is_deterministic_json_artifact(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-002", DigitalCopySource.from_file(source))

    path = persist_job(job, tmp_path / "jobs")
    assert path.is_file()
    assert '"status": "NEW"' in path.read_text(encoding="utf-8")


def test_canonical_hash_mismatch_blocks_job(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-003", DigitalCopySource.from_file(source))
    document = CanonicalDocument(
        document_id="doc-other",
        source_name="other.pdf",
        source_sha256=SHA,
        page_count=1,
    )

    job = attach_canonical(job, document, artifact_path=tmp_path / "canonical.json")

    assert job.status == DigitalCopyStatus.BLOCKED
    assert job.blockers


def test_revision_lock_advances_only_matching_source(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-004", DigitalCopySource.from_file(source))
    document = CanonicalDocument(
        document_id="doc-good",
        source_name=source.name,
        source_sha256=job.source.sha256,
        page_count=1,
    )
    job = attach_canonical(job, document, artifact_path=tmp_path / "canonical.json")
    lock = build_revision_lock(document)

    job = attach_revision_lock(job, lock)

    assert job.revision_id == lock.revision_id
    assert job.status == DigitalCopyStatus.VERIFICATION_REQUIRED
    assert job.stage == JobStage.VERIFICATION


def test_accept_requires_regression_and_revision(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-005", DigitalCopySource.from_file(source))
    blocked = accept_job(job, final_gate_passed=True, regression_passed=True)

    assert blocked.status == DigitalCopyStatus.BLOCKED
    assert "revision lock" in blocked.blockers[-1].lower()


def test_accept_without_regression_is_not_accepted(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    job = new_job("job-006", DigitalCopySource.from_file(source))
    job.document_id = "doc-1"
    job.revision_id = "rev-1"

    job = accept_job(job, final_gate_passed=True, regression_passed=False)

    assert job.status == DigitalCopyStatus.REGRESSION_REQUIRED
    assert not job.accepted


def test_blank_job_id_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    with pytest.raises(ValueError):
        new_job(" ", DigitalCopySource.from_file(source))
