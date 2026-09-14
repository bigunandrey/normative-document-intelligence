import pytest

from ndi import (
    Compatibility,
    DocumentIdentity,
    DiscrepancyEvidence,
    DiscrepancyKind,
    DiscoveryStatus,
    ExternalSourceProvider,
    SourceCandidate,
    SourceType,
    discover_validated,
    validate_candidate,
)


IDENTITY = DocumentIdentity(
    designation="DBN V.2.5-56:2014",
    title="Fire protection systems",
    edition_year=2014,
    amendments=("1", "2"),
    issuing_organization="Ministry of Regional Development",
)


def candidate(**overrides):
    values = dict(
        source_id="official-1",
        source_name="Official source",
        source_type=SourceType.OFFICIAL_WEB,
        identity=IDENTITY,
        source_url="https://example.invalid/dbn.pdf",
        authority_verified=True,
        revision_verified=True,
        evidence=("publisher_record", "revision_notice"),
    )
    values.update(overrides)
    return SourceCandidate(**values)


class Provider:
    name = "test-provider"

    def __init__(self, candidates):
        self.candidates = candidates

    def discover(self, identity):
        assert identity == IDENTITY
        return self.candidates

    def retrieve(self, source):
        raise NotImplementedError


def test_validate_candidate_requires_same_revision_evidence():
    result = validate_candidate(IDENTITY, candidate())
    assert result.compatibility == Compatibility.SAME_REVISION
    assert "authority_verified" in result.validation_evidence
    assert "revision_verified" in result.validation_evidence


def test_discovery_returns_only_validated_same_revision_matches():
    result = discover_validated(IDENTITY, [Provider([
        candidate(source_id="same"),
        candidate(
            source_id="different",
            identity=DocumentIdentity(
                designation="DBN V.2.5-56:2014",
                title="Fire protection systems",
                edition_year=2014,
                amendments=("1",),
            ),
        ),
    ])])
    assert result.status == DiscoveryStatus.MATCHED
    assert [item.candidate.source_id for item in result.sources] == ["same"]
    assert any("different" in reason for reason in result.reasons)


def test_discovery_is_fail_closed_when_no_authoritative_match_exists():
    result = discover_validated(IDENTITY, [Provider([
        candidate(authority_verified=False, evidence=()),
    ])])
    assert result.status == DiscoveryStatus.NO_MATCH
    assert not result.sources
    assert result.reasons


def test_invalid_candidate_cannot_become_validated_source():
    with pytest.raises(ValueError, match="invalid"):
        validate_candidate(
            IDENTITY,
            candidate(
                identity=DocumentIdentity(designation="OTHER", title="Other"),
                authority_verified=False,
                revision_verified=False,
                evidence=("untrusted",),
            ),
        )


def test_discrepancy_evidence_requires_source_provenance_and_evidence():
    with pytest.raises(ValueError, match="source provenance"):
        DiscrepancyEvidence(DiscrepancyKind.MISSING, "Missing clause", (), evidence=("x",))
    with pytest.raises(ValueError, match="explicit evidence"):
        DiscrepancyEvidence(DiscrepancyKind.MISSING, "Missing clause", ("official-1",))
