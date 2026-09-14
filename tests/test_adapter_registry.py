from ndi import (
    AdapterCapabilities,
    adapt_registered,
    default_adapters,
    parser_coverage,
    validate_default_adapters,
)


SHA = "a" * 64


def test_default_adapter_set_is_stable_and_complete():
    adapters = default_adapters(
        markitdown_version="0.1",
        pypdf_version="5.0",
        docling_version="2.0",
        opendataloader_version="2.0",
    )
    assert [adapter.name for adapter in adapters] == [
        "markitdown", "pypdf", "docling", "opendataloader"
    ]
    manifest = validate_default_adapters(adapters)
    assert set(manifest) == {"markitdown", "pypdf", "docling", "opendataloader"}
    assert isinstance(manifest["docling"], AdapterCapabilities)


def test_registered_markitdown_adapter_preserves_evidence():
    adapter = default_adapters(markitdown_version="0.1")[0]
    doc = adapt_registered(
        adapter,
        "# Section\n\nBody",
        source_name="test.pdf",
        source_sha256=SHA,
        page_count=1,
    )
    assert parser_coverage(doc) == {"markitdown": 2}
    assert doc.parser_versions == {"markitdown": "0.1"}
    assert all(node.observations for node in doc.nodes)


def test_registered_pypdf_adapter_preserves_page_boundaries():
    adapter = default_adapters(pypdf_version="5.0")[1]
    doc = adapt_registered(
        adapter,
        ["Page one", "Page two"],
        source_name="test.pdf",
        source_sha256=SHA,
    )
    assert doc.page_count == 2
    assert [node.anchor.page for node in doc.nodes] == [1, 1, 2, 2]
    assert doc.parser_versions == {"pypdf": "5.0"}
