from pathlib import Path

from ndi.digital_copy_package import persist_package_manifest, persist_source, replay_package, write_artifact
from ndi.digital_copy_workflow import DigitalCopySource, new_job, persist_job


def make_job(tmp_path: Path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"controlled source")
    return new_job("job-replay", DigitalCopySource.from_file(source))


def test_replay_round_trips_persisted_job_and_package(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    persist_source(job, root)
    artifact = write_artifact(root, "canonical/document.json", "{}\n")
    job.artifacts["canonical"] = str(artifact)
    persist_job(job, root.parent)
    (root.parent / job.job_id / "job.json").replace(root / "job.json")
    persist_package_manifest(job, root)

    replayed, issues = replay_package(root)

    assert issues == []
    assert replayed is not None
    assert replayed.job_id == job.job_id
    assert replayed.source.sha256 == job.source.sha256


def test_replay_fails_when_packaged_source_is_tampered(tmp_path: Path) -> None:
    job = make_job(tmp_path)
    root = tmp_path / "package"
    persist_source(job, root)
    artifact = write_artifact(root, "artifact.json", "{}\n")
    job.artifacts["artifact"] = str(artifact)
    persist_job(job, root.parent)
    (root.parent / job.job_id / "job.json").replace(root / "job.json")
    persist_package_manifest(job, root)

    (root / "source" / job.source.filename).write_bytes(b"tampered")

    replayed, issues = replay_package(root)

    assert replayed is None
    assert "Packaged intake source SHA-256 does not match job intake source." in issues
