from __future__ import annotations

"""Fail-closed provenance validation for downstream semantic artifacts."""

from typing import Iterable

from .amendment_semantics import AmendmentAction
from .canonical import CanonicalDocument
from .dependency_resolution import SemanticDependencyResolution
from .normative_semantics import (
    ApplicabilityLink,
    NormativeUnit,
    RuleRegistryEntry,
    SemanticDependencyGraph,
    SemanticEvaluation,
)
from .revision_lock import RevisionLock


def validate_semantic_provenance(
    document: CanonicalDocument,
    lock: RevisionLock,
    *,
    units: Iterable[NormativeUnit] = (),
    applicability_links: Iterable[ApplicabilityLink] = (),
    rule_entries: Iterable[RuleRegistryEntry] = (),
    dependency_graph: SemanticDependencyGraph | None = None,
    dependency_resolutions: Iterable[SemanticDependencyResolution] = (),
    evaluations: Iterable[SemanticEvaluation] = (),
    amendments: Iterable[AmendmentAction] = (),
) -> tuple[bool, list[str]]:
    """Validate that every supplied semantic artifact remains traceable to the lock and canonical nodes.

    The validator never infers missing provenance. Any missing node, page anchor,
    source hash, revision, or source-text binding is an error.
    """
    issues: list[str] = []
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256:
        issues.append("Canonical document is not bound to the locked source")
    nodes = {node.node_id: node for node in document.nodes}
    unit_map = {unit.unit_id: unit for unit in units}
    for unit in unit_map.values():
        if (unit.document_id, unit.source_sha256, unit.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Normative unit {unit.unit_id} is not bound to the locked revision")
            continue
        node = nodes.get(unit.node_id)
        if node is None:
            issues.append(f"Normative unit {unit.unit_id} references unknown node {unit.node_id}")
            continue
        page = node.anchor.page if node.anchor else None
        if unit.anchor_page != page:
            issues.append(f"Normative unit {unit.unit_id} has an invalid source page")
        if unit.source_text != " ".join(node.text.split()):
            issues.append(f"Normative unit {unit.unit_id} source text does not match canonical node")

    for link in applicability_links:
        if (link.document_id, link.source_sha256, link.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Applicability link {link.link_id} is not bound to the locked revision")
        unit = unit_map.get(link.unit_id)
        node = nodes.get(link.source_node_id)
        if unit is None:
            issues.append(f"Applicability link {link.link_id} references unknown unit")
        elif link.source_node_id != unit.node_id or link.anchor_page != unit.anchor_page:
            issues.append(f"Applicability link {link.link_id} is not traceable to its normative unit")
        if node is None:
            issues.append(f"Applicability link {link.link_id} references unknown source node")
        elif link.anchor_page != (node.anchor.page if node.anchor else None):
            issues.append(f"Applicability link {link.link_id} has an invalid source anchor")

    for entry in rule_entries:
        if (entry.document_id, entry.source_sha256, entry.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Rule {entry.rule_id} is not bound to the locked revision")
        node = nodes.get(entry.node_id)
        if node is None:
            issues.append(f"Rule {entry.rule_id} references unknown source node")
            continue
        if entry.anchor_page != (node.anchor.page if node.anchor else None):
            issues.append(f"Rule {entry.rule_id} has an invalid source anchor")
        canonical_text = " ".join(node.text.split())
        if entry.source_text != canonical_text or entry.expression != canonical_text:
            issues.append(f"Rule {entry.rule_id} is not traceable to canonical source text")

    dependency_map = {dep.dependency_id: dep for dep in dependency_graph.dependencies} if dependency_graph is not None else {}
    if dependency_graph is not None and (
        dependency_graph.document_id,
        dependency_graph.source_sha256,
        dependency_graph.digital_revision,
    ) != (lock.document_id, lock.source_sha256, lock.digital_revision):
        issues.append("Dependency graph is not bound to the locked revision")
    for dep in dependency_map.values():
        if (dep.document_id, dep.source_sha256, dep.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Dependency {dep.dependency_id} is not bound to the locked revision")
        unit = unit_map.get(dep.source_unit_id)
        node = nodes.get(dep.source_node_id)
        if unit is None:
            issues.append(f"Dependency {dep.dependency_id} references unknown source unit")
        elif dep.source_node_id != unit.node_id or dep.anchor_page != unit.anchor_page or dep.evidence_text != unit.source_text:
            issues.append(f"Dependency {dep.dependency_id} is not traceable to its normative unit")
        if node is None:
            issues.append(f"Dependency {dep.dependency_id} references unknown source node")
        elif dep.anchor_page != (node.anchor.page if node.anchor else None):
            issues.append(f"Dependency {dep.dependency_id} has an invalid source anchor")

    for resolution in dependency_resolutions:
        if (resolution.document_id, resolution.source_sha256, resolution.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Resolution {resolution.resolution_id} is not bound to the locked revision")
        dep = dependency_map.get(resolution.dependency_id)
        node = nodes.get(resolution.source_node_id)
        if dep is None:
            issues.append(f"Resolution {resolution.resolution_id} references unknown dependency")
        elif resolution.source_node_id != dep.source_node_id or resolution.anchor_page != dep.anchor_page or resolution.target != dep.target:
            issues.append(f"Resolution {resolution.resolution_id} is not traceable to its dependency")
        if node is None:
            issues.append(f"Resolution {resolution.resolution_id} references unknown source node")
        elif resolution.anchor_page != (node.anchor.page if node.anchor else None):
            issues.append(f"Resolution {resolution.resolution_id} has an invalid source anchor")
        for target_node_id in resolution.target_node_ids:
            if target_node_id not in nodes:
                issues.append(f"Resolution {resolution.resolution_id} references unknown target node {target_node_id}")

    for evaluation in evaluations:
        if (evaluation.document_id, evaluation.source_sha256, evaluation.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Evaluation {evaluation.evaluation_id} is not bound to the locked revision")
        if evaluation.unit_id not in unit_map:
            issues.append(f"Evaluation {evaluation.evaluation_id} references unknown normative unit")

    for amendment in amendments:
        if (amendment.document_id, amendment.source_sha256, amendment.digital_revision) != (lock.document_id, lock.source_sha256, lock.digital_revision):
            issues.append(f"Amendment {amendment.action_id} is not bound to the locked revision")
        node = nodes.get(amendment.source_node_id)
        if node is None:
            issues.append(f"Amendment {amendment.action_id} references unknown source node")
            continue
        if amendment.anchor_page != (node.anchor.page if node.anchor else None):
            issues.append(f"Amendment {amendment.action_id} has an invalid source anchor")
        if amendment.source_text != " ".join(node.text.split()):
            issues.append(f"Amendment {amendment.action_id} source text does not match canonical node")

    return not issues, issues
