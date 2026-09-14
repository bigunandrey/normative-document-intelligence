import pytest

from ndi import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, SourceAnchor, build_applicability_links, build_dependency_graph, build_normative_units, build_revision_lock, build_rule_registry, evaluate_normative_unit, evaluate_normative_units, validate_dependency_graph, validate_normative_units
from ndi.normative_semantics import SemanticInterpretationError, decompose_normative_node

SHA = "a" * 64


def doc(text, *, node_type=NodeType.PARAGRAPH, attributes=None):
    d = CanonicalDocument("doc-test", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", node_type, text=text, order=0, anchor=SourceAnchor(page=1, bbox=BoundingBox(0,0,10,10)), attributes=attributes or {}))
    return d


def test_requirement_is_atomic_and_source_bound():
    d = doc("The system shall provide fire detection.")
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    assert len(units) == 1
    u = units[0]
    assert u.operator == "shall"
    assert u.modality == "REQUIREMENT"
    assert u.source_sha256 == SHA
    assert u.digital_revision == lock.digital_revision
    assert validate_normative_units(units, lock) == (True, [])


def test_prohibition_and_condition_are_preserved():
    d = doc("Equipment shall not operate if the enclosure is open.")
    lock = build_revision_lock(d)
    u = build_normative_units(d, lock)[0]
    assert u.operator == "shall not"
    assert u.modality == "PROHIBITION"
    assert u.condition == "the enclosure is open."


def test_ambiguous_modalities_fail_closed():
    d = doc("The operator shall use equipment that may be substituted.")
    with pytest.raises(SemanticInterpretationError):
        decompose_normative_node(d, d.nodes[0], digital_revision=build_revision_lock(d).digital_revision)


def test_semantics_reject_different_lock():
    d = doc("The system shall provide fire detection.")
    other = doc("The system shall provide gas detection.")
    with pytest.raises(ValueError):
        build_normative_units(d, build_revision_lock(other))


def test_applicability_and_subject_type_are_source_bound():
    d = doc("The system shall provide fire detection.", attributes={"applicability": ["sprinkler_systems", "protected_buildings"], "subject_type": "system"})
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    assert units[0].applicability == ("sprinkler_systems", "protected_buildings")
    assert units[0].subject_type == "system"
    links = build_applicability_links(units, lock)
    assert [link.target for link in links] == ["sprinkler_systems", "protected_buildings"]
    assert all(link.source_sha256 == SHA and link.digital_revision == lock.digital_revision for link in links)


def test_table_and_formula_rule_registry_is_deterministic_and_bound():
    d = CanonicalDocument("doc-test", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("table-1", NodeType.TABLE, text="Minimum area: 100 m2", order=0, anchor=SourceAnchor(page=1)))
    d.add_node(CanonicalNode("formula-1", NodeType.FORMULA, text="Q = k * sqrt(P)", order=1, anchor=SourceAnchor(page=1)))
    lock = build_revision_lock(d)
    rules = build_rule_registry(d, lock)
    assert [(r.rule_kind, r.node_id) for r in rules] == [("table", "table-1"), ("formula", "formula-1")]
    assert all(r.source_sha256 == SHA and r.digital_revision == lock.digital_revision for r in rules)


def test_dependency_graph_uses_only_explicit_source_targets():
    d = doc("The system shall comply with clause 5.2.", attributes={"references": ["clause:5.2"]})
    lock = build_revision_lock(d)
    units = build_normative_units(d, lock)
    graph = build_dependency_graph(units, lock)
    assert len(graph.dependencies) == 1
    dep = graph.dependencies[0]
    assert dep.target == "clause:5.2"
    assert dep.relation == "depends_on"
    assert dep.source_node_id == "node-1"
    assert dep.evidence_text == units[0].source_text
    assert validate_dependency_graph(graph, lock) == (True, [])


def test_dependency_graph_rejects_unbound_unit():
    d = doc("The system shall comply with clause 5.2.", attributes={"references": ["clause:5.2"]})
    other = doc("The system shall comply with clause 6.1.")
    units = build_normative_units(d, build_revision_lock(d))
    with pytest.raises(ValueError):
        build_dependency_graph(units, build_revision_lock(other))


def test_normative_evaluation_is_deterministic_and_fail_closed():
    d = doc("The system shall provide fire detection.")
    lock = build_revision_lock(d)
    unit = build_normative_units(d, lock)[0]
    active = evaluate_normative_unit(unit)
    assert active.result == "REQUIREMENT_ACTIVE"
    assert evaluate_normative_unit(unit, applicability=False).result == "NOT_APPLICABLE"
    assert evaluate_normative_unit(unit, condition=False).result == "INACTIVE"
    assert evaluate_normative_unit(unit, applicability=None).result == "UNRESOLVED"
    assert evaluate_normative_unit(unit, condition=None).result == "UNRESOLVED"
    assert evaluate_normative_units((unit,), lock) == (active,)
