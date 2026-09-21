from decimal import Decimal

import pytest
from pydantic import ValidationError


from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)


def test_valid_expense() -> None:
    expense = ExpenseValidationModel(
        amount="250.50",
        description="Lunch",
        category="Food",
        expense_date="2026-09-09",
    )

    assert expense.amount == Decimal("250.50")
    assert expense.category == ExpenseCategory.FOOD


def test_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        ExpenseValidationModel(
            amount="0",
            description="Lunch",
            category="Food",
            expense_date="2026-09-09",
        )