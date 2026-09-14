from __future__ import annotations

"""Deterministic resolution of explicit semantic dependencies against the canonical document graph."""

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

from .canonical import CanonicalDocument
from .normative_semantics import SemanticDependency, SemanticDependencyGraph
from .revision_lock import RevisionLock


@dataclass(frozen=True)
class SemanticDependencyResolution:
    resolution_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    dependency_id: str
    target: str
    status: str
    target_node_ids: tuple[str, ...]
    source_node_id: str
    anchor_page: int | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalized_target_values(target: str) -> set[str]:
    value = target.strip()
    values = {value}
    if ":" in value:
        prefix, suffix = value.split(":", 1)
        if prefix.strip() and suffix.strip():
            values.add(suffix.strip())
    return values


def _node_identifiers(node: Any) -> set[str]:
    identifiers = {node.node_id}
    for key in ("reference_id", "clause_id", "section_id", "identifier", "designation", "number", "label"):
        value = node.attributes.get(key)
        if value is None:
            continue
        raw = value if isinstance(value, (list, tuple, set)) else (value,)
        identifiers.update(str(item).strip() for item in raw if str(item).strip())
    return identifiers


def _resolution_id(dependency: SemanticDependency, status: str, target_node_ids: tuple[str, ...], reason: str) -> str:
    payload = f"{dependency.dependency_id}|{status}|{'|'.join(target_node_ids)}|{reason}"
    return "resolve-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _validate_binding(graph: SemanticDependencyGraph, document: CanonicalDocument, lock: RevisionLock) -> None:
    if graph.document_id != lock.document_id or graph.source_sha256 != lock.source_sha256 or graph.digital_revision != lock.digital_revision:
        raise ValueError("dependency graph is not bound to the locked revision")
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256:
        raise ValueError("canonical document is not bound to the locked source")


def resolve_dependency_targets(
    graph: SemanticDependencyGraph,
    document: CanonicalDocument,
    lock: RevisionLock,
) -> tuple[SemanticDependencyResolution, ...]:
    """Resolve explicit dependency identifiers against canonical node identifiers only.

    No prose similarity or semantic inference is used. Zero matches are UNRESOLVED;
    multiple matches are AMBIGUOUS; exactly one match is RESOLVED.
    """
    _validate_binding(graph, document, lock)
    nodes = tuple(sorted(document.nodes, key=lambda node: (node.order, node.node_id)))
    resolutions: list[SemanticDependencyResolution] = []
    for dependency in sorted(graph.dependencies, key=lambda dep: (dep.dependency_id, dep.target)):
        if dependency.document_id != lock.document_id or dependency.source_sha256 != lock.source_sha256 or dependency.digital_revision != lock.digital_revision:
            raise ValueError(f"dependency {dependency.dependency_id} is not bound to the locked revision")
        source_node = next((node for node in nodes if node.node_id == dependency.source_node_id), None)
        if source_node is None:
            raise ValueError(f"dependency {dependency.dependency_id} references unknown source node {dependency.source_node_id}")
        target_values = _normalized_target_values(dependency.target)
        matches = tuple(node.node_id for node in nodes if _node_identifiers(node) & target_values)
        if len(matches) == 1:
            status, reason = "RESOLVED", "exact canonical identifier match"
        elif not matches:
            status, reason = "UNRESOLVED", "no canonical node identifier matches target"
        else:
            status, reason = "AMBIGUOUS", "multiple canonical nodes match target identifier"
        resolutions.append(
            SemanticDependencyResolution(
                _resolution_id(dependency, status, matches, reason),
                lock.document_id,
                lock.source_sha256,
                lock.digital_revision,
                dependency.dependency_id,
                dependency.target,
                status,
                matches,
                dependency.source_node_id,
                dependency.anchor_page,
                reason,
            )
        )
    return tuple(resolutions)


def validate_dependency_resolutions(
    resolutions: tuple[SemanticDependencyResolution, ...],
    graph: SemanticDependencyGraph,
    document: CanonicalDocument,
    lock: RevisionLock,
    *,
    require_resolved: bool = True,
) -> tuple[bool, list[str]]:
    """Validate resolution provenance and, by default, fail closed on unresolved targets."""
    issues: list[str] = []
    _validate_binding(graph, document, lock)
    nodes = {node.node_id: node for node in document.nodes}
    dependencies = {dependency.dependency_id: dependency for dependency in graph.dependencies}
    seen: set[str] = set()
    for resolution in resolutions:
        if resolution.resolution_id in seen:
            issues.append(f"Duplicate dependency resolution: {resolution.resolution_id}")
        seen.add(resolution.resolution_id)
        if resolution.document_id != lock.document_id or resolution.source_sha256 != lock.source_sha256 or resolution.digital_revision != lock.digital_revision:
            issues.append(f"Resolution {resolution.resolution_id} is not bound to the locked revision")
        dependency = dependencies.get(resolution.dependency_id)
        if dependency is None:
            issues.append(f"Resolution {resolution.resolution_id} references unknown dependency {resolution.dependency_id}")
            continue
        if resolution.target != dependency.target or resolution.source_node_id != dependency.source_node_id or resolution.anchor_page != dependency.anchor_page:
            issues.append(f"Resolution {resolution.resolution_id} does not match dependency provenance")
        if resolution.status not in {"RESOLVED", "UNRESOLVED", "AMBIGUOUS"}:
            issues.append(f"Resolution {resolution.resolution_id} has invalid status")
        if not resolution.reason:
            issues.append(f"Resolution {resolution.resolution_id} has no reason")
        if any(node_id not in nodes for node_id in resolution.target_node_ids):
            issues.append(f"Resolution {resolution.resolution_id} references unknown target node")
        if resolution.status == "RESOLVED" and len(resolution.target_node_ids) != 1:
            issues.append(f"Resolution {resolution.resolution_id} must have exactly one target node")
        if resolution.status == "AMBIGUOUS" and len(resolution.target_node_ids) < 2:
            issues.append(f"Resolution {resolution.resolution_id} must retain all ambiguous target nodes")
        if resolution.status == "UNRESOLVED" and resolution.target_node_ids:
            issues.append(f"Resolution {resolution.resolution_id} has targets despite UNRESOLVED status")
        if require_resolved and resolution.status != "RESOLVED":
            issues.append(f"Dependency target is not resolved: {resolution.target}")
    expected = set(dependencies)
    actual = {resolution.dependency_id for resolution in resolutions}
    for dependency_id in sorted(expected - actual):
        issues.append(f"Missing dependency resolution: {dependency_id}")
    for dependency_id in sorted(actual - expected):
        issues.append(f"Unexpected dependency resolution: {dependency_id}")
    return not issues, issues
