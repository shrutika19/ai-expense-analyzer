from collections import defaultdict
from decimal import Decimal

from expense_analyzer.analytics.models import MonthlySummary
from expense_analyzer.domain.entities.expense import Expense


class MonthlyCalculator:

    def calculate(
        self,
        expenses: list[Expense],
    ) -> list[MonthlySummary]:

        totals: dict[str, Decimal] = defaultdict(
            lambda: Decimal("0")
        )

        counts: dict[str, int] = defaultdict(int)

        for expense in expenses:
            month = expense.expense_date.strftime("%Y-%m")

            totals[month] += expense.amount
            counts[month] += 1

        return [
            MonthlySummary(
                month=month,
                total_amount=totals[month],
                expense_count=counts[month],
            )
            for month in sorted(totals)
        ]