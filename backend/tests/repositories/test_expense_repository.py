from datetime import date
from decimal import Decimal

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)


def test_save_expense(test_user) -> None:
    repository = ExpenseRepository()

    expense = Expense(
        user_id=test_user.id,
        amount=Decimal("250.50"),
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date=date(2026, 9, 9),
    )

    result = repository.save(expense)

    assert result.id == expense.id
    assert result.amount == Decimal("250.50")
    assert result.description == "Lunch"
    assert result.category == ExpenseCategory.FOOD
    assert result.expense_date == date(2026, 9, 9)




def test_find_all_expenses(test_user) -> None:
    repository = ExpenseRepository()

    expense = Expense(
        user_id=test_user.id,
        amount=Decimal("500.00"),
        description="Uber",
        category=ExpenseCategory.TRAVEL,
        expense_date=date(2026, 9, 8),
    )

    repository.save(expense)

    result = repository.find_all(test_user.id)

    assert len(result) >= 1

    saved_expense = next(
        item
        for item in result
        if item.id == expense.id
    )

    assert saved_expense.amount == Decimal("500.00")
    assert saved_expense.description == "Uber"
    assert saved_expense.category == ExpenseCategory.TRAVEL
    assert saved_expense.expense_date == date(2026, 9, 8)
    