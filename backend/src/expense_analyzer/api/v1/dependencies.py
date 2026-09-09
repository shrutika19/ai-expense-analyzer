from fastapi import Depends

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


def get_expense_service(
    pipeline: PreprocessingPipeline = Depends(
        get_preprocessing_pipeline
    ),
) -> ExpenseService:
    return ExpenseService(
        preprocessing_pipeline=pipeline,
    )