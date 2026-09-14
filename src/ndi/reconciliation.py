from __future__ import annotations

from dataclasses import dataclass, field

from .canonical import CanonicalDocument, CanonicalNode, ParserObservation


@dataclass(frozen=True)
class ReconciliationDecision:
    """A traceable decision about parser observations.

    This layer does not decide normative meaning. It only records structural
    agreement/disagreement between parser observations.
    """

    node_id: str
    status: str
    observation_ids: tuple[str, ...]
    reason: str


@dataclass
class ReconciliationReport:
    decisions: list[ReconciliationDecision] = field(default_factory=list)

    @property
    def conflicts(self) -> list[ReconciliationDecision]:
        return [item for item in self.decisions if item.status == "CONFLICT"]


def reconcile_document(document: CanonicalDocument) -> ReconciliationReport:
    report = ReconciliationReport()
    for node in document.nodes.values():
        observations = node.observations
        if not observations:
            report.decisions.append(
                ReconciliationDecision(
                    node_id=node.node_id,
                    status="MISSING_OBSERVATION",
                    observation_ids=(),
                    reason="Canonical node has no parser observations.",
                )
            )
            continue

        texts = {observation.text for observation in observations}
        types = {observation.node_type for observation in observations}
        status = "AGREED" if len(texts) == 1 and len(types) == 1 else "CONFLICT"
        reason = "All parser observations agree structurally." if status == "AGREED" else "Parser observations disagree and require review."
        report.decisions.append(
            ReconciliationDecision(
                node_id=node.node_id,
                status=status,
                observation_ids=tuple(_observation_id(observation) for observation in observations),
                reason=reason,
            )
        )
    return report


def _observation_id(observation: ParserObservation) -> str:
    return f"{observation.parser}:{observation.parser_version}:{observation.node_type}:{observation.text}"
