from __future__ import annotations

"""Deterministic, source-bound serialization of parser observation evidence."""

import hashlib
import json
from dataclasses import is_dataclass, fields
from typing import Any

from .canonical import CanonicalDocument
from .observations import parser_coverage


def observation_manifest(document: CanonicalDocument) -> dict[str, Any]:
    """Build a deterministic JSON-safe manifest without changing evidence."""
    observations = []
    for node in document.nodes:
        for observation in node.observations:
            observations.append(
                {
                    "node_id": node.node_id,
                    "observation_id": observation.observation_id,
                    "parser": observation.parser,
                    "parser_version": observation.parser_version,
                    "node_type": observation.node_type.value,
                    "text": observation.text,
                    "anchor": _json_safe(observation.anchor),
                    "confidence": observation.confidence,
                    "attributes": _json_safe(observation.attributes),
                }
            )

    observations.sort(key=lambda item: (item["parser"], item["observation_id"]))
    return {
        "artifact_type": "parser_observation_manifest",
        "schema_version": "1.0",
        "document_id": document.document_id,
        "source_name": document.source_name,
        "source_sha256": document.source_sha256,
        "page_count": document.page_count,
        "parser_versions": dict(sorted(document.parser_versions.items())),
        "parser_coverage": parser_coverage(document),
        "observation_count": len(observations),
        "observations": observations,
    }


def observation_artifact_json(document: CanonicalDocument) -> str:
    """Serialize the observation manifest canonically for hashing/persistence."""
    return json.dumps(observation_manifest(document), ensure_ascii=False, indent=2, sort_keys=True)


def observation_artifact_sha256(document: CanonicalDocument) -> str:
    payload = observation_artifact_json(document).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _json_safe(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value
