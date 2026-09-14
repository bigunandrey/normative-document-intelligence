import hashlib

import pytest

from ndi import DocumentIdentity, SourceCandidate, SourceType, ValidatedSource
from ndi.external_retrieval import retrieve_validated, verify_retrieved_bytes
from ndi.source_registry import Compatibility
from ndi.external_sources import ExternalDocument


IDENTITY = DocumentIdentity("DBN V.2.5-56:2014", edition_year=2014, amendments=("1", "2"))


def source(content=b"pdf"):
    return ValidatedSource(
        SourceCandidate(
            "official", "Official", SourceType.OFFICIAL_WEB, IDENTITY,
            sha256=hashlib.sha256(content).hexdigest(),
            authority_verified=True, revision_verified=True,
            evidence=("authority", "revision"),
        ),
        Compatibility.SAME_REVISION,
        ("authority_verified", "revision_verified"),
    )


class Provider:
    name = "test-provider"

    def __init__(self, content):
        self.content = content

    def discover(self, identity):
        return ()

    def retrieve(self, validated):
        return ExternalDocument(validated, self.content)


def test_verify_retrieved_bytes_binds_sha256():
    result = verify_retrieved_bytes(source(b"pdf"), b"pdf")
    assert result.sha256 == hashlib.sha256(b"pdf").hexdigest()
    assert result.document.metadata["sha256"] == result.sha256


def test_verify_retrieved_bytes_rejects_hash_mismatch():
    with pytest.raises(ValueError, match="SHA-256"):
        verify_retrieved_bytes(source(b"pdf"), b"tampered")


def test_retrieve_validated_requires_same_revision_and_bytes():
    result = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    assert result.sha256 == hashlib.sha256(b"pdf").hexdigest()

    different = ValidatedSource(source().candidate, Compatibility.DIFFERENT_REVISION, ("checked",))
    with pytest.raises(ValueError, match="same-revision"):
        retrieve_validated(Provider(b"pdf"), different)

    class BadProvider(Provider):
        def retrieve(self, validated):
            return ExternalDocument(validated, "not-bytes")

    with pytest.raises(ValueError, match="byte content"):
        retrieve_validated(BadProvider(b"ignored"), source(b"pdf"))
