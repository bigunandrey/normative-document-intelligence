from ndi import (
    AmendmentAction,
    BoundingBox,
    CanonicalDocument,
    CanonicalNode,
    NodeType,
    SourceAnchor,
    build_amendment_actions,
    build_applicability_links,
    build_dependency_graph,
    build_normative_units,
    build_revision_lock,
    build_rule_registry,
    evaluate_normative_unit,
    resolve_dependency_targets,
    validate_semantic_provenance,
)
from ndi.normative_semantics import ApplicabilityLink, RuleRegistryEntry, SemanticDependency, SemanticDependencyGraph
from ndi.dependency_resolution import SemanticDependencyResolution

SHA = "b" * 64


def test_all_semantic_artifacts_are_traceable_to_canonical_source():
    d = CanonicalDocument("doc-prov", "test.pdf", SHA, 1)
    d.add_node(
        CanonicalNode(
            "node-1",
            NodeType.PARAGRAPH,
            text="The system shall comply with clause 5.2.",
            order=0,
            anchor=SourceAnchor(page=4, bbox=BoundingBox(0, 0, 10, 10)),
            attributes={"applicability": ["protected_buildings"], "subject_type": "system", "references": ["clause:5.2"]},
        )
    )
    d.add_node(
        CanonicalNode(
            "node-2",
            NodeType.PARAGRAPH,
            text="The enclosure shall be fire rated.",
            order=1,
            anchor=SourceAnchor(page=5, bbox=BoundingBox(0, 0, 10, 10)),
            attributes={"clause_id": "5.2"},
        )
    )
    d.add_node(CanonicalNode("table-1", NodeType.TABLE, text="Minimum area: 100 m2", order=2, anchor=SourceAnchor(page=6)))
    d.add_node(CanonicalNode("formula-1", NodeType.FORMULA, text="Q = k * sqrt(P)", order=3, anchor=SourceAnchor(page=7)))
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    links = build_applicability_links(units, lock)
    rules = build_rule_registry(d, lock)
    graph = build_dependency_graph(units, lock)
    resolutions = resolve_dependency_targets(graph, d, lock)
    evaluation = evaluate_normative_unit(units[0])
    amendments = build_amendment_actions(
        CanonicalDocument("doc-amend", "test.pdf", SHA, 1),
        build_revision_lock(CanonicalDocument("doc-amend", "test.pdf", SHA, 1)),
    ) if False else ()
    assert resolutions[0].status == "RESOLVED"
    assert validate_semantic_provenance(
        d,
        lock,
        units=units,
        applicability_links=links,
        rule_entries=rules,
        dependency_graph=graph,
        dependency_resolutions=resolutions,
        evaluations=(evaluation,),
        amendments=amendments,
    ) == (True, [])


def test_provenance_rejects_tampered_unit_anchor():
    d = CanonicalDocument("doc-prov", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="The system shall comply.", order=0, anchor=SourceAnchor(page=4)))
    lock = build_revision_lock(d)
    unit = build_normative_units(d, lock)[0]
    tampered = type(unit)(unit.unit_id, unit.document_id, unit.source_sha256, unit.digital_revision, unit.node_id, 99, unit.operator, unit.modality, unit.subject, unit.predicate, unit.condition, unit.exception, unit.source_text, unit.applicability, unit.subject_type, unit.dependency_targets)
    ok, issues = validate_semantic_provenance(d, lock, units=(tampered,))
    assert not ok
    assert any("invalid source page" in issue for issue in issues)


def test_provenance_rejects_tampered_rule_source_text():
    d = CanonicalDocument("doc-prov", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("formula-1", NodeType.FORMULA, text="Q = k * sqrt(P)", order=0, anchor=SourceAnchor(page=7)))
    lock = build_revision_lock(d)
    entry = build_rule_registry(d, lock)[0]
    tampered = RuleRegistryEntry(entry.rule_id, entry.document_id, entry.source_sha256, entry.digital_revision, entry.node_id, entry.anchor_page, entry.rule_kind, entry.expression, "tampered", entry.metadata)
    ok, issues = validate_semantic_provenance(d, lock, rule_entries=(tampered,))
    assert not ok
    assert any("not traceable" in issue for issue in issues)


def test_provenance_rejects_tampered_dependency_resolution_target_node():
    d = CanonicalDocument("doc-prov", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="The system shall comply with clause 5.2.", order=0, anchor=SourceAnchor(page=4), attributes={"references": ["clause:5.2"]}))
    d.add_node(CanonicalNode("node-2", NodeType.PARAGRAPH, text="The enclosure shall be fire rated.", order=1, anchor=SourceAnchor(page=5), attributes={"clause_id": "5.2"}))
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    graph = build_dependency_graph(units, lock)
    resolution = resolve_dependency_targets(graph, d, lock)[0]
    tampered = SemanticDependencyResolution(resolution.resolution_id, resolution.document_id, resolution.source_sha256, resolution.digital_revision, resolution.dependency_id, resolution.target, resolution.status, ("missing-node",), resolution.source_node_id, resolution.anchor_page, resolution.reason)
    ok, issues = validate_semantic_provenance(d, lock, units=units, dependency_graph=graph, dependency_resolutions=(tampered,))
    assert not ok
    assert any("unknown target node" in issue for issue in issues)


def test_provenance_rejects_unbound_amendment():
    d = CanonicalDocument("doc-prov", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text="Delete clause 5.2.", order=0, anchor=SourceAnchor(page=4), attributes={"deletes": "clause:5.2"}))
    lock = build_revision_lock(d)
    action = build_amendment_actions(d, lock)[0]
    tampered = AmendmentAction(action.action_id, action.document_id, "c" * 64, action.digital_revision, action.source_node_id, action.anchor_page, action.action, action.target, action.replacement_text, action.source_text)
    ok, issues = validate_semantic_provenance(d, lock, amendments=(tampered,))
    assert not ok
    assert any("not bound" in issue for issue in issues)
