from __future__ import annotations

"""Immutable operational revision archive for accepted Digital Copy evidence."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .ai_verification import AIVerificationRecord, validate_ai_verifications
from .revision_lock import RevisionLock, verify_revision_lock


ARCHIVE_VERSION = "1.0"


@dataclass(frozen=True)
class RevisionArchiveRecord:
    archive_id: str
    revision_id: str
    document_id: str
    source_sha256: str
    manifest_sha256: str
    verification_hashes: tuple[str, ...]
    result: str
    created_at: str

    def as_dict(self) -> dict[str, object]:
        return {
            "archive_version": ARCHIVE_VERSION,
            "archive_id": self.archive_id,
            "revision_id": self.revision_id,
            "document_id": self.document_id,
            "source_sha256": self.source_sha256,
            "manifest_sha256": self.manifest_sha256,
            "verification_hashes": list(self.verification_hashes),
            "result": self.result,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def next_archive_id(root: Path) -> str:
    numbers = []
    for path in root.glob("Rev_*"):
        if path.is_dir() and path.name[4:].isdigit():
            numbers.append(int(path.name[4:]))
    return f"Rev_{(max(numbers, default=0) + 1):03d}"


def build_archive_record(
    lock: RevisionLock,
    *,
    verification_records: tuple[AIVerificationRecord, ...],
    result: str,
    created_at: str,
    archive_id: str,
) -> RevisionArchiveRecord:
    if result not in {"PASS", "BLOCKED"}:
        raise ValueError("Archive result must be PASS or BLOCKED")
    if not created_at.strip():
        raise ValueError("Archive creation timestamp is required")
    hashes = tuple(sorted(record.evidence_hash for record in verification_records))
    return RevisionArchiveRecord(
        archive_id=archive_id,
        revision_id=lock.revision_id,
        document_id=lock.document_id,
        source_sha256=lock.source_sha256,
        manifest_sha256=lock.manifest_sha256(),
        verification_hashes=hashes,
        result=result,
        created_at=created_at,
    )


def persist_revision_archive(
    lock: RevisionLock,
    lock_root: Path,
    archive_root: Path,
    *,
    verification_records: tuple[AIVerificationRecord, ...],
    result: str,
    created_at: str,
    handoff: Mapping[str, object] | None = None,
) -> RevisionArchiveRecord:
    """Persist an immutable Rev_NNN archive after validating its locked evidence."""
    if not verify_revision_lock_by_manifest(lock, lock_root):
        raise ValueError("Revision lock is missing or invalid; archive creation blocked")
    valid, issues = validate_ai_verifications(verification_records, lock)
    if result == "PASS" and not valid:
        raise ValueError("Cannot archive PASS revision: " + "; ".join(issues))

    archive_root.mkdir(parents=True, exist_ok=True)
    archive_id = next_archive_id(archive_root)
    directory = archive_root / archive_id
    directory.mkdir(parents=False, exist_ok=False)

    record = build_archive_record(
        lock,
        verification_records=verification_records,
        result=result,
        created_at=created_at,
        archive_id=archive_id,
    )
    (directory / "archive-record.json").write_text(record.to_json(), encoding="utf-8")
    lock_manifest = lock_root / lock.revision_id / "reproducibility-manifest.json"
    (directory / "reproducibility-manifest.json").write_text(lock_manifest.read_text(encoding="utf-8"), encoding="utf-8")
    verification_dir = directory / "verification"
    verification_dir.mkdir()
    for verification in sorted(verification_records, key=lambda item: item.evidence_hash):
        (verification_dir / f"{verification.evidence_hash}.json").write_text(
            json.dumps(verification.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if handoff is not None:
        (directory / "handoff.json").write_text(
            json.dumps(dict(handoff), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return record


def verify_revision_lock_by_manifest(lock: RevisionLock, root: Path) -> bool:
    return verify_revision_lock_stub(lock, root)


def verify_revision_lock_stub(lock: RevisionLock, root: Path) -> bool:
    directory = root / lock.revision_id
    manifest = directory / "reproducibility-manifest.json"
    canonical = directory / "digital-representation.json"
    if not manifest.is_file() or not canonical.is_file():
        return False
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("revision_id") == lock.revision_id
        and data.get("document_id") == lock.document_id
        and data.get("source_sha256") == lock.source_sha256
        and _sha256_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n") == lock.manifest_sha256()
    )


def verify_revision_archive(root: Path, archive_id: str) -> tuple[bool, list[str]]:
    directory = root / archive_id
    record_path = directory / "archive-record.json"
    manifest_path = directory / "reproducibility-manifest.json"
    issues: list[str] = []
    if not directory.is_dir():
        return False, ["Revision archive directory is missing."]
    if not record_path.is_file() or not manifest_path.is_file():
        issues.append("Revision archive record or reproducibility manifest is missing.")
        return False, issues
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"Invalid revision archive JSON: {exc}"]
    if record.get("archive_id") != archive_id:
        issues.append("Archive ID mismatch.")
    if record.get("revision_id") != manifest.get("revision_id"):
        issues.append("Archive revision binding mismatch.")
    if record.get("document_id") != manifest.get("document_id"):
        issues.append("Archive document binding mismatch.")
    if record.get("source_sha256") != manifest.get("source_sha256"):
        issues.append("Archive source binding mismatch.")
    if record.get("manifest_sha256") != _sha256_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"):
        issues.append("Archive manifest hash mismatch.")
    verification_dir = directory / "verification"
    expected = set(record.get("verification_hashes", []))
    actual = {p.stem for p in verification_dir.glob("*.json")} if verification_dir.is_dir() else set()
    if expected != actual:
        issues.append("Archived verification set does not match archive record.")
    return not issues, issues
