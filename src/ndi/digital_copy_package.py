from __future__ import annotations

"""Persistent, deterministic and replayable artifact package for a Digital Copy job."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
import shutil

from .digital_copy_workflow import DigitalCopyJob, DigitalCopySource, load_job, persist_job_file

PACKAGE_VERSION = "1.1"


@dataclass(frozen=True)
class PackageManifest:
    package_version: str
    job_id: str
    document_id: str | None
    source_filename: str
    source_sha256: str
    revision_id: str | None
    artifacts: tuple[tuple[str, str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "package_version": self.package_version,
            "job_id": self.job_id,
            "document_id": self.document_id,
            "source": {"filename": self.source_filename, "sha256": self.source_sha256},
            "revision_id": self.revision_id,
            "artifacts": [
                {"name": n, "path": p, "sha256": h} for n, p, h in self.artifacts
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_path(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Artifact path must remain inside the package root")
    path = (root / relative).resolve()
    package_root = root.resolve()
    if package_root not in path.parents:
        raise ValueError("Artifact path escapes package root")
    return path


def write_artifact(root: Path, relative_path: str, content: str | bytes) -> Path:
    path = _safe_path(root, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def persist_source(job: DigitalCopyJob, root: Path) -> Path:
    """Copy the immutable intake source into the package and verify its hash."""
    source = Path(job.source.path)
    if not source.is_file():
        raise FileNotFoundError(source)
    destination = _safe_path(root, f"source/{job.source.filename}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    actual = _sha256(destination)
    if actual != job.source.sha256:
        raise ValueError("Packaged source SHA-256 does not match job intake source.")
    return destination


def build_package_manifest(job: DigitalCopyJob, root: Path) -> PackageManifest:
    package_root = root.resolve()
    entries: list[tuple[str, str, str]] = []
    for name, declared_path in sorted(job.artifacts.items()):
        path = Path(declared_path)
        if not path.is_absolute():
            path = package_root / path
        path = path.resolve()
        if package_root not in path.parents or not path.is_file():
            raise FileNotFoundError(f"Missing declared artifact: {name}")
        entries.append((name, path.relative_to(package_root).as_posix(), _sha256(path)))
    return PackageManifest(
        PACKAGE_VERSION,
        job.job_id,
        job.document_id,
        job.source.filename,
        job.source.sha256,
        job.revision_id,
        tuple(entries),
    )


def persist_package_manifest(job: DigitalCopyJob, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return write_artifact(root, "package-manifest.json", build_package_manifest(job, root).to_json())


def persist_package(job: DigitalCopyJob, root: Path) -> Path:
    """Create a complete self-contained package in one deterministic operation."""
    root.mkdir(parents=True, exist_ok=True)
    persist_source(job, root)
    persist_job_file(job, root / "job.json")
    persist_package_manifest(job, root)
    return root


def verify_package(job: DigitalCopyJob, root: Path) -> tuple[bool, list[str]]:
    manifest_path = root / "package-manifest.json"
    if not manifest_path.is_file():
        return False, ["package-manifest.json is missing."]
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"Invalid package manifest: {exc}"]
    issues: list[str] = []
    if data.get("package_version") != PACKAGE_VERSION:
        issues.append("Unsupported package version.")
    if data.get("job_id") != job.job_id:
        issues.append("Package job_id does not match job.")
    source = data.get("source") or {}
    if source.get("sha256") != job.source.sha256:
        issues.append("Package source SHA-256 does not match job intake source.")
    if source.get("filename") != job.source.filename:
        issues.append("Package source filename does not match job intake source.")
    if data.get("document_id") != job.document_id:
        issues.append("Package document identity does not match job.")
    if data.get("revision_id") != job.revision_id:
        issues.append("Package revision ID does not match job.")

    packaged_source = _safe_path(root, f"source/{job.source.filename}")
    if not packaged_source.is_file():
        issues.append("Packaged intake source is missing.")
    elif _sha256(packaged_source) != job.source.sha256:
        issues.append("Packaged intake source SHA-256 does not match job intake source.")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        issues.append("Package artifacts manifest is invalid.")
        return False, sorted(set(issues))

    manifest_entries: dict[str, tuple[str, str]] = {}
    for entry in artifacts:
        if not isinstance(entry, dict):
            issues.append("Package artifact entry is invalid.")
            continue
        name, relative, expected = entry.get("name"), entry.get("path"), entry.get("sha256")
        if not all(isinstance(value, str) for value in (name, relative, expected)):
            issues.append("Package artifact entry lacks name, path or SHA-256.")
            continue
        if name in manifest_entries:
            issues.append(f"Duplicate package artifact name: {name}")
            continue
        manifest_entries[name] = (relative, expected)
        try:
            path = _safe_path(root, relative)
        except ValueError:
            issues.append(f"Package artifact path escapes root: {relative}")
            continue
        if not path.is_file():
            issues.append(f"Missing package artifact: {relative}")
            continue
        if _sha256(path) != expected:
            issues.append(f"Package artifact hash mismatch: {relative}")

    declared_names = set(job.artifacts)
    manifest_names = set(manifest_entries)
    for name in sorted(declared_names - manifest_names):
        issues.append(f"Job artifact is missing from package manifest: {name}")
    for name in sorted(manifest_names - declared_names):
        issues.append(f"Package manifest contains undeclared job artifact: {name}")
    for name in sorted(declared_names & manifest_names):
        relative, _ = manifest_entries[name]
        try:
            declared = Path(job.artifacts[name]).resolve()
            packaged = _safe_path(root, relative)
            if declared != packaged:
                issues.append(f"Job artifact path does not match package manifest: {name}")
        except ValueError:
            issues.append(f"Job artifact path escapes package root: {name}")

    return not issues, sorted(set(issues))


def replay_package(root: Path) -> tuple[DigitalCopyJob | None, list[str]]:
    """Reload a persisted job, verify bindings, and rebind all paths to package-local files."""
    root = root.resolve()
    job_path = root / "job.json"
    if not job_path.is_file():
        return None, ["job.json is missing."]
    try:
        job = load_job(job_path)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [f"Invalid persisted job: {exc}"]
    ok, issues = verify_package(job, root)
    if not ok:
        return None, issues

    job.source = DigitalCopySource(
        path=str(_safe_path(root, f"source/{job.source.filename}")),
        filename=job.source.filename,
        sha256=job.source.sha256,
    )
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["artifacts"]:
        job.artifacts[entry["name"]] = str(_safe_path(root, entry["path"]))
    job.artifact_root = str(root)
    return job, []
