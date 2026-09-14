from ndi import GraphicalVerificationRecord, validate_graphical_verification

SHA = "a" * 64


def valid_record():
    return GraphicalVerificationRecord(
        document_id="doc",
        source_hash=SHA,
        checked_pages=(1, 2, 3),
        checks=(
            "table structure and merged cells",
            "formula and numeric values",
            "normative operator symbols",
            "notes and footnotes",
            "numbering and page order",
            "amendment and deletion markers",
        ),
        result="PASS",
        verifier="AI-2",
        verified_at="2026-09-14T19:00:00Z",
    )


def test_complete_graphical_evidence_passes():
    result = validate_graphical_verification(valid_record())
    assert result.status == "PASS"
    assert all(result.checks.values())


def test_missing_critical_graphical_category_blocks():
    record = valid_record()
    record = GraphicalVerificationRecord(
        record.document_id,
        record.source_hash,
        record.checked_pages,
        tuple(c for c in record.checks if "formula" not in c),
        result=record.result,
        verifier=record.verifier,
        verified_at=record.verified_at,
    )
    result = validate_graphical_verification(record)
    assert result.status == "FAIL"
    assert not result.checks["critical_categories_covered"]


def test_unresolved_discrepancy_blocks_pass():
    record = valid_record()
    record = GraphicalVerificationRecord(
        record.document_id,
        record.source_hash,
        record.checked_pages,
        record.checks,
        discrepancies=("page 2 table value differs",),
        result="PASS",
        verifier=record.verifier,
        verified_at=record.verified_at,
    )
    result = validate_graphical_verification(record)
    assert result.status == "FAIL"
    assert not result.checks["no_unresolved_discrepancies"]


def test_invalid_source_hash_blocks():
    record = valid_record()
    record = GraphicalVerificationRecord(
        record.document_id,
        "invalid",
        record.checked_pages,
        record.checks,
        result=record.result,
        verifier=record.verifier,
        verified_at=record.verified_at,
    )
    result = validate_graphical_verification(record)
    assert result.status == "FAIL"
    assert not result.checks["source_hash_valid"]
