from expense_analyzer.preprocessing.processors.missing_value import (
    MissingValueProcessor,
)


def test_empty_string_is_converted_to_none() -> None:
    processor = MissingValueProcessor()

    records = [
        {
            "amount": "",
            "description": "Lunch",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] is None


def test_whitespace_is_converted_to_none() -> None:
    processor = MissingValueProcessor()

    records = [
        {
            "amount": "   ",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] is None


def test_common_missing_value_strings_are_converted_to_none() -> None:
    processor = MissingValueProcessor()

    records = [
        {
            "amount": "null",
            "description": "None",
            "category": "N/A",
            "expense_date": "nan",
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] is None
    assert result[0]["description"] is None
    assert result[0]["category"] is None
    assert result[0]["expense_date"] is None


def test_none_remains_none() -> None:
    processor = MissingValueProcessor()

    records = [
        {
            "amount": None,
        }
    ]

    result = processor.process(records)

    assert result[0]["amount"] is None


def test_valid_values_are_not_changed() -> None:
    processor = MissingValueProcessor()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
        }
    ]

    result = processor.process(records)

    assert result == records