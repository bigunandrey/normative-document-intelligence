from ndi import (
    BoundingBox,
    SourceAnchor,
    add_observation,
    from_records,
    observation_artifact_json,
    observation_artifact_sha256,
    observation_manifest,
)
from ndi.observations import RawObservation
from ndi.canonical import NodeType


SHA = "a" * 64


def test_observation_manifest_is_source_bound_and_complete():
    doc = from_records(
        [{"type": "paragraph", "text": "A", "page": 2, "confidence": 0.91}],
        source_name="test.pdf", source_sha256=SHA, page_count=4, parser="test", version="1.0",
    )
    manifest = observation_manifest(doc)
    assert manifest["source_sha256"] == SHA
    assert manifest["document_id"] == doc.document_id
    assert manifest["parser_versions"] == {"test": "1.0"}
    assert manifest["parser_coverage"] == {"test": 1}
    assert manifest["observation_count"] == 1
    assert manifest["observations"][0]["observation_id"].startswith("test:1.0:")


def test_observation_artifact_json_is_deterministic_and_hashable():
    doc = from_records(
        [{"type": "paragraph", "text": "A", "page": 1}],
        source_name="test.pdf", source_sha256=SHA, page_count=1, parser="test", version="1.0",
    )
    payload = observation_artifact_json(doc)
    assert payload == observation_artifact_json(doc)
    assert len(observation_artifact_sha256(doc)) == 64


def test_manifest_preserves_anchor_geometry_and_attributes():
    doc = from_records(
        [{"type": "paragraph", "text": "A", "provenance": {"page": 3, "bbox": {"left": 1, "top": 2, "right": 4, "bottom": 6}, "source_id": "x"}}],
        source_name="test.pdf", source_sha256=SHA, page_count=4, parser="test", version="1.0",
    )
    item = observation_manifest(doc)["observations"][0]
    assert item["anchor"]["page"] == 3
    assert item["anchor"]["bbox"]["left"] == 1.0
    assert item["attributes"]["provenance"]["source_id"] == "x"
