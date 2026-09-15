import pytest

from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind, apply_bindings
from ndi.digital_copy_workflow import DigitalCopyJob, DigitalCopySource


def make_job() -> DigitalCopyJob:
    return DigitalCopyJob("job", DigitalCopySource("/tmp/source.pdf", "source.pdf", "abc"))


def test_failed_evidence_requires_blocker() -> None:
    with pytest.raises(ValueError, match="blockers"):
        StageEvidence(StageEvidenceKind.RECONCILIATION, False).validate()


def test_bindings_are_restricted_to_acceptance_identity_fields() -> None:
    job = make_job()
    evidence = StageEvidence(
        StageEvidenceKind.IDENTITY,
        True,
        bindings={"document_id": "doc-1", "revision_id": "rev-1"},
    )
    evidence.validate()
    apply_bindings(job, evidence.bindings)
    assert job.document_id == "doc-1"
    assert job.revision_id == "rev-1"


def test_unknown_binding_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        apply_bindings(make_job(), {"status": "DIGITAL_ACCEPTED"})
