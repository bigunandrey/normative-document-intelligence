from __future__ import annotations

"""Source identity and revision registry for normative documents."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any
import hashlib
import json


class SourceType(StrEnum):
    USER_SUPPLIED = "user_supplied"
    OFFICIAL_WEB = "official_web"
    OFFICIAL_REPOSITORY = "official_repository"
    PUBLISHER = "publisher"
    THIRD_PARTY = "third_party"
    UNKNOWN = "unknown"


class Compatibility(StrEnum):
    SAME_REVISION = "same_revision"
    DIFFERENT_REVISION = "different_revision"
    UNVERIFIED = "unverified"
    INVALID = "invalid"


@dataclass(frozen=True)
class DocumentIdentity:
    designation: str
    title: str | None = None
    edition_year: int | None = None
    amendments: tuple[str, ...] = ()
    publication_date: str | None = None
    status: str | None = None
    issuing_organization: str | None = None

    def normalized_key(self) -> str:
        payload = {
            "designation": self.designation.strip().casefold(),
            "edition_year": self.edition_year,
            "amendments": tuple(a.strip().casefold() for a in self.amendments),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_name: str
    source_type: SourceType
    sha256: str
    acquired_at: str
    identity: DocumentIdentity
    source_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.sha256) != 64:
            raise ValueError("sha256 must be a 64-character SHA-256 digest")
        try:
            int(self.sha256, 16)
        except ValueError as exc:
            raise ValueError("sha256 must be hexadecimal") from exc

    def identity_fingerprint(self) -> str:
        return hashlib.sha256(self.identity.normalized_key().encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    source_name: str
    source_type: SourceType
    identity: DocumentIdentity
    source_url: str | None = None
    sha256: str | None = None
    authority_verified: bool = False
    revision_verified: bool = False
    evidence: tuple[str, ...] = ()

    def compatibility_with(self, supplied: SourceRecord) -> Compatibility:
        if not self.authority_verified or not self.revision_verified:
            return Compatibility.UNVERIFIED
        if self.identity.normalized_key() != supplied.identity.normalized_key():
            return Compatibility.DIFFERENT_REVISION
        if self.sha256 and self.sha256 != supplied.sha256:
            return Compatibility.DIFFERENT_REVISION
        return Compatibility.SAME_REVISION


@dataclass(frozen=True)
class SourceRegistry:
    records: tuple[SourceRecord, ...] = ()

    def register(self, record: SourceRecord) -> "SourceRegistry":
        if any(r.source_id == record.source_id for r in self.records):
            raise ValueError(f"Duplicate source_id: {record.source_id}")
        return SourceRegistry(self.records + (record,))

    def get(self, source_id: str) -> SourceRecord:
        for record in self.records:
            if record.source_id == source_id:
                return record
        raise KeyError(source_id)

    def as_dict(self) -> dict[str, Any]:
        return {"records": [r.as_dict() for r in self.records]}
