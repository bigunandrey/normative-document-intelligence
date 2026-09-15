from __future__ import annotations

"""Evidence-producing graphical verification contracts.

This module records exactly which source page/region was inspected and which
critical element was checked. It is intentionally viewer-neutral: a future UI
can render the page/region reference without changing the evidence contract.
"""

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .verification import GateResult, GateStatus


CRITICAL_ELEMENT_KINDS = frozenset(
    {
        "table",
        "formula",
        "operator",
        "numeric",
        "unit",
        "note",
        "footnote",
        "numbering",
        "amendment",
        "deletion",
    }
)


@dataclass(frozen=True)
class PageRegion:
    page: int
    x0: float = 0.0
    y0: float = 0.0
    x1: float = 0.0
    y1: float = 0.0

    def validate(self) -> None:
        if self.page <= 0:
            raise ValueError("Graphical evidence page must be positive")
        if min(self.x0, self.y0, self.x1, self.y1) < 0:
            raise ValueError("Graphical evidence coordinates cannot be negative")
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError("Graphical evidence region must have non-negative extent")


@dataclass(frozen=True)
class GraphicalEvidenceItem:
    evidence_id: str
    source_hash: str
    node_id: str
    element_kind: str
    region: PageRegion
    source_text: str
    observed_text: str
    match: bool
    verifier: str
    verified_at: str
    notes: str = ""

    def validate(self) -> None:
        if len(self.source_hash) != 64 or any(c not in "0123456789abcdefABCDEF" for c in self.source_hash):
            raise ValueError("Graphical evidence source SHA-256 is invalid")
        if not self.evidence_id.strip() or not self.node_id.strip():
            raise ValueError("Graphical evidence requires evidence_id and node_id")
        if self.element_kind.lower() not in CRITICAL_ELEMENT_KINDS:
            raise ValueError(f"Unsupported graphical critical element kind: {self.element_kind}")
        self.region.validate()
        if not self.source_text.strip() or not self.observed_text.strip():
            raise ValueError("Graphical evidence requires source and observed text")
        if not self.verifier.strip() or not self.verified_at.strip():
            raise ValueError("Graphical evidence requires verifier and timestamp")


@dataclass(frozen=True)
class GraphicalEvidenceBundle:
    document_id: str
    source_hash: str
    items: tuple[GraphicalEvidenceItem, ...] = ()
    result: str = "NOT_RECORDED"
    verifier: str = "NOT_RECORDED"
    verified_at: str = "NOT_RECORDED"
    discrepancies: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.document_id.strip():
            raise ValueError("Graphical evidence bundle requires document_id")
        if len(self.source_hash) != 64:
            raise ValueError("Graphical evidence bundle source SHA-256 is invalid")
        if not self.items:
            raise ValueError("Graphical evidence bundle requires at least one evidence item")
        for item in self.items:
            item.validate()
            if item.source_hash.lower() != self.source_hash.lower():
                raise ValueError(f"Evidence item {item.evidence_id} has a different source hash")
        if self.result == "PASS" and self.discrepancies:
            raise ValueError("PASS graphical evidence cannot contain unresolved discrepancies")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    def sha256(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def build_graphical_evidence(
    document_id: str,
    source_hash: str,
    items: Iterable[GraphicalEvidenceItem],
    *,
    result: str,
    verifier: str,
    verified_at: str,
    discrepancies: Iterable[str] = (),
    metadata: dict[str, str] | None = None,
) -> GraphicalEvidenceBundle:
    bundle = GraphicalEvidenceBundle(
        document_id=document_id,
        source_hash=source_hash,
        items=tuple(items),
        result=result,
        verifier=verifier,
        verified_at=verified_at,
        discrepancies=tuple(discrepancies),
        metadata=dict(metadata or {}),
    )
    bundle.validate()
    return bundle


def validate_graphical_evidence_bundle(bundle: GraphicalEvidenceBundle) -> GateResult:
    try:
        bundle.validate()
    except ValueError as exc:
        return GateResult("GRAPHICAL-EVIDENCE", GateStatus.FAIL, {"bundle_valid": False}, [str(exc)], ["graphical-evidence.json"])

    checks = {
        "bundle_valid": True,
        "all_items_match": all(item.match for item in bundle.items),
        "result_pass": bundle.result == "PASS",
        "no_unresolved_discrepancies": not bundle.discrepancies,
        "verifier_recorded": bundle.verifier != "NOT_RECORDED",
        "timestamp_recorded": bundle.verified_at != "NOT_RECORDED",
    }
    issues: list[str] = []
    if not checks["all_items_match"]:
        issues.append("At least one graphical evidence item does not match the source.")
    if not checks["result_pass"]:
        issues.append("Graphical evidence bundle result is not PASS.")
    if not checks["no_unresolved_discrepancies"]:
        issues.append("Graphical evidence bundle contains unresolved discrepancies.")
    return GateResult(
        "GRAPHICAL-EVIDENCE",
        GateStatus.PASS if all(checks.values()) else GateStatus.FAIL,
        checks,
        issues,
        ["graphical-evidence.json"],
    )


def persist_graphical_evidence(bundle: GraphicalEvidenceBundle, output: Path) -> str:
    bundle.validate()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(bundle.to_json(), encoding="utf-8")
    return bundle.sha256()
