from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.exceptions.domain import InvalidExpenseException


def test_should_create_valid_expense() -> None:
    user_id = uuid4()
    expense = Expense(
        user_id=user_id,
        amount=Decimal("250.50"),
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date=date(2026, 9, 9),
    )

    assert expense.amount == Decimal("250.50")
    assert expense.description == "Lunch"
    assert expense.category == ExpenseCategory.FOOD
    assert expense.user_id == user_id


def test_should_reject_non_positive_amount() -> None:
    user_id = uuid4()
    with pytest.raises(InvalidExpenseException):
        Expense(
            user_id=user_id,
            amount=Decimal("0"),
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 9),
        )


def test_should_reject_empty_description() -> None:
    user_id = uuid4()
    with pytest.raises(InvalidExpenseException):
        Expense(
            user_id=user_id,
            amount=Decimal("250"),
            description="   ",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 9),
        )