from pathlib import Path

import pytest

from ndi.digital_copy_package import (
    persist_package,
    persist_package_manifest,
    persist_source,
    replay_package,
    verify_package,
    write_artifact,
)
from ndi.digital_copy_workflow import DigitalCopySource, new_job


def make_job(tmp_path: Path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"controlled source")
    return new_job("job-001", DigitalCopySource.from_file(source))


def test_package_manifest_records_and_verifies_artifact(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    persist_source(job, root)
    artifact = write_artifact(root, "extraction/observations.json", "{}\n")
    job.artifacts["observations"] = str(artifact)

    manifest = persist_package_manifest(job, root)

    assert manifest.is_file()
    ok, issues = verify_package(job, root)
    assert ok
    assert issues == []


def test_package_verification_fails_closed_on_tampering(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    persist_source(job, root)
    artifact = write_artifact(root, "canonical/document.json", "original\n")
    job.artifacts["canonical"] = str(artifact)
    persist_package_manifest(job, root)

    artifact.write_text("tampered\n", encoding="utf-8")

    ok, issues = verify_package(job, root)
    assert not ok
    assert "Package artifact hash mismatch: canonical/document.json" in issues


def test_package_rejects_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="inside the package root"):
        write_artifact(tmp_path / "package", "../escape.txt", "x")


def test_package_verification_binds_source_identity(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    persist_source(job, root)
    artifact = write_artifact(root, "artifact.json", "{}\n")
    job.artifacts["artifact"] = str(artifact)
    persist_package_manifest(job, root)

    job.source = DigitalCopySource(job.source.path, job.source.filename, "0" * 64)

    ok, issues = verify_package(job, root)
    assert not ok
    assert "Package source SHA-256 does not match job intake source." in issues


def test_persist_package_is_self_contained_and_replayable(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    artifact = write_artifact(root, "placeholder.txt", "artifact\n")
    job.artifacts["artifact"] = str(artifact)

    persist_package(job, root)

    # Rebind the artifact to a package-local file before final manifest creation.
    artifact.unlink()
    artifact = write_artifact(root, "artifact.json", "artifact\n")
    job.artifacts["artifact"] = str(artifact)
    persist_package_manifest(job, root)
    Path(job.source.path).unlink()

    replayed, issues = replay_package(root)

    assert issues == []
    assert replayed is not None
    assert Path(replayed.source.path) == (root / "source" / job.source.filename).resolve()
    assert Path(replayed.artifacts["artifact"]) == (root / "artifact.json").resolve()
    assert Path(replayed.source.path).is_file()
    assert Path(replayed.artifacts["artifact"]).is_file()
