from datetime import date
from typing import Literal
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
    predicted_category: ExpenseCategory | None
    category_confidence: float | None
    model_version: str | None


class ExpenseCategoryCorrectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: ExpenseCategory


class ExpenseTableRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search: str = Field(default="", max_length=200)
    category: ExpenseCategory | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: Literal["expense_date", "description", "category", "amount"] = "expense_date"
    sort_direction: Literal["asc", "desc"] = "desc"


class ExpenseTableResponse(BaseModel):
    items: list[ExpenseResponse]
    total_count: int
    page: int
    page_size: int
