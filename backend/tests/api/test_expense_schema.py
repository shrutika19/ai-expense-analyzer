from datetime import date
from decimal import Decimal

from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.enums.expense_category import ExpenseCategory


def test_valid_expense_request() -> None:
    request = ExpenseCreateRequest(
        amount="250.50",
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date="2026-09-09",
    )

    assert request.amount == Decimal("250.50")
    assert request.description == "Lunch"
    assert request.category == ExpenseCategory.FOOD
    assert request.expense_date == date(2026, 9, 9)

import pytest
from pydantic import ValidationError


def test_expense_request_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        ExpenseCreateRequest(
            amount="0",
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date="2026-09-09",
        )

def test_expense_request_rejects_invalid_category() -> None:
    with pytest.raises(ValidationError):
        ExpenseCreateRequest(
            amount="250.50",
            description="Lunch",
            category="InvalidCategory",
            expense_date="2026-09-09",
        )


def test_expense_request_rejects_missing_description() -> None:
    with pytest.raises(ValidationError):
        ExpenseCreateRequest(
            amount="250.50",
            category=ExpenseCategory.FOOD,
            expense_date="2026-09-09",
        )



def test_expense_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ExpenseCreateRequest(
            amount="250.50",
            description="Lunch",
            category=ExpenseCategory.FOOD,
            expense_date="2026-09-09",
            unexpected_field="value",
        )