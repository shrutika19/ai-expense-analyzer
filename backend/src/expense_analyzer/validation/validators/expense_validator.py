from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from expense_analyzer.domain.enums.expense_category import ExpenseCategory


class ExpenseValidationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1)
    category: ExpenseCategory
    expense_date: date