from datetime import date
from decimal import Decimal

from expense_analyzer.analytics.calculators.category import (
    CategoryCalculator,
)
from expense_analyzer.analytics.calculators.monthly import (
    MonthlyCalculator,
)
from expense_analyzer.analytics.calculators.summary import (
    SummaryCalculator,
)
from expense_analyzer.analytics.service import AnalyticsService
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.preprocessing.processors.amount import (
    AmountNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.date import (
    DateNormalizationProcessor,
)
from expense_analyzer.preprocessing.processors.duplicate import (
    DuplicateDetectionProcessor,
)
from expense_analyzer.preprocessing.processors.missing_value import (
    MissingValueProcessor,
)
from expense_analyzer.preprocessing.processors.normalization import (
    NormalizationProcessor,
)
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)


def create_pipeline() -> PreprocessingPipeline:
    return PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )


def create_analytics_service() -> AnalyticsService:
    return AnalyticsService(
        summary_calculator=SummaryCalculator(),
        category_calculator=CategoryCalculator(),
        monthly_calculator=MonthlyCalculator(),
    )


def convert_to_expenses(
    records: list[dict],
) -> list[Expense]:
    expenses = []

    for record in records:
        if record["_is_duplicate"]:
            continue

        expense_record = {
            key: value
            for key, value in record.items()
            if key != "_is_duplicate"
        }
        validated = ExpenseValidationModel.model_validate(expense_record)

        expenses.append(
            Expense(
                amount=validated.amount,
                description=validated.description,
                category=validated.category,
                expense_date=validated.expense_date,
            )
        )

    return expenses




def test_preprocessing_validation_and_analytics_flow() -> None:
    records = [
        {
            " amount ": " 100.00 ",
            "description": " Lunch ",
            "category": " Food ",
            "expense_date": "09/09/2026",
        },
        {
            "amount": "200.00",
            "description": "Uber",
            "category": "Travel",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    ]

    pipeline = create_pipeline()

    processed_records = pipeline.process(records)

    expenses = convert_to_expenses(processed_records)

    service = create_analytics_service()

    summary = service.get_summary(expenses)
    category_summary = service.get_category_summary(expenses)
    monthly_summary = service.get_monthly_summary(expenses)

    assert len(expenses) == 2

    assert summary.total_amount == Decimal("300.00")
    assert summary.expense_count == 2
    assert summary.average_amount == Decimal("150.00")
    assert summary.highest_amount == Decimal("200.00")
    assert summary.lowest_amount == Decimal("100.00")

    food = next(
        item
        for item in category_summary
        if item.category == "Food"
    )

    travel = next(
        item
        for item in category_summary
        if item.category == "Travel"
    )

    assert food.total_amount == Decimal("100.00")
    assert food.expense_count == 1

    assert travel.total_amount == Decimal("200.00")
    assert travel.expense_count == 1

    september = next(
        item
        for item in monthly_summary
        if item.month == "2026-09"
    )

    assert september.total_amount == Decimal("300.00")
    assert september.expense_count == 2