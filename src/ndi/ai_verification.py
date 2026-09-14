from __future__ import annotations

"""Independent AI verification evidence and fail-closed aggregation."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .canonical import CanonicalDocument
from .revision_lock import RevisionLock


@dataclass(frozen=True)
class AIVerificationRecord:
    verifier_id: str
    model_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    scope: tuple[str, ...]
    checks: tuple[str, ...]
    result: str
    verified_at: str
    evidence_hash: str
    independence_basis: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_ai_verification(
    document: CanonicalDocument,
    lock: RevisionLock,
    *,
    verifier_id: str,
    model_id: str,
    scope: tuple[str, ...],
    checks: tuple[str, ...],
    result: str,
    verified_at: str,
    independence_basis: str,
) -> AIVerificationRecord:
    if not verifier_id or not model_id or not scope or not checks or not verified_at or not independence_basis:
        raise ValueError("AI verification requires verifier, model, scope, checks, timestamp and independence basis")
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256:
        raise ValueError("AI verification is not bound to the locked source")
    from .verification import digital_revision
    if digital_revision(document) != lock.digital_revision:
        raise ValueError("AI verification is not bound to the locked digital revision")
    if result not in {"PASS", "FAIL"}:
        raise ValueError("AI verification result must be PASS or FAIL")
    payload = {
        "verifier_id": verifier_id,
        "model_id": model_id,
        "document_id": document.document_id,
        "source_sha256": document.source_sha256,
        "digital_revision": lock.digital_revision,
        "scope": scope,
        "checks": checks,
        "result": result,
        "verified_at": verified_at,
        "independence_basis": independence_basis,
    }
    evidence_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return AIVerificationRecord(evidence_hash=evidence_hash, **payload)


def validate_ai_verifications(records: tuple[AIVerificationRecord, ...], lock: RevisionLock) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if len(records) < 2:
        issues.append("At least two independent AI verification records are required")
    verifier_ids = [r.verifier_id for r in records]
    if len(verifier_ids) != len(set(verifier_ids)):
        issues.append("Duplicate verifier identities are not independent")
    for record in records:
        if record.document_id != lock.document_id:
            issues.append(f"Verifier {record.verifier_id} document binding mismatch")
        if record.source_sha256 != lock.source_sha256:
            issues.append(f"Verifier {record.verifier_id} source binding mismatch")
        if record.digital_revision != lock.digital_revision:
            issues.append(f"Verifier {record.verifier_id} revision binding mismatch")
        if record.result != "PASS":
            issues.append(f"Verifier {record.verifier_id} did not PASS")
        if not record.independence_basis:
            issues.append(f"Verifier {record.verifier_id} has no independence basis")
        expected = build_evidence_hash(record)
        if expected != record.evidence_hash:
            issues.append(f"Verifier {record.verifier_id} evidence hash mismatch")
    if len({r.independence_basis for r in records}) < 2:
        issues.append("Independent verifications must have distinct independence bases")
    return not issues, issues


def build_evidence_hash(record: AIVerificationRecord) -> str:
    payload = record.as_dict().copy()
    payload.pop("evidence_hash", None)
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def persist_ai_verification(record: AIVerificationRecord, root: Path) -> Path:
    directory = root / record.evidence_hash
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / "ai-verification.json"
    path.write_text(json.dumps(record.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
