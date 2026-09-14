from ndi import (
    CanonicalDocument,
    DBNFixtureEvidence,
    EvidenceMode,
    build_dbn_fixture_evidence,
    dbn_structural_gate,
)
from ndi.reconciliation import ReconciliationDecision, ReconciliationReport

SHA = "a" * 64


def document():
    return CanonicalDocument("doc", "dbn.pdf", SHA, 105)


def clean_report():
    return ReconciliationReport(
        [ReconciliationDecision("n1", "AGREED", ("o1",), "agreement")]
    )


def evidence(mode=EvidenceMode.FRESH_EXECUTION, regression=True):
    return build_dbn_fixture_evidence(
        document(),
        source_size_bytes=23_532_218,
        mode=mode,
        parser_names=("docling", "markitdown", "opendataloader", "pypdf"),
        regression_verified=regression,
    )


def test_dbn_evidence_preserves_fresh_execution_mode():
    item = evidence()
    assert item.designation == "DBN V.2.5-56:2014"
    assert item.amendments == ("1", "2")
    assert item.mode == EvidenceMode.FRESH_EXECUTION
    assert item.page_count == 105


def test_historical_baseline_cannot_pass_fresh_gate():
    result = dbn_structural_gate(
        document(), clean_report(), evidence(EvidenceMode.HISTORICAL_BASELINE)
    )
    assert result.status == "FAIL"
    assert not result.checks["fresh_execution"]


def test_missing_regression_blocks_dbn_gate():
    result = dbn_structural_gate(
        document(), clean_report(), evidence(regression=False)
    )
    assert result.status == "FAIL"
    assert not result.checks["regression_verified"]


def test_source_hash_mismatch_blocks_gate():
    bad = DBNFixtureEvidence(
        "DBN V.2.5-56:2014",
        ("1", "2"),
        "b" * 64,
        23_532_218,
        105,
        EvidenceMode.FRESH_EXECUTION,
        ("pypdf",),
        True,
    )
    result = dbn_structural_gate(document(), clean_report(), bad)
    assert result.status == "FAIL"
    assert not result.checks["source_hash_matches"]
