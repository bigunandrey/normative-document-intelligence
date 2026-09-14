from __future__ import annotations

"""Deterministic, source-bound serialization of parser observation evidence."""

import hashlib
import json
from typing import Any

from .canonical import CanonicalDocument
from .observations import parser_coverage


def observation_manifest(document: CanonicalDocument) -> dict[str, Any]:
    """Build a deterministic manifest without changing or correcting evidence."""
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
                    "anchor": observation.anchor,
                    "confidence": observation.confidence,
                    "attributes": observation.attributes,
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
    return json.dumps(
        observation_manifest(document), ensure_ascii=False, indent=2, sort_keys=True, default=_json_default
    )


def observation_artifact_sha256(document: CanonicalDocument) -> str:
    payload = observation_artifact_json(document).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _json_default(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _json_default(getattr(value, key)) for key in value.__dataclass_fields__}
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"Unsupported observation artifact value: {type(value)!r}")
