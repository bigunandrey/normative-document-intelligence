from tools.dbn_benchmark import EXPECTED_PAGE_COUNT, EXPECTED_SHA256, EXPECTED_SIZE_BYTES


def test_registered_dbn_identity_constants():
    assert EXPECTED_SHA256 == "fbaa2493ed510d621e8f368ec4910e5cc30d177744f22356fe3a120bbe5a5056"
    assert EXPECTED_SIZE_BYTES == 23_532_218
    assert EXPECTED_PAGE_COUNT == 105
