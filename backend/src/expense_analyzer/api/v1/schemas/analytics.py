from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ExpenseSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_amount: Decimal
    expense_count: int
    average_amount: Decimal
    highest_amount: Decimal | None
    lowest_amount: Decimal | None


class CategorySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    total_amount: Decimal
    expense_count: int


class MonthlySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    total_amount: Decimal
    expense_count: int