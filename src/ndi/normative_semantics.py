from __future__ import annotations

"""Source-bound atomic normative semantics."""

from dataclasses import asdict, dataclass
import hashlib
import json
import re

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

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
    found: list[tuple[str, str]] = []
    for token, mode in matches:
        for match in re.finditer(rf"\b{re.escape(token)}\b", text, re.IGNORECASE):
            found.append((token, mode, match.start(), match.end()))

    if not found:
        raise SemanticInterpretationError("No unambiguous normative operator found")

    # A compound operator owns the words it contains.  Thus "shall not"
    # must not also produce a separate "shall" match, and similarly for
    # "shall be" / "must be".  Other operators elsewhere in the sentence
    # remain visible and can still make the interpretation ambiguous.
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
    return (NormativeUnit(_unit_id(document.document_id, node.node_id, 0, text), document.document_id, document.source_sha256, digital_revision, node.node_id, page, operator, modality, subject, predicate, condition, exception, text),)


def build_normative_units(document: CanonicalDocument, lock: RevisionLock) -> tuple[NormativeUnit, ...]:
    from .verification import digital_revision
    revision = digital_revision(document)
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256 or revision != lock.digital_revision:
        raise ValueError("semantic model is not bound to the locked digital representation")
    units: list[NormativeUnit] = []
    for node in sorted(document.nodes, key=lambda n: (n.order, n.node_id)):
        units.extend(decompose_normative_node(document, node, digital_revision=revision))
    return tuple(units)


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
