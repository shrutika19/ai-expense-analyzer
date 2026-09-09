from datetime import date
from decimal import Decimal

from expense_analyzer.analytics.calculators.summary import (
    SummaryCalculator,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory


def create_expenses() -> list[Expense]:
    return [
        Expense(
            amount=Decimal("100.00"),
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 9, 1),
        ),
        Expense(
            amount=Decimal("200.00"),
            description="Uber",
            category=ExpenseCategory.TRAVEL,
            expense_date=date(2026, 9, 2),
        ),
        Expense(
            amount=Decimal("300.00"),
            description="Shopping",
            category=ExpenseCategory.SHOPPING,
            expense_date=date(2026, 9, 3),
        ),
    ]


def test_summary_calculation() -> None:
    calculator = SummaryCalculator()

    result = calculator.calculate(create_expenses())

    assert result.total_amount == Decimal("600.00")
    assert result.expense_count == 3
    assert result.average_amount == Decimal("200.00")
    assert result.highest_amount == Decimal("300.00")
    assert result.lowest_amount == Decimal("100.00")


def test_empty_expenses_return_zero_summary() -> None:
    calculator = SummaryCalculator()

    result = calculator.calculate([])

    assert result.total_amount == Decimal("0")
    assert result.expense_count == 0
    assert result.average_amount == Decimal("0")
    assert result.highest_amount is None
    assert result.lowest_amount is None