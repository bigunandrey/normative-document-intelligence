import pytest

from ndi import Compatibility, DocumentIdentity, SourceCandidate, SourceRecord, SourceRegistry, SourceType

SHA = "a" * 64


def identity(amendments=("Зміна №1", "Зміна №2")):
    return DocumentIdentity("ДБН В.2.5-56:2014", "Системи протипожежного захисту", 2014, amendments, issuing_organization="Мінрегіон")


def record():
    return SourceRecord("src-1", "user.pdf", SourceType.USER_SUPPLIED, SHA, "2026-09-14T00:00:00Z", identity())


def test_source_record_requires_valid_sha256():
    with pytest.raises(ValueError):
        SourceRecord("src", "x.pdf", SourceType.USER_SUPPLIED, "bad", "now", identity())


def test_registry_rejects_duplicate_source_id():
    registry = SourceRegistry().register(record())
    with pytest.raises(ValueError):
        registry.register(record())


def test_unverified_candidate_cannot_match():
    candidate = SourceCandidate("ext", "official.pdf", SourceType.OFFICIAL_WEB, identity(), authority_verified=False, revision_verified=True)
    assert candidate.compatibility_with(record()) == Compatibility.UNVERIFIED


def test_same_revision_requires_authority_and_revision_evidence():
    candidate = SourceCandidate("ext", "official.pdf", SourceType.OFFICIAL_WEB, identity(), sha256=SHA, authority_verified=True, revision_verified=True)
    assert candidate.compatibility_with(record()) == Compatibility.SAME_REVISION


def test_different_revision_is_explicit():
    candidate = SourceCandidate("ext", "official.pdf", SourceType.OFFICIAL_WEB, DocumentIdentity("ДБН В.2.5-56:2014", edition_year=2014, amendments=("Зміна №1",)), authority_verified=True, revision_verified=True)
    assert candidate.compatibility_with(record()) == Compatibility.DIFFERENT_REVISION
