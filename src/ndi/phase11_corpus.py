from __future__ import annotations

"""Machine-readable register and gate for Phase 11 real-document validation."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import hashlib
import json
from pathlib import Path
from typing import Mapping


class CorpusState(StrEnum):
    CANDIDATE = "CANDIDATE"
    SOURCE_IDENTIFIED = "SOURCE_IDENTIFIED"
    AUTHORITATIVE_SOURCE_VERIFIED = "AUTHORITATIVE_SOURCE_VERIFIED"
    ACQUISITION_PENDING = "ACQUISITION_PENDING"
    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"
    ACCEPTED = "ACCEPTED"


@dataclass(frozen=True)
class CorpusItem:
    item_id: str
    title: str
    edition: str
    authoritative_source: str
    source_sha256: str | None = None
    state: CorpusState = CorpusState.CANDIDATE
    source_form: str | None = None
    revision: str | None = None
    workflow_result: str | None = None
    blockers: tuple[str, ...] = ()
    discrepancies: tuple[str, ...] = ()
    generic_gaps: tuple[str, ...] = ()
    regression_fixtures: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        for name in ("item_id", "title", "edition", "authoritative_source"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Corpus item {name} must be non-empty")
        if self.source_sha256 is not None:
            value = self.source_sha256.lower()
            if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ValueError("source_sha256 must be a SHA-256 hex digest")
        if self.state == CorpusState.ACCEPTED:
            if self.workflow_result != "DIGITAL_ACCEPTED":
                raise ValueError("Accepted corpus item requires DIGITAL_ACCEPTED result")
            if not self.source_sha256:
                raise ValueError("Accepted corpus item requires source_sha256")
            if self.blockers or self.generic_gaps:
                raise ValueError("Accepted corpus item cannot contain blockers or generic gaps")
        if self.workflow_result == "DIGITAL_ACCEPTED" and self.state != CorpusState.ACCEPTED:
            raise ValueError("DIGITAL_ACCEPTED result requires ACCEPTED corpus state")
        if self.generic_gaps and not self.regression_fixtures:
            raise ValueError("Every generic capability gap must have regression-fixture evidence")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        data = asdict(self)
        data["state"] = self.state.value
        for key in ("blockers", "discrepancies", "generic_gaps", "regression_fixtures"):
            data[key] = list(data[key])
        data["metadata"] = dict(sorted(self.metadata.items()))
        return data


def load_corpus(path: Path) -> tuple[CorpusItem, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Corpus register must contain an items array")
    items: list[CorpusItem] = []
    for raw in data["items"]:
        if not isinstance(raw, dict):
            raise ValueError("Each corpus item must be an object")
        item = CorpusItem(
            item_id=str(raw.get("item_id", "")),
            title=str(raw.get("title", "")),
            edition=str(raw.get("edition", "")),
            authoritative_source=str(raw.get("authoritative_source", "")),
            source_sha256=raw.get("source_sha256"),
            state=CorpusState(str(raw.get("state", CorpusState.CANDIDATE.value))),
            source_form=raw.get("source_form"),
            revision=raw.get("revision"),
            workflow_result=raw.get("workflow_result"),
            blockers=tuple(raw.get("blockers", ())),
            discrepancies=tuple(raw.get("discrepancies", ())),
            generic_gaps=tuple(raw.get("generic_gaps", ())),
            regression_fixtures=tuple(raw.get("regression_fixtures", ())),
            metadata=dict(raw.get("metadata", {})),
        )
        item.validate()
        items.append(item)
    return tuple(items)


def corpus_sha256(items: tuple[CorpusItem, ...]) -> str:
    payload = json.dumps(
        {"items": [item.as_dict() for item in items]},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
