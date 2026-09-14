from __future__ import annotations

from .ai_verification import AIVerificationRecord, validate_ai_verifications
from .revision_lock import RevisionLock
from .verification import AcceptanceEvidence, GateResult, GateStatus


def final_acceptance_with_ai(
    evidence: AcceptanceEvidence,
    records: tuple[AIVerificationRecord, ...],
    lock: RevisionLock,
) -> GateResult:
    ai_ok, ai_issues = validate_ai_verifications(records, lock)
    missing = evidence.missing()
    checks = {name: name not in missing for name in evidence.__dataclass_fields__}
    checks["independent_ai_verification"] = ai_ok
    issues = list(ai_issues)
    if missing:
        issues.insert(0, "DIGITAL_ACCEPTED blocked: " + ", ".join(missing))
    if not ai_ok:
        issues.append("Independent AI verification requirement is not satisfied.")
    if issues:
        return GateResult("FINAL", GateStatus.FAIL, checks, issues, ["DIGITAL_ACCEPTED"])
    return GateResult("FINAL", GateStatus.PASS, checks, [], ["DIGITAL_ACCEPTED"])
