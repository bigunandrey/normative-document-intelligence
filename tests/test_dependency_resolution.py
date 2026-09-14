import pytest

from ndi import (
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    SourceAnchor,
    build_dependency_graph,
    build_normative_units,
    build_revision_lock,
    resolve_dependency_targets,
    validate_dependency_resolutions,
)
from ndi.normative_semantics import SemanticDependency

SHA = "a" * 64


def make_doc(*nodes):
    d = CanonicalDocument("doc-test", "test.pdf", SHA, 1)
    for node_id, text, order, attributes in nodes:
        d.add_node(
            CanonicalNode(
                node_id,
                NodeType.PARAGRAPH,
                text=text,
                order=order,
                anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10)),
                attributes=attributes,
            )
        )
    return d


def test_exact_node_id_dependency_resolves():
    d = make_doc(
        ("source", "The system shall comply with node-target.", 0, {"references": ["node-target"]}),
        ("node-target", "The system shall provide detection.", 1, {}),
    )
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    resolutions = resolve_dependency_targets(graph, d, lock)
    assert len(resolutions) == 1
    assert resolutions[0].status == "RESOLVED"
    assert resolutions[0].target_node_ids == ("node-target",)
    assert validate_dependency_resolutions(resolutions, graph, d, lock) == (True, [])


def test_clause_identifier_dependency_resolves():
    d = make_doc(
        ("source", "The system shall comply with clause 5.2.", 0, {"references": ["clause:5.2"]}),
        ("target", "The system shall provide detection.", 1, {"clause_id": "5.2"}),
    )
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    resolution = resolve_dependency_targets(graph, d, lock)[0]
    assert resolution.status == "RESOLVED"
    assert resolution.target_node_ids == ("target",)


def test_unknown_dependency_target_is_unresolved_and_fails_closed():
    d = make_doc(("source", "The system shall comply with clause 9.9.", 0, {"references": ["clause:9.9"]}))
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    resolution = resolve_dependency_targets(graph, d, lock)[0]
    assert resolution.status == "UNRESOLVED"
    assert resolution.target_node_ids == ()
    ok, issues = validate_dependency_resolutions((resolution,), graph, d, lock)
    assert not ok
    assert "Dependency target is not resolved: clause:9.9" in issues


def test_duplicate_canonical_identifiers_are_ambiguous():
    d = make_doc(
        ("source", "The system shall comply with clause 5.2.", 0, {"references": ["clause:5.2"]}),
        ("target-a", "The system shall provide detection.", 1, {"clause_id": "5.2"}),
        ("target-b", "The system shall provide alarm.", 2, {"clause_id": "5.2"}),
    )
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    resolution = resolve_dependency_targets(graph, d, lock)[0]
    assert resolution.status == "AMBIGUOUS"
    assert resolution.target_node_ids == ("target-a", "target-b")
    assert not validate_dependency_resolutions((resolution,), graph, d, lock)[0]


def test_resolution_rejects_tampered_dependency_provenance():
    d = make_doc(
        ("source", "The system shall comply with clause 5.2.", 0, {"references": ["clause:5.2"]}),
        ("target", "The system shall provide detection.", 1, {"clause_id": "5.2"}),
    )
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    resolution = resolve_dependency_targets(graph, d, lock)[0]
    tampered = type(resolution)(
        resolution.resolution_id,
        resolution.document_id,
        "b" * 64,
        resolution.digital_revision,
        resolution.dependency_id,
        resolution.target,
        resolution.status,
        resolution.target_node_ids,
        resolution.source_node_id,
        resolution.anchor_page,
        resolution.reason,
    )
    ok, issues = validate_dependency_resolutions((tampered,), graph, d, lock)
    assert not ok
    assert any("not bound to the locked revision" in issue for issue in issues)


def test_resolution_requires_canonical_document_binding():
    d = make_doc(("source", "The system shall comply with node-target.", 0, {"references": ["node-target"]}))
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    other = make_doc(("node-target", "The system shall provide detection.", 0, {}))
    with pytest.raises(ValueError):
        resolve_dependency_targets(graph, other, lock)


def test_resolution_order_is_deterministic():
    d = make_doc(
        ("source-a", "The system shall comply with target-b.", 0, {"references": ["target-b"]}),
        ("source-b", "The system shall comply with target-a.", 1, {"references": ["target-a"]}),
        ("target-a", "The system shall provide detection.", 2, {}),
        ("target-b", "The system shall provide alarm.", 3, {}),
    )
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    first = resolve_dependency_targets(graph, d, lock)
    second = resolve_dependency_targets(graph, d, lock)
    assert first == second


def test_validate_resolution_rejects_missing_resolution():
    d = make_doc(("source", "The system shall comply with node-target.", 0, {"references": ["node-target"]}))
    lock = build_revision_lock(d)
    graph = build_dependency_graph(build_normative_units(d, lock), lock)
    ok, issues = validate_dependency_resolutions((), graph, d, lock)
    assert not ok
    assert any("Missing dependency resolution" in issue for issue in issues)
