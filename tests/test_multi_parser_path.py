import pytest

from ndi import RegisteredAdapter, adapt_all, default_adapters, from_records, parser_coverage
from ndi.adapter_contract import AdapterCapabilities

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
        page_count=1,
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


def _record_adapter(records):
    return RegisteredAdapter(
        "test",
        "1.0",
        AdapterCapabilities(),
        lambda source, *, source_name, source_sha256, page_count, version: from_records(
            source,
            source_name=source_name,
            source_sha256=source_sha256,
            page_count=page_count,
            parser="test",
            version=version,
        ),
    )


def test_adapter_output_contract_rejects_out_of_range_page_anchor():
    adapter = _record_adapter(None)
    with pytest.raises(ValueError, match="anchor page is outside document bounds"):
        adapter.adapt(
            [{"type": "paragraph", "text": "bad", "page": 2}],
            source_name="test.pdf",
            source_sha256=SHA,
            page_count=1,
        )


def test_adapter_output_contract_rejects_invalid_confidence():
    adapter = _record_adapter(None)
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        adapter.adapt(
            [{"type": "paragraph", "text": "bad", "confidence": 1.1}],
            source_name="test.pdf",
            source_sha256=SHA,
            page_count=1,
        )
