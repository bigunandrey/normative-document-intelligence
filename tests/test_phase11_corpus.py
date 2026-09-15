from pathlib import Path

from ndi.phase11_corpus import CorpusState, corpus_sha256, load_corpus


ROOT = Path(__file__).parents[1]
CORPUS = ROOT / "benchmarks" / "phase11-corpus.json"


def test_phase11_corpus_register_is_valid_and_deterministic():
    items = load_corpus(CORPUS)
    assert len(items) >= 3
    assert items[0].item_id == "DBN-V2.5-56-2014"
    assert items[0].state == CorpusState.ACQUISITION_PENDING
    assert items[0].source_sha256 is None
    assert corpus_sha256(items) == corpus_sha256(items)


def test_phase11_corpus_does_not_promote_historical_evidence_to_current_acceptance():
    items = load_corpus(CORPUS)
    dbn = items[0]
    assert dbn.metadata["historical_evidence"]
    assert dbn.workflow_result is None
    assert dbn.state != CorpusState.ACCEPTED


def test_phase11_acceptance_requires_current_source_hash_and_clean_result():
    items = load_corpus(CORPUS)
    assert all(item.state != CorpusState.ACCEPTED for item in items)
