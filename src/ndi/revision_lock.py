from __future__ import annotations

"""Immutable digital-representation revision locks and reproducibility manifests."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .canonical import CanonicalDocument
from .verification import digital_revision


PROTOCOL_VERSION = "2.1"


@dataclass(frozen=True)
class RevisionLock:
    revision_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    protocol_version: str
    parser_versions: tuple[tuple[str, str], ...]
    evidence_hashes: tuple[tuple[str, str], ...] = ()

    def manifest_dict(self) -> dict[str, object]:
        return asdict(self)

    def manifest_json(self) -> str:
        return json.dumps(self.manifest_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    def manifest_sha256(self) -> str:
        return hashlib.sha256(self.manifest_json().encode("utf-8")).hexdigest()


def _validate_sha256(value: str, field: str) -> None:
    if len(value) != 64:
        raise ValueError(f"{field} must be a SHA-256 hexadecimal digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be a SHA-256 hexadecimal digest") from exc


def build_revision_lock(
    document: CanonicalDocument,
    *,
    evidence_hashes: dict[str, str] | None = None,
    protocol_version: str = PROTOCOL_VERSION,
) -> RevisionLock:
    _validate_sha256(document.source_sha256, "source_sha256")
    revision = digital_revision(document)
    evidence = tuple(sorted((name, digest) for name, digest in (evidence_hashes or {}).items()))
    for name, digest in evidence:
        _validate_sha256(digest, f"evidence hash for {name}")
    revision_id_payload = json.dumps(
        {
            "document_id": document.document_id,
            "source_sha256": document.source_sha256,
            "digital_revision": revision,
            "protocol_version": protocol_version,
            "parser_versions": sorted(document.parser_versions.items()),
            "evidence_hashes": evidence,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    revision_id = "rev-" + hashlib.sha256(revision_id_payload.encode("utf-8")).hexdigest()[:24]
    return RevisionLock(
        revision_id=revision_id,
        document_id=document.document_id,
        source_sha256=document.source_sha256,
        digital_revision=revision,
        protocol_version=protocol_version,
        parser_versions=tuple(sorted(document.parser_versions.items())),
        evidence_hashes=evidence,
    )


def persist_revision_lock(document: CanonicalDocument, root: Path, *, evidence_hashes: dict[str, str] | None = None) -> RevisionLock:
    lock = build_revision_lock(document, evidence_hashes=evidence_hashes)
    directory = root / lock.revision_id
    directory.mkdir(parents=True, exist_ok=False)
    canonical_path = directory / "digital-representation.json"
    manifest_path = directory / "reproducibility-manifest.json"
    canonical_path.write_text(document.to_json() + "\n", encoding="utf-8")
    manifest_path.write_text(lock.manifest_json(), encoding="utf-8")
    return lock


def verify_revision_lock(document: CanonicalDocument, root: Path, revision_id: str) -> bool:
    directory = root / revision_id
    canonical_path = directory / "digital-representation.json"
    manifest_path = directory / "reproducibility-manifest.json"
    if not directory.is_dir() or not canonical_path.is_file() or not manifest_path.is_file():
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("revision_id") != revision_id:
        return False
    if manifest.get("source_sha256") != document.source_sha256:
        return False
    if manifest.get("document_id") != document.document_id:
        return False
    stored = canonical_path.read_text(encoding="utf-8").rstrip("\n")
    if stored != document.to_json():
        return False
    if manifest.get("digital_revision") != digital_revision(document):
        return False
    if tuple(sorted(map(tuple, manifest.get("parser_versions", [])))) != tuple(sorted(document.parser_versions.items())):
        return False
    return True
