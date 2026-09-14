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


def _unit_id(document_id: str, node_id: str, ordinal: int, text: str) -> str:
    payload = f"{document_id}|{node_id}|{ordinal}|{text}"
    return "unit-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _operator(text: str) -> tuple[str, str]:
    matches = [
        ("shall not", "PROHIBITION"),
        ("must not", "PROHIBITION"),
        ("shall be", "REQUIREMENT"),
        ("must be", "REQUIREMENT"),
        ("shall", "REQUIREMENT"),
        ("must", "REQUIREMENT"),
        ("should", "RECOMMENDATION"),
        ("may", "PERMISSION"),
    ]
    found: list[tuple[str, str, int, int]] = []
    for token, mode in matches:
        for match in re.finditer(rf"\b{re.escape(token)}\b", text, re.IGNORECASE):
            found.append((token, mode, match.start(), match.end()))
    if not found:
        raise SemanticInterpretationError("No unambiguous normative operator found")
    compound_ranges = [
        (start, end)
        for token, _mode, start, end in found
        if token in {"shall not", "must not", "shall be", "must be"}
    ]
    effective = [
        item for item in found
        if not any(start <= item[2] and item[3] <= end and item[0] not in {"shall not", "must not", "shall be", "must be"}
                   for start, end in compound_ranges)
    ]
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
    return (NormativeUnit(_unit_id(document.document_id, node.node_id, 0, text), document.document_id, document.source_sha256, digital_revision, node.node_id, page, operator, modality, subject, predicate, condition, exception, text, applicability, subject_type),)


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
            links.append(ApplicabilityLink(
                "link-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24],
                lock.document_id, lock.source_sha256, lock.digital_revision,
                unit.unit_id, target, "applies_to", unit.node_id, unit.anchor_page,
            ))
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
        entries.append(RuleRegistryEntry(
            "rule-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24],
            document.document_id, document.source_sha256, revision, node.node_id,
            node.anchor.page if node.anchor else None, kind, expression, expression,
            dict(node.attributes),
        ))
    return tuple(entries)


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
