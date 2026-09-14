from datetime import date
from decimal import Decimal
from uuid import uuid4

from expense_analyzer.analytics.calculators.category import (
    CategoryCalculator,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory


def test_category_calculation() -> None:
    calculator = CategoryCalculator()
    user_id = uuid4()

    expenses = [
        Expense(
            user_id=user_id,
            amount=Decimal("100.00"),
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 1),
        ),
        Expense(
            user_id=user_id,
            amount=Decimal("200.00"),
            description="Dinner",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 2),
        ),
        Expense(
            user_id=user_id,
            amount=Decimal("500.00"),
            description="Uber",
            category=ExpenseCategory.TRAVEL,
            expense_date=date(2026, 9, 3),
        ),
    ]

    result = calculator.calculate(expenses)

    assert len(result) == 2

    food = next(
        item for item in result
        if item.category == "Food"
    )

    travel = next(
        item for item in result
        if item.category == "Travel"
    )

    assert food.total_amount == Decimal("300.00")
    assert food.expense_count == 2

    assert travel.total_amount == Decimal("500.00")
    assert travel.expense_count == 1