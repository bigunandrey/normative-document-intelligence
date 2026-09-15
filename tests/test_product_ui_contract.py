from pathlib import Path


def test_product_ui_contract_is_present():
    path = Path(__file__).parents[1] / "docs" / "PRODUCT-UI-CONTRACT.md"
    text = path.read_text(encoding="utf-8")
    for marker in ("Source PDF", "Canonical Document", "Graphical Verification", "DIGITAL_ACCEPTED"):
        assert marker in text
