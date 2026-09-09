from datetime import date
from decimal import Decimal

from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.preprocessing.processors.amount import (
    AmountNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.duplicate import (
    DuplicateDetectionProcessor,
)
from expense_analyzer.preprocessing.processors.missing_value import (
    MissingValueProcessor,
)
from expense_analyzer.preprocessing.processors.normalization import (
    NormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.date import (
    DateNormalizationProcessor,
)


def test_pipeline_executes_processors_in_order() -> None:
    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DuplicateDetectionProcessor(),
            DateNormalizationProcessor()
        ]
    )

    records = [
        {
            " amount ": " 1,200.50 ",
            "description": " Uber ride ",
            "category": " Travel ",
            "expense_date": " 2026-09-08 ",
        },
        {
            "amount": "1200.50",
            "description": "Uber ride",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
    ]

    result = pipeline.process(records)
    assert result[0]["amount"] == Decimal("1200.50")
    assert result[0]["expense_date"] == date(2026, 9, 8)
    assert result[0]["_is_duplicate"] is False

    assert result[1]["amount"] == Decimal("1200.50")
    assert result[1]["expense_date"] == date(2026, 9, 8)
    assert result[1]["_is_duplicate"] is True

    assert result == [
        {
            "amount": Decimal("1200.50"),
            "description": "Uber ride",
            "category": "Travel",
            "expense_date": date(2026, 9, 8),
            "_is_duplicate": False,
        },
        {
            "amount": Decimal("1200.50"),
            "description": "Uber ride",
            "category": "Travel",
            "expense_date": date(2026, 9, 8),
            "_is_duplicate": True,
        },
    ]


def test_pipeline_normalizes_missing_values() -> None:
    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
        ]
    )

    records = [
        {
            "amount": " null ",
            "description": " Lunch ",
            "category": " Food ",
        }
    ]

    result = pipeline.process(records)

    assert result == [
        {
            "amount": None,
            "description": "Lunch",
            "category": "Food",
        }
    ]


def test_empty_records_return_empty_records() -> None:
    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
        ]
    )

    result = pipeline.process([])

    assert result == []