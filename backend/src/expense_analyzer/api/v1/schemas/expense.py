from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from expense_analyzer.domain.enums.expense_category import ExpenseCategory


class ExpenseCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    description: str = Field(
        min_length=1,
        max_length=500,
    )
    category: ExpenseCategory
    expense_date: date


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    description: str
    category: ExpenseCategory
    expense_date: date