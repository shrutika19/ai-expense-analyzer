from expense_analyzer.preprocessing.processors.duplicate import (
    DuplicateDetectionProcessor,
)


def test_duplicate_record_is_detected() -> None:
    processor = DuplicateDetectionProcessor()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    ]

    result = processor.process(records)

    assert result[0]["_is_duplicate"] is False
    assert result[1]["_is_duplicate"] is True


def test_unique_records_are_not_marked_as_duplicates() -> None:
    processor = DuplicateDetectionProcessor()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "1200.00",
            "description": "Uber ride",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
    ]

    result = processor.process(records)

    assert result[0]["_is_duplicate"] is False
    assert result[1]["_is_duplicate"] is False


def test_multiple_duplicates_are_detected() -> None:
    processor = DuplicateDetectionProcessor()

    records = [
        {
            "amount": "100.00",
            "description": "Coffee",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "100.00",
            "description": "Coffee",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "100.00",
            "description": "Coffee",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    ]

    result = processor.process(records)

    assert result[0]["_is_duplicate"] is False
    assert result[1]["_is_duplicate"] is True
    assert result[2]["_is_duplicate"] is True


def test_empty_records_return_empty_records() -> None:
    processor = DuplicateDetectionProcessor()

    result = processor.process([])

    assert result == []