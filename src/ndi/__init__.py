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
from .verification import (
    AcceptanceEvidence, ExternalCrossCheckRecord, GateResult, GateStatus,
    GraphicalVerificationRecord, RevisionRecord, digital_revision,
    final_acceptance, gate_a_observations, gate_b_reconciliation,
    gate_c_structural_acceptance, gate_d_persistence, gate_e_revision_infrastructure,
    gate_f_verification, persist_digital_representation, write_revision_record,
)

__all__ = [
    "BoundingBox", "CanonicalDocument", "CanonicalNode", "NodeType", "ParserObservation", "SourceAnchor",
    "stable_document_id", "stable_node_id", "compare_documents", "match_nodes", "normalize_text",
    "RawObservation", "add_observation", "observation_discrepancies", "parser_coverage",
    "from_markitdown", "from_records", "new_document", "ExtractionError", "extract_pdf", "markitdown_version",
    "Quality", "RecognitionAudit", "RecognitionIssue", "audit_document",
    "ReconciliationDecision", "ReconciliationReport", "reconcile_document",
    "AcceptanceEvidence", "ExternalCrossCheckRecord", "GateResult", "GateStatus",
    "GraphicalVerificationRecord", "RevisionRecord", "digital_revision", "final_acceptance",
    "gate_a_observations", "gate_b_reconciliation", "gate_c_structural_acceptance",
    "gate_d_persistence", "gate_e_revision_infrastructure", "gate_f_verification",
    "persist_digital_representation", "write_revision_record",
]
