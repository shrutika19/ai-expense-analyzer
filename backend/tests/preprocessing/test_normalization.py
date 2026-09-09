from expense_analyzer.preprocessing.processors.normalization import (
    NormalizationProcessor,
)


def test_normalization_strips_whitespace_from_values() -> None:
    processor = NormalizationProcessor()

    records = [
        {
            "amount": " 250.50 ",
            "description": " Lunch ",
            "category": " Food ",
            "expense_date": " 2026-09-09 ",
        }
    ]

    result = processor.process(records)

    assert result == [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        }
    ]


def test_normalization_strips_whitespace_from_keys() -> None:
    processor = NormalizationProcessor()

    records = [
        {
            " amount ": "250.50",
            " description ": "Lunch",
        }
    ]

    result = processor.process(records)

    assert result == [
        {
            "amount": "250.50",
            "description": "Lunch",
        }
    ]


def test_normalization_preserves_non_string_values() -> None:
    processor = NormalizationProcessor()

    records = [
        {
            "amount": 250.50,
            "description": "Lunch",
        }
    ]

    result = processor.process(records)

    assert result == records