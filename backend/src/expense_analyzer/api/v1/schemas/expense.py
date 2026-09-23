from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.domain.enums.category_source import (
    CategorySource,
)

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
    category: ExpenseCategory | None = None
    expense_date: date

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: ExpenseCategory | str) -> ExpenseCategory | str:
        if isinstance(value, str):
            try:
                return ExpenseCategory[value]
            except KeyError:
                return value

        return value


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    description: str
    category: ExpenseCategory | None = None
    expense_date: date
    category_source: CategorySource
    category_confidence: float | None
    model_version: str | None