from datetime import date

import pytest

from expense_analyzer.preprocessing.processors.date import (
    DateNormalizationProcessor,
)


def test_iso_date_is_normalized() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": "2026-09-09",
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == date(2026, 9, 9)



def test_slash_date_is_normalized() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": "09/09/2026",
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == date(2026, 9, 9)


def test_hyphen_date_is_normalized() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": "09-09-2026",
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == date(2026, 9, 9)


def test_two_digit_year_is_normalized() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": "09/09/26",
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == date(2026, 9, 9)


def test_date_whitespace_is_removed() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": " 2026-09-09 ",
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == date(2026, 9, 9)


def test_existing_date_remains_date() -> None:
    processor = DateNormalizationProcessor()

    expense_date = date(2026, 9, 9)

    records = [
        {
            "expense_date": expense_date,
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] == expense_date


def test_missing_date_remains_none() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": None,
        }
    ]

    result = processor.process(records)

    assert result[0]["expense_date"] is None


def test_invalid_date_raises_error() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "expense_date": "invalid-date",
        }
    ]

    with pytest.raises(
        ValueError,
        match="Invalid expense date",
    ):
        processor.process(records)



def test_other_fields_are_not_modified() -> None:
    processor = DateNormalizationProcessor()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "09/09/2026",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] == "250.50"
    assert result[0]["description"] == "Lunch"
    assert result[0]["category"] == "Food"
    assert result[0]["expense_date"] == date(2026, 9, 9)