from pathlib import Path
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.services.expense_import_service import (
    ExpenseImportService,
)


def test_import_expenses() -> None:
    repository = Mock(spec=ExpenseRepository)
    pipeline = Mock()
    user_id = uuid4()

    expense = Expense(
        user_id=user_id,
        amount=Decimal("100.00"),
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date=date(2026, 9, 10),
    )

    pipeline.process.return_value = [
        {
            "amount": Decimal("100.00"),
            "description": "Lunch",
            "category": "Food",
            "expense_date": date(2026, 9, 10),
            "_is_duplicate": False,
        }
    ]
    repository.save_many.side_effect = lambda expenses: expenses

    service = ExpenseImportService(
        repository=repository,
        preprocessing_pipeline=pipeline,
    )

    raw_records = [
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "FOOD",
            "expense_date": "2026-09-10",
        }
    ]

    with patch(
        "expense_analyzer.services.expense_import_service."
        "IngestionStrategyFactory.get_strategy"
    ) as factory:

        strategy = Mock()
        strategy.read.return_value = raw_records
        factory.return_value = strategy

        result = service.import_expenses(
            Path("expenses.csv"),
            user_id,
        )

    assert len(result) == 1
    assert result[0].amount == expense.amount
    assert result[0].description == expense.description
    assert result[0].category == expense.category
    assert result[0].expense_date == expense.expense_date
    factory.assert_called_once()
    strategy.read.assert_called_once()
    pipeline.process.assert_called_once_with([raw_records[0]])

    repository.save_many.assert_called_once()
    saved_expense = repository.save_many.call_args.args[0][0]
    assert saved_expense.id is not None
    assert saved_expense.user_id == user_id
    assert saved_expense.amount == expense.amount
    assert saved_expense.description == expense.description
    assert saved_expense.category == expense.category
    assert saved_expense.expense_date == expense.expense_date


def test_import_expenses_skips_and_reports_duplicates() -> None:
    user_id = uuid4()
    repository = Mock(spec=ExpenseRepository)
    repository.save_many.side_effect = lambda expenses: expenses
    pipeline = PreprocessingPipeline(processors=[])
    service = ExpenseImportService(
        repository=repository,
        preprocessing_pipeline=pipeline,
    )

    raw_records = [
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "FOOD",
            "expense_date": "2026-09-10",
        },
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "FOOD",
            "expense_date": "2026-09-10",
        },
    ]

    with patch(
        "expense_analyzer.services.expense_import_service."
        "IngestionStrategyFactory.get_strategy"
    ) as factory:
        strategy = Mock()
        strategy.read.return_value = raw_records
        factory.return_value = strategy

        result = service.import_expenses_detailed(Path("expenses.csv"),user_id=user_id,)

    assert len(result.expenses) == 1
    assert result.skipped_duplicates == 1
    assert result.skipped_rows == [
        {
            "row_number": 2,
            "reason": "Duplicate expense skipped.",
        }
    ]