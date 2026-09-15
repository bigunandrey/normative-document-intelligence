from ndi import (
    BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor,
    build_amendment_actions, build_dependency_graph, build_normative_units,
    build_revision_lock, evaluate_normative_unit, resolve_dependency_targets,
    validate_semantic_fail_closed,
)
from ndi.dependency_resolution import SemanticDependencyResolution

SHA = "d" * 64


def make_doc():
    d = CanonicalDocument("doc-accept", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode(
        "node-1", NodeType.PARAGRAPH,
        text="The system shall comply with clause 5.2.", order=0,
        anchor=SourceAnchor(page=1, bbox=BoundingBox(0, 0, 10, 10)),
        attributes={"references": ["clause:5.2"]},
    ))
    d.add_node(CanonicalNode(
        "node-2", NodeType.PARAGRAPH,
        text="The enclosure shall be fire rated.", order=1,
        anchor=SourceAnchor(page=2), attributes={"clause_id": "5.2"},
    ))
    return d


def test_fail_closed_accepts_resolved_semantic_chain():
    d = make_doc()
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    graph = build_dependency_graph(units, lock)
    resolutions = resolve_dependency_targets(graph, d, lock)
    evaluations = tuple(evaluate_normative_unit(unit) for unit in units)
    assert validate_semantic_fail_closed(
        d, lock, units=units, evaluations=evaluations,
        dependency_graph=graph, dependency_resolutions=resolutions,
    ) == (True, [])


def test_fail_closed_rejects_unresolved_dependency():
    d = make_doc()
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    graph = build_dependency_graph(units, lock)
    dep = graph.dependencies[0]
    unresolved = SemanticDependencyResolution(
        "resolve-test", dep.document_id, dep.source_sha256, dep.digital_revision,
        dep.dependency_id, dep.target, "UNRESOLVED", (), dep.source_node_id,
        dep.anchor_page, "no canonical node identifier matches target",
    )
    ok, issues = validate_semantic_fail_closed(
        d, lock, units=units, dependency_graph=graph,
        dependency_resolutions=(unresolved,),
    )
    assert not ok
    assert any("Dependency target is not resolved" in issue for issue in issues)


def test_fail_closed_rejects_unresolved_evaluation():
    d = make_doc()
    lock = build_revision_lock(d)
    unit = build_normative_units(d, lock)[0]
    unresolved = evaluate_normative_unit(unit, applicability=None)
    ok, issues = validate_semantic_fail_closed(d, lock, units=(unit,), evaluations=(unresolved,))
    assert not ok
    assert any("Evaluation" in issue and "unresolved" in issue for issue in issues)


def test_fail_closed_rejects_unresolved_amendment_target():
    d = CanonicalDocument("doc-amend", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode(
        "node-1", NodeType.PARAGRAPH, text="Delete clause 9.9.", order=0,
        anchor=SourceAnchor(page=1), attributes={"deletes": "clause:9.9"},
    ))
    lock = build_revision_lock(d)
    actions = build_amendment_actions(d, lock)
    ok, issues = validate_semantic_fail_closed(d, lock, amendments=actions)
    assert not ok
    assert "Amendment target is unresolved: clause:9.9" in issues


def test_fail_closed_rejects_ambiguous_amendment_target():
    d = CanonicalDocument("doc-amend", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="Clause 5.2 shall apply.", order=0, anchor=SourceAnchor(page=1), attributes={"clause_id": "5.2"}))
    d.add_node(CanonicalNode("node-2", NodeType.PARAGRAPH, text="Clause 5.2 shall be protected.", order=1, anchor=SourceAnchor(page=2), attributes={"clause_id": "5.2"}))
    d.add_node(CanonicalNode("node-3", NodeType.PARAGRAPH, text="Delete clause 5.2.", order=2, anchor=SourceAnchor(page=3), attributes={"deletes": "clause:5.2"}))
    lock = build_revision_lock(d)
    actions = build_amendment_actions(d, lock)
    ok, issues = validate_semantic_fail_closed(d, lock, amendments=actions)
    assert not ok
    assert "Amendment target is ambiguous: clause:5.2" in issues
