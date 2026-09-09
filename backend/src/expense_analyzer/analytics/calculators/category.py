from collections import defaultdict
from decimal import Decimal

from expense_analyzer.analytics.models import CategorySummary
from expense_analyzer.domain.entities.expense import Expense


class CategoryCalculator:

    def calculate(
        self,
        expenses: list[Expense],
    ) -> list[CategorySummary]:

        totals: dict[str, Decimal] = defaultdict(
            lambda: Decimal("0")
        )

        counts: dict[str, int] = defaultdict(int)

        for expense in expenses:
            category = expense.category.value

            totals[category] += expense.amount
            counts[category] += 1

        return [
            CategorySummary(
                category=category,
                total_amount=totals[category],
                expense_count=counts[category],
            )
            for category in sorted(totals)
        ]