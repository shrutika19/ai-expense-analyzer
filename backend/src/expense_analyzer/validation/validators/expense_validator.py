from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from expense_analyzer.domain.enums.expense_category import ExpenseCategory


class ExpenseValidationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1)
    category: ExpenseCategory
    expense_date: date

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(
        cls,
        value: ExpenseCategory | str | None,
    ) -> ExpenseCategory | str | None:
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return ExpenseCategory[value]
            except KeyError:
                return value

        return value
