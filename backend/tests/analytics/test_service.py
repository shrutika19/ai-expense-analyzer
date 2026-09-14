from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4


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
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)


def create_service(
    repository: ExpenseRepository,
) -> AnalyticsService:
    return AnalyticsService(
        summary_calculator=SummaryCalculator(),
        category_calculator=CategoryCalculator(),
        monthly_calculator=MonthlyCalculator(),
        repository=repository,
    )


def test_get_summary() -> None:
    user_id = uuid4()
    expenses = [
        Expense(
            user_id=user_id,
            amount=Decimal("100.00"),
            description="Food",
            category=ExpenseCategory.FOOD,
            expense_date=__import__("datetime").date(
                2026,
                1,
                10,
            ),
        ),
        Expense(
            user_id=user_id,
            amount=Decimal("200.00"),
            description="Transport",
            category=ExpenseCategory.TRANSPORT,
            expense_date=__import__("datetime").date(
                2026,
                1,
                15,
            ),
        ),
    ]

    repository = Mock(spec=ExpenseRepository)
    repository.find_all.return_value = expenses

    service = create_service(repository)

    result = service.get_summary(user_id)

    assert result.total_amount == Decimal("300.00")
    assert result.expense_count == 2
    repository.find_all.assert_called_once_with(user_id)

def test_get_category_summary() -> None:
    user_id = uuid4()
    expenses = [
        Expense(
            user_id=user_id,
            amount=Decimal("100.00"),
            description="Food",
            category=ExpenseCategory.FOOD,
            expense_date=__import__("datetime").date(
                2026,
                1,
                10,
            ),
        ),
        Expense(
            user_id=user_id,
            amount=Decimal("50.00"),
            description="Food",
            category=ExpenseCategory.FOOD,
            expense_date=__import__("datetime").date(
                2026,
                1,
                11,
            ),
        ),
    ]

    repository = Mock(spec=ExpenseRepository)
    repository.find_all.return_value = expenses

    service = create_service(repository)

    result = service.get_category_summary(user_id)

    assert len(result) == 1
    assert result[0].category == ExpenseCategory.FOOD.value
    assert result[0].total_amount == Decimal("150.00")
    assert result[0].expense_count == 2
    repository.find_all.assert_called_once_with(user_id)


def test_get_monthly_summary() -> None:
    user_id = uuid4()
    expenses = [
        Expense(
            user_id=user_id,
            amount=Decimal("100.00"),
            description="Food",
            category=ExpenseCategory.FOOD,
            expense_date=__import__("datetime").date(
                2026,
                1,
                10,
            ),
        ),
        Expense(
            user_id=user_id,
            amount=Decimal("200.00"),
            description="Transport",
            category=ExpenseCategory.TRANSPORT,
            expense_date=__import__("datetime").date(
                2026,
                2,
                15,
            ),
        ),
    ]

    repository = Mock(spec=ExpenseRepository)
    repository.find_all.return_value = expenses

    service = create_service(repository)

    result = service.get_monthly_summary(user_id)

    assert len(result) == 2
    assert result[0].month == "2026-01"
    assert result[1].month == "2026-02"
    repository.find_all.assert_called_once_with(user_id)