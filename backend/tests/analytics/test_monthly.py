from datetime import date
from decimal import Decimal

from expense_analyzer.analytics.calculators.monthly import (
    MonthlyCalculator,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory


def test_monthly_calculation() -> None:
    calculator = MonthlyCalculator()

    expenses = [
        Expense(
            amount=Decimal("100.00"),
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 1, 10),
        ),
        Expense(
            amount=Decimal("200.00"),
            description="Uber",
            category=ExpenseCategory.TRAVEL,
            expense_date=date(2026, 1, 20),
        ),
        Expense(
            amount=Decimal("500.00"),
            description="Shopping",
            category=ExpenseCategory.SHOPPING,
            expense_date=date(2026, 2, 5),
        ),
    ]

    result = calculator.calculate(expenses)

    assert len(result) == 2

    january = next(
        item for item in result
        if item.month == "2026-01"
    )

    february = next(
        item for item in result
        if item.month == "2026-02"
    )

    assert january.total_amount == Decimal("300.00")
    assert january.expense_count == 2

    assert february.total_amount == Decimal("500.00")
    assert february.expense_count == 1


def test_empty_expenses_return_empty_monthly_summary() -> None:
    calculator = MonthlyCalculator()

    result = calculator.calculate([])

    assert result == []