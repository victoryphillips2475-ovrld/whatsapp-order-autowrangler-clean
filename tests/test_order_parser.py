"""Unit tests for the WhatsApp order parser.

Covers a range of realistic message formats and edge‑cases.
"""

import pytest

from orderstream.backend.services.order_parser_service import parse_whatsapp_order


def _normalize_price(price_str: str) -> float:
    """Helper to reliably compare float values from the parser.
    Strips commas and converts to float.
    """
    return float(price_str.replace(",", ""))


def test_parser_basic_full_fields():
    msg = """
    Name: John Doe
    Phone: +2348012345678
    2x Coke ₦150
    1x Bread ₦200
    Total: ₦500
    Notes: extra sauce
    """
    result = parse_whatsapp_order(msg)
    assert result["customer_name"] == "John Doe"
    assert result["customer_phone"] == "+2348012345678"
    assert len(result["items"]) == 2
    assert result["items"][0]["product"] == "Coke"
    assert result["items"][0]["quantity"] == 2
    assert result["items"][0]["price"] == 150.0
    assert result["total"] == 500.0
    assert result["notes"] == "extra sauce"


def test_parser_no_total_computed():
    msg = """
    Customer: Jane Smith
    Contact: 08012345678
    3x Water ₦100
    2x Juice ₦250
    """
    result = parse_whatsapp_order(msg)
    # Phone should be normalised to leading '+'
    assert result["customer_phone"] == "+08012345678"
    # Total = 3*100 + 2*250 = 800
    assert result["total"] == 800.0
    assert result["notes"] is None


def test_parser_hyphen_and_ngn_symbol():
    msg = """
    name - Alice Johnson
    mobile - +234 809 123 4567
    1 x Bread NGN200
    2x Milk ₦300
    total ₦800
    """
    result = parse_whatsapp_order(msg)
    assert result["customer_name"] == "Alice Johnson"
    # Normalised phone strips spaces
    assert result["customer_phone"] == "+2348091234567"
    assert len(result["items"]) == 2
    # Ensure both NGN and ₦ symbols are accepted
    assert any(it["product"] == "Bread" and it["price"] == 200.0 for it in result["items"])
    assert any(it["product"] == "Milk" and it["price"] == 300.0 for it in result["items"])
    assert result["total"] == 800.0


def test_parser_price_with_commas():
    msg = """
    Name: Bob Marley
    Phone: +2348011122233
    1x Pizza ₦1,250
    2x Soda ₦300
    Total: ₦1,850
    """
    result = parse_whatsapp_order(msg)
    assert result["total"] == 1850.0
    # Verify individual prices are parsed correctly despite commas
    pizza = next(item for item in result["items"] if item["product"] == "Pizza")
    assert pizza["price"] == 1250.0
    soda = next(item for item in result["items"] if item["product"] == "Soda")
    assert soda["price"] == 300.0


def test_parser_missing_notes_and_extra_whitespace():
    msg = """
    Customer :   Charlie
    Phone: +234 807 555 9999
    5x IceCream ₦120
    
    """
    result = parse_whatsapp_order(msg)
    assert result["customer_name"] == "Charlie"
    assert result["customer_phone"] == "+2348075559999"
    assert len(result["items"]) == 1
    assert result["items"][0]["product"] == "IceCream"
    assert result["total"] == 600.0  # 5 * 120
    assert result["notes"] is None

# The parser raises ``ValueError`` when mandatory fields are missing.

def test_parser_missing_name_raises():
    msg = """
    Phone: +2348012345678
    1x Water ₦100
    """
    with pytest.raises(ValueError):
        parse_whatsapp_order(msg)

def test_parser_missing_items_raises():
    msg = """
    Name: No Items
    Phone: +2348012345678
    Total: ₦0
    """
    with pytest.raises(ValueError):
        parse_whatsapp_order(msg)