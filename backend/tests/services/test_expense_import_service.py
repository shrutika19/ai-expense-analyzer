from pathlib import Path
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.services.expense_import_service import (
    ExpenseImportService,
)


def test_import_expenses() -> None:
    repository = Mock(spec=ExpenseRepository)
    pipeline = Mock()

    expense = Expense(
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
    repository.save.return_value = expense

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
            Path("expenses.csv")
        )

    assert result == [expense]
    factory.assert_called_once()
    strategy.read.assert_called_once()
    pipeline.process.assert_called_once_with(raw_records)

    repository.save.assert_called_once()
    saved_expense = repository.save.call_args.args[0]
    assert saved_expense.id is not None
    assert saved_expense.amount == expense.amount
    assert saved_expense.description == expense.description
    assert saved_expense.category == expense.category
    assert saved_expense.expense_date == expense.expense_date