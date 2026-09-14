import pytest

from ndi import ingest_parser_outputs

SHA = "a" * 64


def outputs():
    return {
        "markitdown": "# Title\n\nBody",
        "pypdf": ["Title\nBody"],
        "docling": [{"type": "heading", "text": "Title", "page": 1}],
        "opendataloader": [{"type": "heading", "text": "Title", "page": 1}],
    }


def test_ingestion_produces_one_source_bound_artifact_per_parser():
    package = ingest_parser_outputs(outputs(), source_name="test.pdf", source_sha256=SHA, page_count=1)
    assert package.source_sha256 == SHA
    assert package.parser_names == ("markitdown", "pypdf", "docling", "opendataloader")
    assert all(item.document.source_sha256 == SHA for item in package.parsers)
    assert all(item.manifest_json and len(item.sha256) == 64 for item in package.parsers)


def test_ingestion_is_deterministic():
    first = ingest_parser_outputs(outputs(), source_name="test.pdf", source_sha256=SHA, page_count=1)
    second = ingest_parser_outputs(outputs(), source_name="test.pdf", source_sha256=SHA, page_count=1)
    assert [item.sha256 for item in first.parsers] == [item.sha256 for item in second.parsers]
    assert [item.manifest_json for item in first.parsers] == [item.manifest_json for item in second.parsers]


def test_ingestion_fails_closed_for_incomplete_parser_set():
    data = outputs()
    del data["docling"]
    with pytest.raises(ValueError, match="Missing parser outputs"):
        ingest_parser_outputs(data, source_name="test.pdf", source_sha256=SHA)
