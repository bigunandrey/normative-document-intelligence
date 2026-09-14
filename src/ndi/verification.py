from __future__ import annotations

"""Protocol-driven verification gates A-F."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import hashlib
import json
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

from .canonical import CanonicalDocument
from .matching import compare_documents, match_nodes
from .reconciliation import ReconciliationReport, reconcile_document
from .validator import Quality, audit_document

if TYPE_CHECKING:
    from .integrated_reconciliation import IntegratedReconciliationReport, ResolvedReconciliation


class GateStatus(StrEnum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"


@dataclass(frozen=True)
class GateResult:
    gate: str
    status: GateStatus
    checks: dict[str, bool]
    issues: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status in {GateStatus.PASS, GateStatus.PASS_WITH_WARNINGS}


@dataclass(frozen=True)
class RevisionRecord:
    revision_id: str
    document_id: str
    source_hash: str
    digital_revision: str
    reviewer_ai: str
    review_type: str
    review_date: str
    source_checked: bool
    source_urls: tuple[str, ...] = ()
    independent_sources: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()
    checks_performed: tuple[str, ...] = ()
    discrepancies: tuple[str, ...] = ()
    resolution_status: str = "NOT_RECORDED"
    result: str = "NOT_RECORDED"
    recommended_master_register_changes: tuple[str, ...] = ()
    handoff_tasks: tuple[str, ...] = ()
    previous_revision: str | None = None


@dataclass(frozen=True)
class GraphicalVerificationRecord:
    document_id: str
    source_hash: str
    checked_pages: tuple[int, ...]
    checks: tuple[str, ...]
    discrepancies: tuple[str, ...] = ()
    result: str = "NOT_RECORDED"
    verifier: str = "NOT_RECORDED"
    verified_at: str = "NOT_RECORDED"


@dataclass(frozen=True)
class ExternalCrossCheckRecord:
    document_id: str
    source_hash: str
    sources: tuple[str, ...]
    checks: tuple[str, ...]
    discrepancies: tuple[str, ...] = ()
    resolution_status: str = "NOT_RECORDED"
    result: str = "NOT_RECORDED"


@dataclass(frozen=True)
class AcceptanceEvidence:
    source_verified: bool = False
    structural_verified: bool = False
    reconciliation_verified: bool = False
    digital_representation_persisted: bool = False
    graphical_verification: bool = False
    external_cross_check: bool = False
    changes_deletions_verified: bool = False
    ai_verifications: int = 0
    regression_verified: bool = False
    master_registers_synchronized: bool = False
    revision_locked: bool = False

    def missing(self) -> list[str]:
        return [name for name, value in asdict(self).items() if value is False or value == 0]


def merge_parser_documents(documents: Iterable[CanonicalDocument]) -> CanonicalDocument:
    """Merge parser documents and preserve every unmatched parser node as a discrepancy."""
    docs = list(documents)
    if not docs:
        raise ValueError("At least one parser document is required")
    merged = docs[0]
    discrepancies: list[dict[str, object]] = []
    for other in docs[1:]:
        left_before = list(merged.nodes)
        pairs = match_nodes(merged, other)
        matched_left = {left_id for left_id, _ in pairs}
        matched_right = {right_id for _, right_id in pairs}
        other_parser = next(iter(other.parser_versions), "unknown")
        for left_id, right_id in pairs:
            target = merged.node(left_id)
            source = other.node(right_id)
            for observation in source.observations:
                target.add_observation(observation)
        for source in left_before:
            if source.node_id not in matched_left:
                discrepancies.append({"side": "left", "node_id": source.node_id, "parser": "merged"})
        for source in other.nodes:
            if source.node_id not in matched_right:
                discrepancies.append({"side": "right", "node_id": source.node_id, "parser": other_parser})
                merged.nodes.append(source)
        merged.parser_versions.update(other.parser_versions)
    merged.metadata["parser_merge_discrepancies"] = discrepancies
    return merged


def gate_a_observations(documents: Iterable[CanonicalDocument], *, required_parsers: set[str] | None = None) -> GateResult:
    docs = list(documents)
    issues: list[str] = []
    checks: dict[str, bool] = {"documents_present": bool(docs)}
    parsers = {o.parser for d in docs for n in d.nodes for o in n.observations}
    if required_parsers:
        missing = sorted(required_parsers - parsers)
        checks["required_parsers_present"] = not missing
        if missing:
            issues.append(f"Missing parser observations: {', '.join(missing)}")
    checks["observations_present"] = all(bool(n.observations) for d in docs for n in d.nodes) if docs else False
    checks["source_identity_present"] = all(bool(d.source_sha256) and len(d.source_sha256) == 64 for d in docs) if docs else False
    return GateResult("A", GateStatus.PASS if all(checks.values()) else GateStatus.FAIL, checks, issues)


def gate_b_reconciliation(document: CanonicalDocument) -> tuple[GateResult, ReconciliationReport]:
    report = reconcile_document(document)
    conflicts = len(report.conflicts)
    missing = sum(d.status == "MISSING_OBSERVATION" for d in report.decisions)
    unmatched = document.metadata.get("parser_merge_discrepancies", [])
    checks = {"reconciliation_executed": True, "no_conflicts": conflicts == 0, "no_missing_observations": missing == 0, "no_unmatched_parser_nodes": not unmatched}
    issues = [f"{conflicts} parser conflicts require review."] if conflicts else []
    if missing:
        issues.append(f"{missing} canonical nodes have missing observations.")
    if unmatched:
        issues.append(f"{len(unmatched)} parser nodes could not be matched and require review.")
    return GateResult("B", GateStatus.PASS if all(checks.values()) else GateStatus.FAIL, checks, issues, ["reconciliation-report.json"]), report


def gate_c_structural_acceptance(
    document: CanonicalDocument,
    reconciliation: ReconciliationReport,
    integrated_reconciliation: IntegratedReconciliationReport | ResolvedReconciliation | None = None,
) -> GateResult:
    """Close structural acceptance only when integrated reconciliation is resolved."""
    audit = audit_document(document)
    blocking = [d for d in reconciliation.decisions if d.status != "AGREED"]
    resolved = False
    if integrated_reconciliation is not None:
        resolved = integrated_reconciliation.accepted
    checks = {
        # Optional recognition evidence (bbox, character spans, confidence) may
        # be absent without blocking acceptance; structural/provenance errors
        # still produce Quality.FAIL and therefore block Gate C.
        "recognition_quality_pass": audit.passed,
        "reconciliation_clean": not blocking or resolved,
        "source_hash_valid": len(document.source_sha256) == 64,
    }
    issues = [f"Recognition quality: {audit.quality.value}"] if audit.quality != Quality.PASS else []
    if blocking and not resolved:
        issues.append(f"{len(blocking)} reconciliation decisions are not AGREED.")
    if integrated_reconciliation is not None:
        checks["integrated_reconciliation_resolved"] = resolved
        if not resolved:
            issues.append("Integrated reconciliation has unresolved parser or external evidence blockers.")
    return GateResult("C", GateStatus.PASS if all(checks.values()) else GateStatus.FAIL, checks, issues, ["structural-acceptance.json"])


def digital_revision(document: CanonicalDocument) -> str:
    return "sha256:" + hashlib.sha256(document.to_json().encode("utf-8")).hexdigest()


def persist_digital_representation(document: CanonicalDocument, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document.to_json() + "\n", encoding="utf-8")
    return digital_revision(document)


def gate_d_persistence(document: CanonicalDocument, output: Path) -> GateResult:
    revision = persist_digital_representation(document, output)
    checks = {"artifact_exists": output.is_file(), "source_hash_bound": document.source_sha256 in document.to_json(), "digital_revision_available": bool(revision)}
    return GateResult("D", GateStatus.PASS if all(checks.values()) else GateStatus.FAIL, checks, [], [str(output)])


def write_revision_record(record: RevisionRecord, root: Path) -> Path:
    directory = root / record.revision_id
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / "verification-record.json"
    path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def gate_e_revision_infrastructure(record: RevisionRecord, root: Path) -> GateResult:
    checks = {"revision_id_unique": not (root / record.revision_id).exists(), "source_hash_recorded": len(record.source_hash) == 64, "digital_revision_recorded": bool(record.digital_revision), "source_checked": record.source_checked, "reviewer_recorded": bool(record.reviewer_ai), "result_recorded": record.result != "NOT_RECORDED"}
    if not all(checks.values()):
        return GateResult("E", GateStatus.FAIL, checks, ["Revision evidence is incomplete or revision ID already exists."])
    path = write_revision_record(record, root)
    return GateResult("E", GateStatus.PASS, checks, [], [str(path)])


def gate_f_verification(graphical: GraphicalVerificationRecord, external: ExternalCrossCheckRecord) -> GateResult:
    graphical_ok = graphical.result == "PASS" and bool(graphical.checked_pages) and bool(graphical.checks)
    external_ok = external.result == "PASS" and bool(external.sources) and bool(external.checks)
    checks = {"graphical_verification": graphical_ok, "external_cross_check": external_ok}
    issues = []
    if not graphical_ok:
        issues.append("Graphical verification evidence is incomplete or not PASS.")
    if not external_ok:
        issues.append("External cross-check evidence is incomplete or not PASS.")
    return GateResult("F", GateStatus.PASS if all(checks.values()) else GateStatus.FAIL, checks, issues, ["graphical-verification.json", "external-cross-check.json"])


def final_acceptance(evidence: AcceptanceEvidence) -> GateResult:
    missing = evidence.missing()
    checks = {name: name not in missing for name in asdict(evidence)}
    if missing:
        return GateResult("FINAL", GateStatus.FAIL, checks, ["DIGITAL_ACCEPTED blocked: " + ", ".join(missing)])
    return GateResult("FINAL", GateStatus.PASS, checks, [], ["DIGITAL_ACCEPTED"])


def compare_parser_documents(left: CanonicalDocument, right: CanonicalDocument) -> GateResult:
    discrepancies = compare_documents(left, right)
    checks = {"comparison_executed": True, "no_discrepancies": not discrepancies}
    issues = [f"{len(discrepancies)} cross-parser discrepancies require review."] if discrepancies else []
    return GateResult("B-CROSS-PARSER", GateStatus.PASS if not discrepancies else GateStatus.FAIL, checks, issues, ["parser-comparison.json"])
