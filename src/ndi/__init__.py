"""Generic normative document intelligence primitives."""

from .canonical import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, ParserObservation, SourceAnchor, stable_document_id, stable_node_id
from .matching import compare_documents, match_nodes, normalize_text
from .observations import RawObservation, add_observation, observation_discrepancies, parser_coverage
from .observation_artifacts import observation_artifact_json, observation_artifact_sha256, observation_manifest
from .adapters import from_docling_records, from_markitdown, from_opendataloader_records, from_pypdf_pages, from_records, new_document
from .adapter_contract import AdapterCapabilities, ParserAdapter, validate_adapter_capabilities, validate_adapter_output
from .adapter_registry import RegisteredAdapter, adapt_all, adapt_registered, default_adapters, validate_default_adapters
from .ingestion import ObservationArtifact, ObservationPackage, ingest_parser_outputs
from .external_sources import CrossCheckResult, DiscrepancyEvidence, DiscrepancyKind, DiscoveryStatus, ExternalDocument, ExternalObservationSet, ExternalSourceProvider, ValidatedSource, discover_validated, validate_candidate
from .external_comparison import ExternalComparisonResult, compare_against_external, compare_discovered_sources, compare_observation_set
from .external_retrieval import RetrievedSource, retrieve_validated, verify_retrieved_bytes
from .external_parsing import ExternalParser, ExternalParserObservation, aggregate_external_observations, parse_retrieved_external
from .external_pipeline import ExternalPipelineResult, run_external_cross_check
from .integrated_reconciliation import IntegratedReconciliationReport, ResolutionAction, ResolutionDecision, ResolvedReconciliation, reconcile_with_external, resolve_reconciliation
from .dbn_gate import DBNFixtureEvidence, EvidenceMode, build_dbn_fixture_evidence, dbn_structural_gate, write_dbn_fixture_evidence
from .graphical_verification import GraphicalVerificationScope, validate_graphical_verification
from .revision_lock import PROTOCOL_VERSION, RevisionLock, build_revision_lock, persist_revision_lock, verify_revision_lock
from .ai_verification import AIVerificationRecord, build_ai_verification, build_evidence_hash, persist_ai_verification, validate_ai_verifications
from .final_acceptance import final_acceptance_with_ai
from .normative_semantics import ApplicabilityLink, NormativeUnit, RuleRegistryEntry, SemanticDependency, SemanticDependencyGraph, SemanticInterpretationError, build_applicability_links, build_dependency_graph, build_normative_units, build_rule_registry, decompose_normative_node, validate_dependency_graph, validate_normative_units
from .extractor import ExtractionError, extract_pdf, extract_pdf_evidence, markitdown_version, pdf_page_text, pypdf_version
from .validator import Quality, RecognitionAudit, RecognitionIssue, audit_document
from .reconciliation import ReconciliationDecision, ReconciliationReport, reconcile_document
from .verification import AcceptanceEvidence, ExternalCrossCheckRecord, GateResult, GateStatus, GraphicalVerificationRecord, RevisionRecord, digital_revision, final_acceptance, gate_a_observations, gate_b_reconciliation, gate_c_structural_acceptance, gate_d_persistence, gate_e_revision_infrastructure, gate_f_verification, merge_parser_documents, persist_digital_representation, write_revision_record
from .source_registry import Compatibility, DocumentIdentity, SourceCandidate, SourceRecord, SourceRegistry, SourceType

__all__ = [
    "BoundingBox", "CanonicalDocument", "CanonicalNode", "NodeType", "ParserObservation", "SourceAnchor", "stable_document_id", "stable_node_id",
    "compare_documents", "match_nodes", "normalize_text", "RawObservation", "add_observation", "observation_discrepancies", "parser_coverage",
    "observation_manifest", "observation_artifact_json", "observation_artifact_sha256",
    "from_docling_records", "from_markitdown", "from_opendataloader_records", "from_pypdf_pages", "from_records", "new_document",
    "AdapterCapabilities", "ParserAdapter", "validate_adapter_capabilities", "validate_adapter_output", "RegisteredAdapter", "adapt_all", "adapt_registered", "default_adapters", "validate_default_adapters",
    "ObservationArtifact", "ObservationPackage", "ingest_parser_outputs",
    "CrossCheckResult", "DiscrepancyEvidence", "DiscrepancyKind", "DiscoveryStatus", "ExternalDocument", "ExternalObservationSet", "ExternalSourceProvider", "ValidatedSource", "discover_validated", "validate_candidate",
    "ExternalComparisonResult", "compare_against_external", "compare_discovered_sources", "compare_observation_set",
    "RetrievedSource", "retrieve_validated", "verify_retrieved_bytes", "ExternalParser", "ExternalParserObservation", "aggregate_external_observations", "parse_retrieved_external", "ExternalPipelineResult", "run_external_cross_check",
    "IntegratedReconciliationReport", "ResolutionAction", "ResolutionDecision", "ResolvedReconciliation", "reconcile_with_external", "resolve_reconciliation",
    "DBNFixtureEvidence", "EvidenceMode", "build_dbn_fixture_evidence", "dbn_structural_gate", "write_dbn_fixture_evidence",
    "GraphicalVerificationScope", "validate_graphical_verification", "PROTOCOL_VERSION", "RevisionLock", "build_revision_lock", "persist_revision_lock", "verify_revision_lock",
    "AIVerificationRecord", "build_ai_verification", "build_evidence_hash", "persist_ai_verification", "validate_ai_verifications", "final_acceptance_with_ai",
    "NormativeUnit", "ApplicabilityLink", "RuleRegistryEntry", "SemanticDependency", "SemanticDependencyGraph", "SemanticInterpretationError", "build_normative_units", "decompose_normative_node", "validate_normative_units", "build_applicability_links", "build_rule_registry", "build_dependency_graph", "validate_dependency_graph",
    "ExtractionError", "extract_pdf", "extract_pdf_evidence", "markitdown_version", "pdf_page_text", "pypdf_version",
    "Quality", "RecognitionAudit", "RecognitionIssue", "audit_document", "ReconciliationDecision", "ReconciliationReport", "reconcile_document",
    "AcceptanceEvidence", "ExternalCrossCheckRecord", "GateResult", "GateStatus", "GraphicalVerificationRecord", "RevisionRecord",
    "digital_revision", "final_acceptance", "gate_a_observations", "gate_b_reconciliation", "gate_c_structural_acceptance", "gate_d_persistence",
    "gate_e_revision_infrastructure", "gate_f_verification", "merge_parser_documents", "persist_digital_representation", "write_revision_record",
    "Compatibility", "DocumentIdentity", "SourceCandidate", "SourceRecord", "SourceRegistry", "SourceType",
]