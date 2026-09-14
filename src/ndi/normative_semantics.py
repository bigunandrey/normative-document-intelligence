from __future__ import annotations

"""Source-bound atomic normative semantics."""

from dataclasses import asdict, dataclass, field
import hashlib
import json
import re
from typing import Any

from .canonical import CanonicalDocument, CanonicalNode, NodeType
from .revision_lock import RevisionLock


class SemanticInterpretationError(ValueError):
    pass


@dataclass(frozen=True)
class NormativeUnit:
    unit_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    node_id: str
    anchor_page: int | None
    operator: str
    modality: str
    subject: str
    predicate: str
    condition: str = ""
    exception: str = ""
    source_text: str = ""
    applicability: tuple[str, ...] = ()
    subject_type: str = ""
    dependency_targets: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class ApplicabilityLink:
    link_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    unit_id: str
    target: str
    relation: str
    source_node_id: str
    anchor_page: int | None


@dataclass(frozen=True)
class RuleRegistryEntry:
    rule_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    node_id: str
    anchor_page: int | None
    rule_kind: str
    expression: str
    source_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticDependency:
    dependency_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    source_unit_id: str
    target: str
    relation: str
    source_node_id: str
    anchor_page: int | None
    evidence_text: str


@dataclass(frozen=True)
class SemanticDependencyGraph:
    document_id: str
    source_sha256: str
    digital_revision: str
    dependencies: tuple[SemanticDependency, ...]


@dataclass(frozen=True)
class SemanticEvaluation:
    evaluation_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    unit_id: str
    result: str
    applicability_state: str
    condition_state: str
    reason: str


def _unit_id(document_id: str, node_id: str, ordinal: int, text: str) -> str:
    payload = f"{document_id}|{node_id}|{ordinal}|{text}"
    return "unit-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _operator(text: str) -> tuple[str, str]:
    matches = [("shall not", "PROHIBITION"), ("must not", "PROHIBITION"), ("shall be", "REQUIREMENT"), ("must be", "REQUIREMENT"), ("shall", "REQUIREMENT"), ("must", "REQUIREMENT"), ("should", "RECOMMENDATION"), ("may", "PERMISSION")]
    found: list[tuple[str, str, int, int]] = []
    for token, mode in matches:
        for match in re.finditer(rf"\b{re.escape(token)}\b", text, re.IGNORECASE):
            found.append((token, mode, match.start(), match.end()))
    if not found:
        raise SemanticInterpretationError("No unambiguous normative operator found")
    compound_ranges = [(start, end) for token, _mode, start, end in found if token in {"shall not", "must not", "shall be", "must be"}]
    effective = [item for item in found if not any(start <= item[2] and item[3] <= end and item[0] not in {"shall not", "must not", "shall be", "must be"} for start, end in compound_ranges)]
    modes = {mode for _token, mode, _start, _end in effective}
    if len(modes) != 1:
        raise SemanticInterpretationError("Multiple conflicting normative operators found")
    token, mode, _start, _end = max(effective, key=lambda item: len(item[0]))
    return token, mode


def _attribute_values(node: CanonicalNode, *keys: str) -> tuple[str, ...]:
    values: list[str] = []
    for key in keys:
        value = node.attributes.get(key)
        if value is None:
            continue
        raw = value if isinstance(value, (list, tuple, set)) else (value,)
        values.extend(str(item).strip() for item in raw if str(item).strip())
    return tuple(dict.fromkeys(values))


