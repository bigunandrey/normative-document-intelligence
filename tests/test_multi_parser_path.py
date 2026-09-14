import pytest

from ndi import adapt_all, default_adapters, parser_coverage

SHA = "a" * 64


def test_adapt_all_executes_complete_configured_parser_set():
    adapters = default_adapters(
        markitdown_version="0.1",
        pypdf_version="5.0",
        docling_version="2.0",
        opendataloader_version="2.0",
    )
    result = adapt_all(
        {
            "markitdown": "# Title",
            "pypdf": ["Title"],
            "docling": [{"type": "heading", "text": "Title", "page": 1}],
            "opendataloader": [{"type": "heading", "text": "Title", "page": 1}],
        },
        source_name="test.pdf",
        source_sha256=SHA,
        adapters=adapters,
    )
    assert list(result) == ["markitdown", "pypdf", "docling", "opendataloader"]
    assert all(parser_coverage(document) for document in result.values())


def test_adapt_all_rejects_missing_parser_output():
    adapters = default_adapters()
    with pytest.raises(ValueError, match="Missing parser outputs"):
        adapt_all(
            {"markitdown": "# Title"},
            source_name="test.pdf",
            source_sha256=SHA,
            adapters=adapters,
        )
