from __future__ import annotations

"""Parser-neutral helpers for preserving extraction evidence."""

from dataclasses import dataclass
from typing import Any

from .canonical import CanonicalDocument, CanonicalNode, NodeType, ParserObservation, SourceAnchor, stable_node_id


@dataclass(frozen=True)
class RawObservation:
    parser: str
    parser_version: str
    node_type: NodeType
    text: str = ""
    anchor: SourceAnchor | None = None
    confidence: float | None = None
    attributes: dict[str, Any] | None = None


def add_observation(document: CanonicalDocument, observation: RawObservation, *, ordinal: int, parent_id: str | None = None) -> CanonicalNode:
    node_id = stable_node_id(document.document_id, observation.node_type, observation.anchor, ordinal)
    try:
        node = document.node(node_id)
    except KeyError:
        node = CanonicalNode(node_id=node_id, node_type=observation.node_type, text=observation.text,
                             parent_id=parent_id, order=ordinal, anchor=observation.anchor,
                             attributes=dict(observation.attributes or {}))
        document.add_node(node)
    evidence_id = f"{observation.parser}:{observation.parser_version}:{node_id}"
    node.add_observation(ParserObservation(parser=observation.parser, parser_version=observation.parser_version,
        observation_id=evidence_id, node_type=observation.node_type, text=observation.text,
        anchor=observation.anchor, confidence=observation.confidence,
        attributes=dict(observation.attributes or {})))
    return node


def parser_coverage(document: CanonicalDocument) -> dict[str, int]:
    coverage: dict[str, int] = {}
    for node in document.nodes:
        for observation in node.observations:
            coverage[observation.parser] = coverage.get(observation.parser, 0) + 1
    return dict(sorted(coverage.items()))


def observation_discrepancies(document: CanonicalDocument) -> list[dict[str, Any]]:
    discrepancies: list[dict[str, Any]] = []
    for node in document.nodes:
        texts = {o.parser: o.text for o in node.observations if o.text}
        if len(texts) > 1 and len(set(texts.values())) > 1:
            discrepancies.append({"node_id": node.node_id, "node_type": node.node_type.value,
                                  "parsers": dict(sorted(texts.items())), "status": "REVIEW_REQUIRED"})
    return discrepancies
