from datetime import date
from decimal import Decimal

from expense_analyzer.analytics.calculators.category import (
    CategoryCalculator,
)
from expense_analyzer.analytics.calculators.monthly import (
    MonthlyCalculator,
)
from expense_analyzer.analytics.calculators.summary import (
    SummaryCalculator,
)
from expense_analyzer.analytics.service import AnalyticsService
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
            description="Dinner",
            category=ExpenseCategory.FOOD,
            expense_date=date(2026, 10, 1),
        ),
    ]


def create_service() -> AnalyticsService:
    return AnalyticsService(
        summary_calculator=SummaryCalculator(),
        category_calculator=CategoryCalculator(),
        monthly_calculator=MonthlyCalculator(),
    )



def test_get_summary() -> None:
    service = create_service()

    result = service.get_summary(create_expenses())

    assert result.total_amount == Decimal("600.00")
    assert result.expense_count == 3
    assert result.average_amount == Decimal("200.00")
    assert result.highest_amount == Decimal("300.00")
    assert result.lowest_amount == Decimal("100.00")



def test_get_category_summary() -> None:
    service = create_service()

    result = service.get_category_summary(create_expenses())

    assert len(result) == 2

    food = next(
        item for item in result
        if item.category == "Food"
    )

    travel = next(
        item for item in result
        if item.category == "Travel"
    )

    assert food.total_amount == Decimal("400.00")
    assert food.expense_count == 2

    assert travel.total_amount == Decimal("200.00")
    assert travel.expense_count == 1


def test_get_monthly_summary() -> None:
    service = create_service()

    result = service.get_monthly_summary(create_expenses())

    assert len(result) == 2

    september = next(
        item for item in result
        if item.month == "2026-09"
    )

    october = next(
        item for item in result
        if item.month == "2026-10"
    )

    assert september.total_amount == Decimal("300.00")
    assert september.expense_count == 2

    assert october.total_amount == Decimal("300.00")
    assert october.expense_count == 1



def test_service_handles_empty_expenses() -> None:
    service = create_service()

    summary = service.get_summary([])

    assert summary.total_amount == Decimal("0")
    assert summary.expense_count == 0
    assert summary.average_amount == Decimal("0")
    assert summary.highest_amount is None
    assert summary.lowest_amount is None

    category_summary = service.get_category_summary([])

    assert category_summary == []

    monthly_summary = service.get_monthly_summary([])

    assert monthly_summary == []