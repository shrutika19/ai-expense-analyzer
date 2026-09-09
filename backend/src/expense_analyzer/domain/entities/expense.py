from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.exceptions.domain import InvalidExpenseException


@dataclass
class Expense:
    amount: Decimal
    description: str
    category: ExpenseCategory
    expense_date: date
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise InvalidExpenseException(
                "Expense amount must be greater than zero."
            )

        if not self.description.strip():
            raise InvalidExpenseException(
                "Expense description cannot be empty."
            )