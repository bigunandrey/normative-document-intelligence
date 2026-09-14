from ndi.canonical import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    ParserObservation,
    SourceAnchor,
)
from ndi.reconciliation import reconcile_document


def observation(observation_id: str, text: str, node_type: NodeType = NodeType.PARAGRAPH):
    return ParserObservation(
        parser="test-parser",
        parser_version="1.0",
        observation_id=observation_id,
        node_type=node_type,
        text=text,
        anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10)),
    )


def test_agreement_preserves_observation_ids():
    document = CanonicalDocument("doc-test", "test.pdf", "a" * 64, 1)
    node = CanonicalNode("node-1", NodeType.PARAGRAPH, "same")
    node.add_observation(observation("obs-a", "same"))
    node.add_observation(observation("obs-b", "same"))
    document.add_node(node)

    report = reconcile_document(document)

    assert report.decisions[0].status == "AGREED"
    assert report.decisions[0].observation_ids == ("obs-a", "obs-b")


def test_disagreement_is_not_silently_resolved():
    document = CanonicalDocument("doc-test", "test.pdf", "a" * 64, 1)
    node = CanonicalNode("node-1", NodeType.PARAGRAPH)
    node.add_observation(observation("obs-a", "first"))
    node.add_observation(observation("obs-b", "second"))
    document.add_node(node)

    report = reconcile_document(document)

    assert len(report.conflicts) == 1
    assert report.conflicts[0].status == "CONFLICT"
    assert report.conflicts[0].observation_ids == ("obs-a", "obs-b")


def test_missing_observation_is_explicit():
    document = CanonicalDocument("doc-test", "test.pdf", "a" * 64, 1)
    document.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH))

    report = reconcile_document(document)

    assert report.decisions[0].status == "MISSING_OBSERVATION"
