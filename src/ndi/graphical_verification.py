from __future__ import annotations

"""Validation of evidence that visually critical source content was checked."""

from dataclasses import dataclass
import re

from .verification import GateResult, GateStatus, GraphicalVerificationRecord


_REQUIRED_CHECK_TERMS = (
    "table",
    "formula",
    "numeric",
    "operator",
    "note",
    "numbering",
    "amendment",
)


def _valid_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{64}", value or ""))


@dataclass(frozen=True)
class GraphicalVerificationScope:
    """Minimum visually critical categories expected in a verification scope."""

    required_terms: tuple[str, ...] = _REQUIRED_CHECK_TERMS


def validate_graphical_verification(
    record: GraphicalVerificationRecord,
    *,
    scope: GraphicalVerificationScope | None = None,
) -> GateResult:
    """Fail closed unless graphical verification evidence is complete.

    A PASS record must identify the source, at least one checked page, a verifier,
    a verification timestamp, and checks covering the critical categories. A
    record with unresolved discrepancies cannot be accepted as PASS.
    """
    scope = scope or GraphicalVerificationScope()
    checks_text = " ".join(record.checks).lower()
    checks = {
        "source_hash_valid": _valid_sha256(record.source_hash),
        "pages_recorded": bool(record.checked_pages) and all(p > 0 for p in record.checked_pages),
        "checks_recorded": bool(record.checks),
        "verifier_recorded": bool(record.verifier) and record.verifier != "NOT_RECORDED",
        "timestamp_recorded": bool(record.verified_at) and record.verified_at != "NOT_RECORDED",
        "critical_categories_covered": all(term.lower() in checks_text for term in scope.required_terms),
        "result_pass": record.result == "PASS",
        "no_unresolved_discrepancies": not record.discrepancies,
    }
    issues: list[str] = []
    if not checks["source_hash_valid"]:
        issues.append("Graphical verification source SHA-256 is invalid.")
    if not checks["pages_recorded"]:
        issues.append("Graphical verification has no valid checked-page evidence.")
    if not checks["checks_recorded"]:
        issues.append("Graphical verification checks are not recorded.")
    if not checks["verifier_recorded"]:
        issues.append("Graphical verifier is not recorded.")
    if not checks["timestamp_recorded"]:
        issues.append("Graphical verification timestamp is not recorded.")
    if not checks["critical_categories_covered"]:
        missing = [term for term in scope.required_terms if term.lower() not in checks_text]
        issues.append("Missing critical graphical checks: " + ", ".join(missing) + ".")
    if not checks["result_pass"]:
        issues.append("Graphical verification result is not PASS.")
    if not checks["no_unresolved_discrepancies"]:
        issues.append("Graphical verification contains unresolved discrepancies.")
    return GateResult(
        "GRAPHICAL",
        GateStatus.PASS if all(checks.values()) else GateStatus.FAIL,
        checks,
        issues,
        ["graphical-verification.json"],
    )
