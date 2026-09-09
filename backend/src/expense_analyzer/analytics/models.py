from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ExpenseSummary:
    total_amount: Decimal
    expense_count: int
    average_amount: Decimal
    highest_amount: Decimal | None
    lowest_amount: Decimal | None


@dataclass(frozen=True)
class CategorySummary:
    category: str
    total_amount: Decimal
    expense_count: int


@dataclass(frozen=True)
class MonthlySummary:
    month: str
    total_amount: Decimal
    expense_count: int