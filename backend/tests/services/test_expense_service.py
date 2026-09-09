from datetime import date
from decimal import Decimal

from expense_analyzer.domain.entities.expense import Expense

from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.preprocessing.processors.amount import (
    AmountNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.date import (
    DateNormalizationProcessor,
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
from expense_analyzer.services.expense_service import ExpenseService


class FakeExpenseRepository:

    def save(self, expense: Expense) -> Expense:
        return expense

    def find_all(self) -> list[Expense]:
        return []


def create_service() -> ExpenseService:
    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )

    return ExpenseService(
        preprocessing_pipeline=pipeline,
        repository=FakeExpenseRepository(),
    )



def test_create_expense() -> None:
    service = create_service()

    request = ExpenseCreateRequest(
        amount="250.50",
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date="2026-09-09",
    )

    result = service.create_expense(request)

    assert result.id is not None
    assert result.amount == Decimal("250.50")
    assert result.description == "Lunch"
    assert result.category == ExpenseCategory.FOOD
    assert result.expense_date == date(2026, 9, 9)



def test_process_records() -> None:
    service = create_service()

    records = [
        {
            " amount ": " 250.50 ",
            "description": " Lunch ",
            "category": " Food ",
            "expense_date": "09/09/2026",
        }
    ]

    result = service.process_records(records)

    assert len(result) == 1

    expense = result[0]

    assert expense.amount == Decimal("250.50")
    assert expense.description == "Lunch"
    assert expense.category == ExpenseCategory.FOOD
    assert expense.expense_date == date(2026, 9, 9)




def test_process_records_ignores_duplicates() -> None:
    service = create_service()

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

    result = service.process_records(records)

    assert len(result) == 1

    assert result[0].amount == Decimal("250.50")




def test_process_multiple_records() -> None:
    service = create_service()

    records = [
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "500.00",
            "description": "Uber",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
    ]

    result = service.process_records(records)

    assert len(result) == 2

    assert result[0].amount == Decimal("100.00")
    assert result[1].amount == Decimal("500.00")



def test_process_empty_records() -> None:
    service = create_service()

    result = service.process_records([])

    assert result == []