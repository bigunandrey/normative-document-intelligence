import pytest

from ndi import BoundingBox, CanonicalDocument, CanonicalNode, NodeType, RevisionLock, SourceAnchor, build_normative_units, build_revision_lock, validate_normative_units
from ndi.normative_semantics import SemanticInterpretationError, decompose_normative_node

SHA = "a" * 64


def doc(text):
    d = CanonicalDocument("doc-test", "test.pdf", SHA, 1)
    d.add_node(CanonicalNode("node-1", NodeType.PARAGRAPH, text=text, order=0, anchor=SourceAnchor(page=1, bbox=BoundingBox(0,0,10,10))))
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
