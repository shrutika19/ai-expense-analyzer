from decimal import Decimal

from expense_analyzer.analytics.models import ExpenseSummary
from expense_analyzer.domain.entities.expense import Expense


class SummaryCalculator:

    def calculate(
        self,
        expenses: list[Expense],
    ) -> ExpenseSummary:

        if not expenses:
            return ExpenseSummary(
                total_amount=Decimal("0"),
                expense_count=0,
                average_amount=Decimal("0"),
                highest_amount=None,
                lowest_amount=None,
            )

        total_amount = sum(
            (expense.amount for expense in expenses),
            Decimal("0"),
        )

        expense_count = len(expenses)

        average_amount = (
            total_amount / expense_count
        )

        highest_amount = max(
            expense.amount for expense in expenses
        )

        lowest_amount = min(
            expense.amount for expense in expenses
        )

        return ExpenseSummary(
            total_amount=total_amount,
            expense_count=expense_count,
            average_amount=average_amount,
            highest_amount=highest_amount,
            lowest_amount=lowest_amount,
        )