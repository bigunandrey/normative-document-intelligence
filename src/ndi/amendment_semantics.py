from __future__ import annotations

"""Explicit, source-bound semantics for amendments and deletions."""

from dataclasses import dataclass
import hashlib

from .canonical import CanonicalDocument, CanonicalNode
from .revision_lock import RevisionLock


class AmendmentInterpretationError(ValueError):
    pass


@dataclass(frozen=True)
class AmendmentAction:
    action_id: str
    document_id: str
    source_sha256: str
    digital_revision: str
    source_node_id: str
    anchor_page: int | None
    action: str
    target: str
    replacement_text: str
    source_text: str


def _values(node: CanonicalNode, *keys: str) -> tuple[str, ...]:
    values: list[str] = []
    for key in keys:
        value = node.attributes.get(key)
        if value is None:
            continue
        raw = value if isinstance(value, (list, tuple, set)) else (value,)
        values.extend(str(item).strip() for item in raw if str(item).strip())
    return tuple(dict.fromkeys(values))


def _action_for(node: CanonicalNode) -> tuple[str, tuple[str, ...]]:
    deletions = _values(node, "deletes", "deletion", "deleted", "repeals", "repealed")
    replacements = _values(node, "replaces", "replacement", "replaced", "amends")
    additions = _values(node, "adds", "addition", "inserted", "inserts")
    kinds = []
    if deletions:
        kinds.append(("DELETE", deletions))
    if replacements:
        kinds.append(("REPLACE", replacements))
    if additions:
        kinds.append(("ADD", additions))
    if len(kinds) != 1:
        raise AmendmentInterpretationError("amendment action is missing or ambiguous")
    return kinds[0]


def build_amendment_actions(document: CanonicalDocument, lock: RevisionLock) -> tuple[AmendmentAction, ...]:
    if document.document_id != lock.document_id or document.source_sha256 != lock.source_sha256:
        raise ValueError("amendment semantics are not bound to the locked source")
    from .verification import digital_revision
    revision = digital_revision(document)
    if revision != lock.digital_revision:
        raise ValueError("amendment semantics are not bound to the locked digital revision")
    actions: list[AmendmentAction] = []
    for node in sorted(document.nodes, key=lambda n: (n.order, n.node_id)):
        markers = _values(node, "deletes", "deletion", "deleted", "repeals", "repealed", "replaces", "replacement", "replaced", "amends", "adds", "addition", "inserted", "inserts")
        if not markers:
            continue
        action, targets = _action_for(node)
        replacement = " ".join(node.attributes.get("replacement_text", "").split())
        if action == "REPLACE" and not replacement:
            raise AmendmentInterpretationError("replacement action has no replacement_text")
        source_text = " ".join(node.text.split())
        page = node.anchor.page if node.anchor else None
        for target in targets:
            payload = f"{document.document_id}|{node.node_id}|{action}|{target}|{replacement}"
            actions.append(AmendmentAction("amend-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], document.document_id, document.source_sha256, revision, node.node_id, page, action, target, replacement, source_text))
    return tuple(actions)


def validate_amendment_actions(actions: tuple[AmendmentAction, ...], lock: RevisionLock) -> tuple[bool, list[str]]:
    issues: list[str] = []
    seen: set[str] = set()
    for item in actions:
        if item.action_id in seen:
            issues.append(f"Duplicate amendment action: {item.action_id}")
        seen.add(item.action_id)
        if item.document_id != lock.document_id or item.source_sha256 != lock.source_sha256 or item.digital_revision != lock.digital_revision:
            issues.append(f"Amendment {item.action_id} is not bound to the locked revision")
        if item.action not in {"ADD", "REPLACE", "DELETE"} or not item.target or not item.source_text:
            issues.append(f"Amendment {item.action_id} is incomplete")
        if item.action == "REPLACE" and not item.replacement_text:
            issues.append(f"Replacement {item.action_id} has no replacement text")
        if item.action != "REPLACE" and item.replacement_text:
            issues.append(f"Non-replacement {item.action_id} contains replacement text")
    return not issues, issues
