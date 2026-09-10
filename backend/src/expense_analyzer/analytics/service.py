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
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)


class AnalyticsService:

    def __init__(
        self,
        summary_calculator: SummaryCalculator,
        category_calculator: CategoryCalculator,
        monthly_calculator: MonthlyCalculator,
        repository: ExpenseRepository,
    ) -> None:
        self.summary_calculator = summary_calculator
        self.category_calculator = category_calculator
        self.monthly_calculator = monthly_calculator
        self.repository = repository

    def get_summary(self) -> ExpenseSummary:
        expenses = self.repository.find_all()

        return self.summary_calculator.calculate(expenses)

    def get_category_summary(self) -> list[CategorySummary]:
        expenses = self.repository.find_all()

        return self.category_calculator.calculate(expenses)

    def get_monthly_summary(self) -> list[MonthlySummary]:
        expenses = self.repository.find_all()

        return self.monthly_calculator.calculate(expenses)