def decompose_normative_node(document: CanonicalDocument, node: CanonicalNode, *, digital_revision: str) -> tuple[NormativeUnit, ...]:
    if node.node_type not in {NodeType.PARAGRAPH, NodeType.LIST_ITEM, NodeType.NOTE, NodeType.TABLE_CELL}:
        return ()
    text = " ".join(node.text.split())
    if not text:
        return ()
    operator, modality = _operator(text)
    clauses = re.split(r"\s+(?:provided that|if|unless|except that|except)\s+", text, maxsplit=1, flags=re.IGNORECASE)
    main = clauses[0]
    condition = clauses[1] if len(clauses) == 2 and re.search(r"\bprovided that\b|\bif\b", text, re.IGNORECASE) else ""
    exception = clauses[1] if len(clauses) == 2 and re.search(r"\bunless\b|\bexcept\b", text, re.IGNORECASE) else ""
    match = re.search(rf"\b{re.escape(operator)}\b", main, re.IGNORECASE)
    if not match:
        raise SemanticInterpretationError("Normative operator could not be located")
    subject = main[:match.start()].strip(" ,:;- ") or "unspecified subject"
    predicate = main[match.end():].strip(" ,:;- ")
    if not predicate:
        raise SemanticInterpretationError("Normative predicate is empty")
    page = node.anchor.page if node.anchor else None
    applicability = _attribute_values(node, "applicability", "applies_to", "scope")
    subject_type = str(node.attributes.get("subject_type", node.attributes.get("type", ""))).strip()
    dependency_targets = _attribute_values(node, "references", "cross_references", "depends_on", "dependency", "related_to")
    return (NormativeUnit(_unit_id(document.document_id, node.node_id, 0, text), document.document_id, document.source_sha256, digital_revision, node.node_id, page, operator, modality, subject, predicate, condition, exception, text, applicability, subject_type, dependency_targets),)


def build_normative_units(document: CanonicalDocument, lock: RevisionLock) -> tuple[NormativeUnit, ...]:
    from .verification import digital_revision
    revision = digital_revision(document)
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256 or revision != lock.digital_revision:
        raise ValueError("semantic model is not bound to the locked digital representation")
    units: list[NormativeUnit] = []
    for node in sorted(document.nodes, key=lambda n: (n.order, n.node_id)):
        units.extend(decompose_normative_node(document, node, digital_revision=revision))
    return tuple(units)


