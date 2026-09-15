from __future__ import annotations

"""Fail-closed acceptance checks for downstream normative semantics."""

from typing import Iterable

from .amendment_semantics import AmendmentAction
from .canonical import CanonicalDocument
from .dependency_resolution import SemanticDependencyResolution
from .normative_semantics import NormativeUnit, SemanticDependencyGraph, SemanticEvaluation
from .revision_lock import RevisionLock
from .semantic_provenance import validate_semantic_provenance


def _node_identifiers(node: object) -> set[str]:
    identifiers = {node.node_id}
    for key in ("reference_id", "clause_id", "section_id", "identifier", "designation", "number", "label"):
        value = node.attributes.get(key)
        if value is None:
            continue
        raw = value if isinstance(value, (list, tuple, set)) else (value,)
        identifiers.update(str(item).strip() for item in raw if str(item).strip())
    return identifiers


def _target_matches(document: CanonicalDocument, target: str) -> tuple[str, ...]:
    value = target.strip()
    candidates = {value}
    if ":" in value:
        _prefix, suffix = value.split(":", 1)
        if suffix.strip():
            candidates.add(suffix.strip())
    return tuple(sorted(node.node_id for node in document.nodes if _node_identifiers(node) & candidates))


def validate_semantic_fail_closed(
    document: CanonicalDocument,
    lock: RevisionLock,
    *,
    units: Iterable[NormativeUnit] = (),
    evaluations: Iterable[SemanticEvaluation] = (),
    dependency_graph: SemanticDependencyGraph | None = None,
    dependency_resolutions: Iterable[SemanticDependencyResolution] = (),
    amendments: Iterable[AmendmentAction] = (),
) -> tuple[bool, list[str]]:
    """Reject unresolved semantic states before downstream execution/acceptance.

    This is deliberately conservative: unresolved or ambiguous dependency targets,
    amendment targets, unknown evaluation states, and invalid normative modalities
    are never auto-resolved.
    """
    units = tuple(units)
    evaluations = tuple(evaluations)
    dependency_resolutions = tuple(dependency_resolutions)
    amendments = tuple(amendments)
    issues: list[str] = []
    provenance_ok, provenance_issues = validate_semantic_provenance(
        document, lock, units=units, dependency_graph=dependency_graph,
        dependency_resolutions=dependency_resolutions, evaluations=evaluations,
        amendments=amendments,
    )
    if not provenance_ok:
        issues.extend(provenance_issues)

    allowed_modalities = {"REQUIREMENT", "PROHIBITION", "RECOMMENDATION", "PERMISSION"}
    unit_ids = {unit.unit_id for unit in units}
    for unit in units:
        if unit.modality not in allowed_modalities:
            issues.append(f"Normative unit {unit.unit_id} has unresolved semantic modality")
        if not unit.operator or not unit.predicate:
            issues.append(f"Normative unit {unit.unit_id} has unresolved semantic interpretation")
        if unit.applicability and not unit.subject_type:
            issues.append(f"Normative unit {unit.unit_id} has unresolved applicability type")

    for evaluation in evaluations:
        if evaluation.unit_id not in unit_ids:
            issues.append(f"Evaluation {evaluation.evaluation_id} references unknown normative unit")
        if evaluation.result == "UNRESOLVED" or evaluation.applicability_state == "UNKNOWN" or evaluation.condition_state == "UNKNOWN":
            issues.append(f"Evaluation {evaluation.evaluation_id} is unresolved")
        elif evaluation.result not in {"REQUIREMENT_ACTIVE", "PROHIBITION_ACTIVE", "RECOMMENDATION_ACTIVE", "PERMISSION_ACTIVE", "NOT_APPLICABLE", "INACTIVE"}:
            issues.append(f"Evaluation {evaluation.evaluation_id} has unresolved result state")

    if dependency_graph is not None:
        if not dependency_resolutions and dependency_graph.dependencies:
            issues.append("Dependency graph has dependencies but no resolutions")
        for resolution in dependency_resolutions:
            if resolution.status != "RESOLVED":
                issues.append(f"Dependency target is not resolved: {resolution.target}")

    for amendment in amendments:
        matches = _target_matches(document, amendment.target)
        if len(matches) == 0:
            issues.append(f"Amendment target is unresolved: {amendment.target}")
        elif len(matches) > 1:
            issues.append(f"Amendment target is ambiguous: {amendment.target}")
        if amendment.action not in {"ADD", "REPLACE", "DELETE"}:
            issues.append(f"Amendment {amendment.action_id} has unresolved action")
        if amendment.action == "REPLACE" and not amendment.replacement_text:
            issues.append(f"Amendment {amendment.action_id} has unresolved replacement text")

    return not issues, issues
