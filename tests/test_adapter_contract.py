import pytest

from ndi import AdapterCapabilities, validate_adapter_capabilities


class Adapter:
    def __init__(self, name, version="1"):
        self.name = name
        self.version = version
        self.capabilities = AdapterCapabilities(paragraphs=True)


def test_adapter_capability_registry_is_deterministic():
    result = validate_adapter_capabilities([Adapter("pypdf"), Adapter("markitdown")])
    assert list(result) == ["pypdf", "markitdown"]
    assert result["pypdf"].paragraphs


def test_duplicate_adapter_names_are_rejected():
    with pytest.raises(ValueError, match="Duplicate parser adapter"):
        validate_adapter_capabilities([Adapter("pypdf"), Adapter("pypdf")])


def test_adapter_identity_is_required():
    with pytest.raises(ValueError, match="name and version"):
        validate_adapter_capabilities([Adapter("")])
