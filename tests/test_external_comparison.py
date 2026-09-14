import pytest

from ndi import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    DocumentIdentity,
    SourceCandidate,
    SourceType,
    ValidatedSource,
    compare_against_external,
)
from ndi.external_sources import DiscrepancyKind
from ndi.canonical import NodeType, SourceAnchor
from ndi.source_registry import Compatibility


SHA = "a" * 64
IDENTITY = DocumentIdentity("DBN V.2.5-56:2014", edition_year=2014, amendments=("1", "2"))


def source():
    return ValidatedSource(
        SourceCandidate("official", "Official", SourceType.OFFICIAL_WEB, IDENTITY, authority_verified=True, revision_verified=True, evidence=("authority", "revision")),
        Compatibility.SAME_REVISION,
        ("authority_verified", "revision_verified"),
    )


def document(text: str, *, page: int = 1):
    return CanonicalDocument(
        "doc-test", "test.pdf", SHA, 1,
        nodes=[CanonicalNode("n1", NodeType.PARAGRAPH, text=text, order=0, anchor=SourceAnchor(page=page))],
        parser_versions={"test": "1.0"},
    )


def test_external_comparison_detects_text_difference():
    result = compare_against_external(document("original"), document("external"), source())
    assert not result.passed
    assert result.discrepancies[0].kind == DiscrepancyKind.TEXT_MISMATCH
    assert result.discrepancies[0].source_ids == ("official",)


def test_external_comparison_detects_missing_observation():
    external = CanonicalDocument("doc-test", "test.pdf", SHA, 1, nodes=[], parser_versions={"test": "1.0"})
    result = compare_against_external(document("original"), external, source())
    assert any(item.kind == DiscrepancyKind.MISSING for item in result.discrepancies)


def test_external_comparison_requires_same_revision():
    different = ValidatedSource(source().candidate, Compatibility.DIFFERENT_REVISION, ("revision_checked",))
    with pytest.raises(ValueError, match="same-revision"):
        compare_against_external(document("original"), document("external"), different)
