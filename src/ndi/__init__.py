"""Generic normative-document intelligence primitives."""

from .canonical import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    ParserObservation,
    SourceAnchor,
    stable_document_id,
    stable_node_id,
)
from .matching import compare_documents, match_nodes, normalize_text

__all__ = [
    "BoundingBox",
    "CanonicalDocument",
    "CanonicalNode",
    "NodeType",
    "ParserObservation",
    "SourceAnchor",
    "stable_document_id",
    "stable_node_id",
    "compare_documents",
    "match_nodes",
    "normalize_text",
]
