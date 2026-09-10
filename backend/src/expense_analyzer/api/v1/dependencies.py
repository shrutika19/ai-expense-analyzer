from fastapi import Depends

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
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.services.expense_import_service import (
    ExpenseImportService,
)
from expense_analyzer.services.expense_service import ExpenseService


def get_preprocessing_pipeline() -> PreprocessingPipeline:
    return PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )


def get_expense_repository() -> ExpenseRepository:
    return ExpenseRepository()


def get_expense_service(
    pipeline: PreprocessingPipeline = Depends(
        get_preprocessing_pipeline
    ),
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
) -> ExpenseService:
    return ExpenseService(
        preprocessing_pipeline=pipeline,
        repository=repository,
    )


def get_analytics_service(
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
) -> AnalyticsService:
    return AnalyticsService(
        summary_calculator=SummaryCalculator(),
        category_calculator=CategoryCalculator(),
        monthly_calculator=MonthlyCalculator(),
        repository=repository,
    )

def get_expense_import_service(
    repository: ExpenseRepository = Depends(
        get_expense_repository
    ),
    pipeline: PreprocessingPipeline = Depends(
        get_preprocessing_pipeline
    ),
) -> ExpenseImportService:
    return ExpenseImportService(
        repository=repository,
        preprocessing_pipeline=pipeline,
    )