from pathlib import Path

from ndi import (
    GraphicalEvidenceItem,
    PageRegion,
    build_graphical_evidence,
    persist_graphical_evidence,
    validate_graphical_evidence_bundle,
)

SHA = "a" * 64


def item(kind="table", match=True):
    return GraphicalEvidenceItem(
        evidence_id="gv-001",
        source_hash=SHA,
        node_id="node-001",
        element_kind=kind,
        region=PageRegion(page=3, x0=10, y0=20, x1=200, y1=300),
        source_text="Table 1 — values",
        observed_text="Table 1 — values",
        match=match,
        verifier="AI-2",
        verified_at="2026-09-15T12:00:00Z",
    )


def test_graphical_evidence_bundle_records_page_region_and_passes():
    bundle = build_graphical_evidence(
        "doc",
        SHA,
        [item("table"), item("formula")],
        result="PASS",
        verifier="AI-2",
        verified_at="2026-09-15T12:00:00Z",
    )
    result = validate_graphical_evidence_bundle(bundle)
    assert result.status == "PASS"
    assert bundle.items[0].region.page == 3
    assert bundle.items[0].region.x1 == 200


def test_unmatched_visual_item_blocks():
    bundle = build_graphical_evidence(
        "doc", SHA, [item(match=False)], result="PASS", verifier="AI-2", verified_at="now"
    )
    result = validate_graphical_evidence_bundle(bundle)
    assert result.status == "FAIL"
    assert not result.checks["all_items_match"]


def test_source_hash_mismatch_blocks():
    first = item()
    other = GraphicalEvidenceItem(
        first.evidence_id, "b" * 64, first.node_id, first.element_kind, first.region,
        first.source_text, first.observed_text, True, first.verifier, first.verified_at
    )
    try:
        build_graphical_evidence("doc", SHA, [other], result="PASS", verifier="AI-2", verified_at="now")
    except ValueError as exc:
        assert "different source hash" in str(exc)
    else:
        raise AssertionError("Expected source hash mismatch to block")


def test_invalid_region_blocks():
    bad = PageRegion(page=0, x0=0, y0=0, x1=10, y1=10)
    first = item()
    bad_item = GraphicalEvidenceItem(
        first.evidence_id, SHA, first.node_id, first.element_kind, bad,
        first.source_text, first.observed_text, True, first.verifier, first.verified_at
    )
    try:
        build_graphical_evidence("doc", SHA, [bad_item], result="PASS", verifier="AI-2", verified_at="now")
    except ValueError as exc:
        assert "page must be positive" in str(exc)
    else:
        raise AssertionError("Expected invalid page to block")


def test_persistence_is_deterministic(tmp_path: Path):
    bundle = build_graphical_evidence(
        "doc", SHA, [item()], result="PASS", verifier="AI-2", verified_at="2026-09-15T12:00:00Z"
    )
    first = persist_graphical_evidence(bundle, tmp_path / "graphical-evidence.json")
    second = persist_graphical_evidence(bundle, tmp_path / "graphical-evidence-2.json")
    assert first == second
    assert (tmp_path / "graphical-evidence.json").read_text(encoding="utf-8") == (tmp_path / "graphical-evidence-2.json").read_text(encoding="utf-8")
