import hashlib

import pytest

from ndi import CanonicalDocument, CanonicalNode, DocumentIdentity, NodeType, SourceAnchor, SourceCandidate, SourceType, ValidatedSource
from ndi.external_comparison import compare_observation_set
from ndi.external_pipeline import run_external_cross_check
from ndi.external_retrieval import retrieve_validated, verify_retrieved_bytes
from ndi.external_parsing import aggregate_external_observations, parse_retrieved_external
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
        return (source(self.content).candidate,)

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


class Parser:
    name = "independent"
    version = "1.0"

    def parse(self, content, *, source_name, source_sha256):
        return CanonicalDocument(
            "external-test", source_name, source_sha256, 1, [], {self.name: self.version}
        )


def test_independent_external_parser_is_source_bound():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    result = parse_retrieved_external(retrieved, (Parser(),))
    assert len(result) == 1
    assert result[0].source_sha256 == retrieved.sha256
    assert result[0].document.source_sha256 == retrieved.sha256


def test_independent_external_parser_fails_closed_on_duplicate_identity():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    with pytest.raises(ValueError, match="Duplicate"):
        parse_retrieved_external(retrieved, (Parser(), Parser()))


def test_independent_external_parser_rejects_wrong_source_hash():
    class BadParser(Parser):
        def parse(self, content, *, source_name, source_sha256):
            return CanonicalDocument("external-test", source_name, "0" * 64, 1, [], {self.name: self.version})

    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    with pytest.raises(ValueError, match="another source"):
        parse_retrieved_external(retrieved, (BadParser(),))


def _parser_with_node(name, text):
    class ParserWithNode(Parser):
        pass

    ParserWithNode.name = name

    def parse(self, content, *, source_name, source_sha256):
        document = CanonicalDocument("external-test", source_name, source_sha256, 1, [], {self.name: self.version})
        document.add_node(CanonicalNode("n1", NodeType.PARAGRAPH, text, order=0, anchor=SourceAnchor(page=1)))
        return document

    ParserWithNode.parse = parse
    return ParserWithNode()


def test_external_observations_aggregate_deterministically():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    observations = parse_retrieved_external(retrieved, (_parser_with_node("b", "same"), _parser_with_node("a", "same")))
    result = aggregate_external_observations(retrieved.document, observations)
    assert [(item.parser, item.parser_version) for item in result.parser_observations] == [("a", "1.0"), ("b", "1.0")]
    assert result.canonical_document is result.parser_observations[0].document


def test_external_observations_fail_closed_on_parser_disagreement():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    observations = parse_retrieved_external(retrieved, (_parser_with_node("a", "same"), _parser_with_node("b", "different")))
    with pytest.raises(ValueError, match="disagreement"):
        aggregate_external_observations(retrieved.document, observations)


def test_external_observations_reject_wrong_retrieved_sha_metadata():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    observations = parse_retrieved_external(retrieved, (Parser(),))
    tampered_document = ExternalDocument(retrieved.document.source, retrieved.document.content, {"sha256": "0" * 64})
    with pytest.raises(ValueError, match="retrieved source SHA-256"):
        aggregate_external_observations(tampered_document, observations)


def test_aggregated_external_observations_feed_comparison_engine():
    retrieved = retrieve_validated(Provider(b"pdf"), source(b"pdf"))
    observations = parse_retrieved_external(retrieved, (_parser_with_node("a", "same"), _parser_with_node("b", "same")))
    aggregated = aggregate_external_observations(retrieved.document, observations)
    supplied = aggregated.canonical_document
    result = compare_observation_set(supplied, aggregated)
    assert result.passed
    assert result.source.candidate.source_id == "official"


def test_external_pipeline_executes_provider_to_comparison():
    supplied = CanonicalDocument("external-test", "Official", source(b"pdf").candidate.sha256, 1, [], {"supplied": "1.0"})
    results = run_external_cross_check(supplied, IDENTITY, (Provider(b"pdf"),), (Parser(),))
    assert len(results) == 1
    assert results[0].comparison.passed


def test_external_pipeline_deduplicates_sources_deterministically():
    supplied = CanonicalDocument("external-test", "Official", source(b"pdf").candidate.sha256, 1, [], {"supplied": "1.0"})
    results = run_external_cross_check(supplied, IDENTITY, (Provider(b"pdf"), Provider(b"pdf")), (Parser(),))
    assert len(results) == 1


def test_external_pipeline_is_fail_closed_on_parser_disagreement():
    supplied = CanonicalDocument("external-test", "Official", source(b"pdf").candidate.sha256, 1, [], {"supplied": "1.0"})
    with pytest.raises(ValueError, match="disagreement"):
        run_external_cross_check(
            supplied,
            IDENTITY,
            (Provider(b"pdf"),),
            (_parser_with_node("a", "same"), _parser_with_node("b", "different")),
        )
