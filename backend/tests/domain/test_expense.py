from datetime import date
from decimal import Decimal

import pytest

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.exceptions.domain import InvalidExpenseException


def test_should_create_valid_expense() -> None:
    expense = Expense(
        amount=Decimal("250.50"),
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date=date(2026, 9, 9),
    )

    assert expense.amount == Decimal("250.50")
    assert expense.description == "Lunch"
    assert expense.category == ExpenseCategory.FOOD


def test_should_reject_non_positive_amount() -> None:
    with pytest.raises(InvalidExpenseException):
        Expense(
            amount=Decimal("0"),
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 9),
        )


def test_should_reject_empty_description() -> None:
    with pytest.raises(InvalidExpenseException):
        Expense(
            amount=Decimal("250"),
            description="   ",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 9),
        )