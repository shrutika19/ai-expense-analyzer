from decimal import Decimal

import pytest

from expense_analyzer.preprocessing.processors.amount import (
    AmountNormalizationProcessor,
)


def test_amount_string_is_converted_to_decimal() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": "250.50",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == Decimal("250.50")


def test_amount_whitespace_is_removed() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": " 250.50 ",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == Decimal("250.50")


def test_amount_with_comma_is_normalized() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": "1,200.50",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == Decimal("1200.50")


def test_rupee_symbol_is_removed() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": "₹500.00",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == Decimal("500.00")


def test_decimal_amount_remains_decimal() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": Decimal("250.50"),
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == Decimal("250.50")


def test_missing_amount_remains_none() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": None,
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] is None


def test_invalid_amount_raises_error() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": "abc",
        }
    ]

    with pytest.raises(ValueError, match="Invalid expense amount"):
        processor.process(records)


def test_other_fields_are_not_modified() -> None:
    processor = AmountNormalizationProcessor()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
        }
    ]

    result = processor.process(records)

    assert result[0]["description"] == "Lunch"
    assert result[0]["category"] == "Food"