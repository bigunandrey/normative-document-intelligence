import json
from pathlib import Path

import pytest

from ndi import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    SourceAnchor,
    build_ai_verification,
    build_revision_lock,
    persist_revision_archive,
    persist_revision_lock,
    verify_revision_archive,
)

SHA = "a" * 64


def make_doc() -> CanonicalDocument:
    doc = CanonicalDocument("doc-archive", "source.pdf", SHA, 1, parser_versions={"p1": "1.0"})
    doc.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="same", anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10), char_start=0, char_end=4)))
    return doc


def verifications(doc, lock):
    return (
        build_ai_verification(doc, lock, verifier_id="v1", model_id="m1", scope=("structure",), checks=("source",), result="PASS", verified_at="2026-09-15T12:00:00Z", independence_basis="parser-A"),
        build_ai_verification(doc, lock, verifier_id="v2", model_id="m2", scope=("structure",), checks=("source",), result="PASS", verified_at="2026-09-15T12:01:00Z", independence_basis="parser-B"),
    )


def test_archive_is_sequential_and_rejects_duplicate_revision(tmp_path: Path):
    doc = make_doc()
    lock_root = tmp_path / "locks"
    lock = persist_revision_lock(doc, lock_root)
    archive_root = tmp_path / "archive"
    records = verifications(doc, lock)
    first = persist_revision_archive(lock, lock_root, archive_root, verification_records=records, result="PASS", created_at="2026-09-15T12:02:00Z")
    assert first.archive_id == "Rev_001"
    assert verify_revision_archive(archive_root, "Rev_001") == (True, [])
    with pytest.raises(FileExistsError, match="already archived"):
        persist_revision_archive(lock, lock_root, archive_root, verification_records=records, result="PASS", created_at="2026-09-15T12:03:00Z")


def test_pass_archive_requires_two_independent_passes(tmp_path: Path):
    doc = make_doc()
    lock_root = tmp_path / "locks"
    lock = persist_revision_lock(doc, lock_root)
    with pytest.raises(ValueError, match="Cannot archive PASS revision"):
        persist_revision_archive(lock, lock_root, tmp_path / "archive", verification_records=(), result="PASS", created_at="2026-09-15T12:00:00Z")


def test_tampered_archive_manifest_is_detected(tmp_path: Path):
    doc = make_doc()
    lock_root = tmp_path / "locks"
    lock = persist_revision_lock(doc, lock_root)
    archive_root = tmp_path / "archive"
    persist_revision_archive(lock, lock_root, archive_root, verification_records=verifications(doc, lock), result="PASS", created_at="2026-09-15T12:00:00Z")
    path = archive_root / "Rev_001" / "reproducibility-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["source_sha256"] = "b" * 64
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ok, issues = verify_revision_archive(archive_root, "Rev_001")
    assert not ok
    assert "Archive source binding mismatch." in issues


def test_tampered_verification_is_detected(tmp_path: Path):
    doc = make_doc()
    lock_root = tmp_path / "locks"
    lock = persist_revision_lock(doc, lock_root)
    archive_root = tmp_path / "archive"
    persist_revision_archive(lock, lock_root, archive_root, verification_records=verifications(doc, lock), result="PASS", created_at="2026-09-15T12:00:00Z")
    path = next((archive_root / "Rev_001" / "verification").glob("*.json"))
    data = json.loads(path.read_text(encoding="utf-8"))
    data["result"] = "FAIL"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ok, issues = verify_revision_archive(archive_root, "Rev_001")
    assert not ok
    assert any("hash mismatch" in issue for issue in issues)


def test_archive_is_fail_closed_for_invalid_locked_source(tmp_path: Path):
    doc = make_doc()
    lock = build_revision_lock(doc)
    with pytest.raises(ValueError, match="Revision lock is missing or invalid"):
        persist_revision_archive(lock, tmp_path / "missing-locks", tmp_path / "archive", verification_records=verifications(doc, lock), result="PASS", created_at="2026-09-15T12:00:00Z")
