from __future__ import annotations

"""Fail-closed DBN end-to-end structural gate and evidence manifest."""

from dataclasses import asdict, dataclass
from enum import StrEnum
import json
from pathlib import Path

from .canonical import CanonicalDocument
from .reconciliation import ReconciliationReport
from .verification import GateResult, GateStatus, gate_c_structural_acceptance


class EvidenceMode(StrEnum):
    FRESH_EXECUTION = "FRESH_EXECUTION"
    HISTORICAL_BASELINE = "HISTORICAL_BASELINE"


@dataclass(frozen=True)
class DBNFixtureEvidence:
    designation: str
    amendments: tuple[str, ...]
    source_sha256: str
    size_bytes: int
    page_count: int
    mode: EvidenceMode
    parser_names: tuple[str, ...]
    regression_verified: bool
    notes: tuple[str, ...] = ()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build_dbn_fixture_evidence(
    document: CanonicalDocument,
    *,
    source_size_bytes: int,
    mode: EvidenceMode,
    parser_names: tuple[str, ...],
    regression_verified: bool,
    notes: tuple[str, ...] = (),
) -> DBNFixtureEvidence:
    if not document.source_sha256 or len(document.source_sha256) != 64:
        raise ValueError("DBN fixture evidence requires a valid source SHA-256")
    if document.page_count is None or document.page_count <= 0:
        raise ValueError("DBN fixture evidence requires a positive page count")
    if source_size_bytes <= 0:
        raise ValueError("DBN fixture evidence requires positive source size")
    if not parser_names:
        raise ValueError("DBN fixture evidence requires parser provenance")
    return DBNFixtureEvidence(
        designation="DBN V.2.5-56:2014",
        amendments=("1", "2"),
        source_sha256=document.source_sha256,
        size_bytes=source_size_bytes,
        page_count=document.page_count,
        mode=mode,
        parser_names=tuple(sorted(parser_names)),
        regression_verified=regression_verified,
        notes=notes,
    )


def write_dbn_fixture_evidence(evidence: DBNFixtureEvidence, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(evidence.to_json(), encoding="utf-8")
    return output


def dbn_structural_gate(
    document: CanonicalDocument,
    reconciliation: ReconciliationReport,
    evidence: DBNFixtureEvidence,
) -> GateResult:
    if evidence.source_sha256 != document.source_sha256:
        return GateResult(
            "DBN",
            GateStatus.FAIL,
            {"source_hash_matches": False},
            ["Fixture evidence source SHA-256 does not match canonical document."],
        )
    if evidence.page_count != document.page_count:
        return GateResult(
            "DBN",
            GateStatus.FAIL,
            {"page_count_matches": False},
            ["Fixture evidence page count does not match canonical document."],
        )
    if evidence.mode == EvidenceMode.HISTORICAL_BASELINE:
        return GateResult(
            "DBN",
            GateStatus.FAIL,
            {"fresh_execution": False},
            ["Historical baseline cannot satisfy the fresh DBN end-to-end gate."],
        )
    if not evidence.regression_verified:
        return GateResult(
            "DBN",
            GateStatus.FAIL,
            {"regression_verified": False},
            ["DBN regression evidence is missing."],
        )
    result = gate_c_structural_acceptance(document, reconciliation)
    checks = dict(result.checks)
    checks.update(
        {
            "fresh_execution": True,
            "fixture_identity": True,
            "page_count": True,
            "regression_verified": True,
        }
    )
    return GateResult(
        "DBN",
        result.status,
        checks,
        result.issues,
        result.artifacts + ["dbn-fixture-evidence.json"],
    )
