"""Generic normative-document intelligence primitives."""

from .canonical import (
    BoundingBox, CanonicalDocument, CanonicalNode, NodeType, ParserObservation,
    SourceAnchor, stable_document_id, stable_node_id,
)
from .matching import compare_documents, match_nodes, normalize_text
from .observations import RawObservation, add_observation, observation_discrepancies, parser_coverage
from .adapters import from_markitdown, from_records, new_document
from .extractor import ExtractionError, extract_pdf, markitdown_version
from .validator import Quality, RecognitionAudit, RecognitionIssue, audit_document
from .reconciliation import ReconciliationDecision, ReconciliationReport, reconcile_document

__all__ = [
    "BoundingBox", "CanonicalDocument", "CanonicalNode", "NodeType", "ParserObservation", "SourceAnchor",
    "stable_document_id", "stable_node_id", "compare_documents", "match_nodes", "normalize_text",
    "RawObservation", "add_observation", "observation_discrepancies", "parser_coverage",
    "from_markitdown", "from_records", "new_document", "ExtractionError", "extract_pdf", "markitdown_version",
    "Quality", "RecognitionAudit", "RecognitionIssue", "audit_document",
    "ReconciliationDecision", "ReconciliationReport", "reconcile_document",
]