def build_applicability_links(units: tuple[NormativeUnit, ...], lock: RevisionLock) -> tuple[ApplicabilityLink, ...]:
    links: list[ApplicabilityLink] = []
    for unit in units:
        if unit.document_id != lock.document_id or unit.source_sha256 != lock.source_sha256 or unit.digital_revision != lock.digital_revision:
            raise ValueError("applicability unit is not bound to the locked revision")
        for target in unit.applicability:
            payload = f"{unit.unit_id}|{target}|applies_to"
            links.append(ApplicabilityLink("link-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], lock.document_id, lock.source_sha256, lock.digital_revision, unit.unit_id, target, "applies_to", unit.node_id, unit.anchor_page))
    return tuple(links)


def build_rule_registry(document: CanonicalDocument, lock: RevisionLock) -> tuple[RuleRegistryEntry, ...]:
    from .verification import digital_revision
    revision = digital_revision(document)
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256 or revision != lock.digital_revision:
        raise ValueError("rule registry is not bound to the locked digital representation")
    entries: list[RuleRegistryEntry] = []
    for node in sorted(document.nodes, key=lambda n: (n.order, n.node_id)):
        if node.node_type not in {NodeType.TABLE, NodeType.TABLE_CELL, NodeType.FORMULA}:
            continue
        kind = "table" if node.node_type in {NodeType.TABLE, NodeType.TABLE_CELL} else "formula"
        expression = " ".join(node.text.split())
        if not expression:
            continue
        payload = f"{document.document_id}|{node.node_id}|{kind}|{expression}"
        entries.append(RuleRegistryEntry("rule-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], document.document_id, document.source_sha256, revision, node.node_id, node.anchor.page if node.anchor else None, kind, expression, expression, dict(node.attributes)))
    return tuple(entries)


def build_dependency_graph(units: tuple[NormativeUnit, ...], lock: RevisionLock) -> SemanticDependencyGraph:
    dependencies: list[SemanticDependency] = []
    for unit in units:
        if unit.document_id != lock.document_id or unit.source_sha256 != lock.source_sha256 or unit.digital_revision != lock.digital_revision:
            raise ValueError("dependency graph unit is not bound to the locked revision")
        for target in unit.dependency_targets:
            if not target:
                raise SemanticInterpretationError("empty dependency target")
            payload = f"{unit.unit_id}|{target}|depends_on"
            dependencies.append(SemanticDependency("dep-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], lock.document_id, lock.source_sha256, lock.digital_revision, unit.unit_id, target, "depends_on", unit.node_id, unit.anchor_page, unit.source_text))
    return SemanticDependencyGraph(lock.document_id, lock.source_sha256, lock.digital_revision, tuple(dependencies))


def validate_dependency_graph(graph: SemanticDependencyGraph, lock: RevisionLock) -> tuple[bool, list[str]]:
    issues: list[str] = []
    seen: set[str] = set()
    for dep in graph.dependencies:
        if dep.dependency_id in seen:
            issues.append(f"Duplicate dependency: {dep.dependency_id}")
        seen.add(dep.dependency_id)
        if dep.document_id != lock.document_id or dep.source_sha256 != lock.source_sha256 or dep.digital_revision != lock.digital_revision:
            issues.append(f"Dependency {dep.dependency_id} is not bound to the locked revision")
        if not dep.source_unit_id or not dep.target or not dep.relation or not dep.evidence_text:
            issues.append(f"Dependency {dep.dependency_id} is incomplete")
    return not issues, issues


def evaluate_normative_unit(unit: NormativeUnit, *, applicability: bool | None = True, condition: bool | None = True) -> SemanticEvaluation:
    if not unit.unit_id or not unit.document_id or not unit.source_sha256 or not unit.digital_revision:
        raise SemanticInterpretationError("incomplete normative unit")
    if applicability is None:
        result, state, reason = "UNRESOLVED", "UNKNOWN", "applicability is unresolved"
    elif not applicability:
        result, state, reason = "NOT_APPLICABLE", "FALSE", "normative unit is not applicable"
    elif condition is None:
        result, state, reason = "UNRESOLVED", "UNKNOWN", "condition is unresolved"
    elif condition is False:
        result, state, reason = "INACTIVE", "FALSE", "normative condition is false"
    else:
        state = "TRUE"
        result = {"REQUIREMENT": "REQUIREMENT_ACTIVE", "PROHIBITION": "PROHIBITION_ACTIVE", "RECOMMENDATION": "RECOMMENDATION_ACTIVE", "PERMISSION": "PERMISSION_ACTIVE"}.get(unit.modality)
        if result is None:
            raise SemanticInterpretationError("unsupported normative modality")
        reason = "normative applicability and condition are satisfied"
    payload = f"{unit.unit_id}|{result}|{state}|{reason}"
    return SemanticEvaluation("eval-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], unit.document_id, unit.source_sha256, unit.digital_revision, unit.unit_id, result, "TRUE" if applicability else "FALSE" if applicability is False else "UNKNOWN", state, reason)


def evaluate_normative_units(units: tuple[NormativeUnit, ...], lock: RevisionLock, *, applicability: dict[str, bool | None] | None = None, conditions: dict[str, bool | None] | None = None) -> tuple[SemanticEvaluation, ...]:
    applicability = applicability or {}
    conditions = conditions or {}
    results: list[SemanticEvaluation] = []
    for unit in sorted(units, key=lambda u: u.unit_id):
        if unit.document_id != lock.document_id or unit.source_sha256 != lock.source_sha256 or unit.digital_revision != lock.digital_revision:
            raise ValueError("semantic evaluation is not bound to the locked revision")
        results.append(evaluate_normative_unit(unit, applicability=applicability.get(unit.unit_id, True), condition=conditions.get(unit.unit_id, True)))
    return tuple(results)


def validate_normative_units(units: tuple[NormativeUnit, ...], lock: RevisionLock) -> tuple[bool, list[str]]:
    issues: list[str] = []
    seen: set[str] = set()
    for unit in units:
        if unit.unit_id in seen:
            issues.append(f"Duplicate normative unit: {unit.unit_id}")
        seen.add(unit.unit_id)
        if unit.document_id != lock.document_id or unit.source_sha256 != lock.source_sha256 or unit.digital_revision != lock.digital_revision:
            issues.append(f"Unit {unit.unit_id} is not bound to the locked revision")
        if not unit.source_text or not unit.operator or not unit.predicate:
            issues.append(f"Unit {unit.unit_id} is incomplete")
    return not issues, issues
