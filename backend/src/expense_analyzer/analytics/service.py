from expense_analyzer.analytics.calculators.category import (
    CategoryCalculator,
)
from expense_analyzer.analytics.calculators.monthly import (
    MonthlyCalculator,
)
from expense_analyzer.analytics.calculators.summary import (
    SummaryCalculator,
)
from expense_analyzer.analytics.models import (
    CategorySummary,
    ExpenseSummary,
    MonthlySummary,
)
from expense_analyzer.domain.entities.expense import Expense


class AnalyticsService:

    def __init__(
        self,
        summary_calculator: SummaryCalculator,
        category_calculator: CategoryCalculator,
        monthly_calculator: MonthlyCalculator,
    ) -> None:
        self.summary_calculator = summary_calculator
        self.category_calculator = category_calculator
        self.monthly_calculator = monthly_calculator

    def get_summary(
        self,
        expenses: list[Expense],
    ) -> ExpenseSummary:
        return self.summary_calculator.calculate(expenses)

    def get_category_summary(
        self,
        expenses: list[Expense],
    ) -> list[CategorySummary]:
        return self.category_calculator.calculate(expenses)

    def get_monthly_summary(
        self,
        expenses: list[Expense],
    ) -> list[MonthlySummary]:
        return self.monthly_calculator.calculate(expenses)