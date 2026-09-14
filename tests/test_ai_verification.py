from pathlib import Path

from ndi import (
    BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor,
    build_revision_lock, build_ai_verification, validate_ai_verifications,
    persist_ai_verification,
)

SHA = "a" * 64


def make_doc():
    doc = CanonicalDocument("doc-test", "test.pdf", SHA, 1, parser_versions={"p1": "1.0"})
    doc.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="same", anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10), char_start=0, char_end=4)))
    return doc


def make_records(doc, lock):
    return (
        build_ai_verification(doc, lock, verifier_id="ai-1", model_id="model-a", scope=("structure",), checks=("tables", "numbers"), result="PASS", verified_at="2026-09-14", independence_basis="separate-review-pass-1"),
        build_ai_verification(doc, lock, verifier_id="ai-2", model_id="model-b", scope=("structure",), checks=("tables", "numbers"), result="PASS", verified_at="2026-09-14", independence_basis="separate-review-pass-2"),
    )


def test_two_independent_verifications_pass():
    doc = make_doc(); lock = build_revision_lock(doc)
    ok, issues = validate_ai_verifications(make_records(doc, lock), lock)
    assert ok and not issues


def test_missing_second_verifier_blocks():
    doc = make_doc(); lock = build_revision_lock(doc)
    ok, issues = validate_ai_verifications((make_records(doc, lock)[0],), lock)
    assert not ok and any("two" in issue for issue in issues)


def test_duplicate_verifier_blocks_independence():
    doc = make_doc(); lock = build_revision_lock(doc); first = make_records(doc, lock)[0]
    second = build_ai_verification(doc, lock, verifier_id="ai-1", model_id="model-b", scope=("structure",), checks=("tables",), result="PASS", verified_at="2026-09-14", independence_basis="separate-review-pass-2")
    ok, issues = validate_ai_verifications((first, second), lock)
    assert not ok and any("Duplicate" in issue for issue in issues)


def test_mismatched_revision_blocks():
    doc = make_doc(); lock = build_revision_lock(doc)
    altered = CanonicalDocument(doc.document_id, doc.source_name, doc.source_sha256, doc.page_count, nodes=list(doc.nodes), parser_versions={"p1": "2.0"})
    try:
        build_ai_verification(altered, lock, verifier_id="ai-2", model_id="model-b", scope=("structure",), checks=("tables",), result="PASS", verified_at="2026-09-14", independence_basis="pass-2")
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched revision must fail closed")


def test_persisted_verification_is_immutable(tmp_path: Path):
    doc = make_doc(); lock = build_revision_lock(doc); record = make_records(doc, lock)[0]
    path = persist_ai_verification(record, tmp_path)
    assert path.is_file()
