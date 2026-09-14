import json
from pathlib import Path

import pytest

from ndi import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor, build_revision_lock, persist_revision_lock, verify_revision_lock


SHA = "a" * 64


def make_doc() -> CanonicalDocument:
    doc = CanonicalDocument("doc-test", "test.pdf", SHA, 1, parser_versions={"p1": "1.0", "p2": "2.0"})
    doc.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="same", anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10), char_start=0, char_end=4)))
    return doc


def test_revision_lock_is_deterministic():
    first = build_revision_lock(make_doc())
    second = build_revision_lock(make_doc())
    assert first == second
    assert first.revision_id.startswith("rev-")
    assert first.digital_revision.startswith("sha256:")


def test_revision_lock_binds_evidence_hashes_deterministically():
    lock = build_revision_lock(make_doc(), evidence_hashes={"graphical": "b" * 64, "external": "c" * 64})
    assert lock.evidence_hashes == (("external", "c" * 64), ("graphical", "b" * 64))
    assert lock.manifest_sha256() == build_revision_lock(make_doc(), evidence_hashes={"external": "c" * 64, "graphical": "b" * 64}).manifest_sha256()


def test_persisted_lock_is_reproducible_and_immutable(tmp_path: Path):
    lock = persist_revision_lock(make_doc(), tmp_path)
    assert verify_revision_lock(make_doc(), tmp_path, lock.revision_id)
    with pytest.raises(FileExistsError):
        persist_revision_lock(make_doc(), tmp_path)


def test_tampered_canonical_representation_fails_verification(tmp_path: Path):
    lock = persist_revision_lock(make_doc(), tmp_path)
    path = tmp_path / lock.revision_id / "digital-representation.json"
    path.write_text(path.read_text(encoding="utf-8").replace("same", "tampered"), encoding="utf-8")
    assert not verify_revision_lock(make_doc(), tmp_path, lock.revision_id)


def test_manifest_binds_source_hash(tmp_path: Path):
    lock = persist_revision_lock(make_doc(), tmp_path)
    manifest_path = tmp_path / lock.revision_id / "reproducibility-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_sha256"] = "d" * 64
    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
    assert not verify_revision_lock(make_doc(), tmp_path, lock.revision_id)
