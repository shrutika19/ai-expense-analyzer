from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4
import pytest

from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)
from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)
from expense_analyzer.preprocessing.pipeline import (
    PreprocessingPipeline,
)
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
from expense_analyzer.services.expense_service import (
    ExpenseService,
)
from expense_analyzer.exceptions.api import (
    CategoryPredictionLowConfidenceException,
    ExpenseNotFoundException,
)
from expense_analyzer.domain.enums.category_source import CategorySource
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionOutput,
)

class FakeExpenseRepository:

    def save(self, expense: Expense) -> Expense:
        return expense

    def find_all(
        self,
        user_id: UUID,
    ) -> list[Expense]:
        return []

    def find_by_id(
        self,
        expense_id: UUID,
        user_id: UUID,
    ) -> Expense | None:
        return None

class FakeInferenceService:
    confidence_threshold = 0.70
    model_version = "v1.0.0"

    def predict(self, prediction):
        raise AssertionError(
            "ML prediction should not run for manual categories."
        )


class SuccessfulInferenceService:
    confidence_threshold = 0.70
    model_version = "v1.0.0"

    def predict(self, prediction):
        return CategoryPredictionOutput(
            predicted_category="Transport",
            confidence=0.92,
        )


class LowConfidenceInferenceService:
    confidence_threshold = 0.70
    model_version = "v1.0.0"

    def predict(self, prediction):
        return CategoryPredictionOutput(
            predicted_category="Transport",
            confidence=0.45,
        )


def create_service() -> ExpenseService:
    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )

    return ExpenseService(
        preprocessing_pipeline=pipeline,
        repository=FakeExpenseRepository(),
        inference_service=FakeInferenceService(),
    )


def test_create_expense() -> None:
    user_id = uuid4()
    service = create_service()

    request = ExpenseCreateRequest(
        amount="250.50",
        description="Lunch",
        category=ExpenseCategory.FOOD,
        expense_date="2026-09-09",
    )

    result = service.create_expense(
        request,
        user_id=user_id,
    )

    assert result.id is not None
    assert result.user_id == user_id
    assert result.amount == Decimal("250.50")
    assert result.description == "Lunch"
    assert result.category == ExpenseCategory.FOOD
    assert result.expense_date == date(2026, 9, 9)



def test_process_records_ignores_duplicates() -> None:
    service = create_service()
    user_id = uuid4()

    records = [
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "250.50",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
    ]

    result = service.process_records(
        records,
        user_id=user_id,
    )

    assert len(result) == 1

    assert result[0].id is not None
    assert result[0].user_id == user_id
    assert result[0].amount == Decimal("250.50")
    assert result[0].description == "Lunch"
    assert result[0].category == ExpenseCategory.FOOD
    assert result[0].expense_date == date(2026, 9, 9)


def test_process_multiple_records() -> None:
    service = create_service()
    user_id = uuid4()

    records = [
        {
            "amount": "100.00",
            "description": "Lunch",
            "category": "Food",
            "expense_date": "2026-09-09",
        },
        {
            "amount": "500.00",
            "description": "Uber",
            "category": "Travel",
            "expense_date": "2026-09-08",
        },
    ]

    result = service.process_records(
        records,
        user_id=user_id,
    )

    assert len(result) == 2

    assert result[0].user_id == user_id
    assert result[0].amount == Decimal("100.00")
    assert result[0].description == "Lunch"
    assert result[0].category == ExpenseCategory.FOOD

    assert result[1].user_id == user_id
    assert result[1].amount == Decimal("500.00")
    assert result[1].description == "Uber"
    assert result[1].category == ExpenseCategory.TRAVEL


def test_process_empty_records() -> None:
    service = create_service()
    user_id = uuid4()

    result = service.process_records(
        [],
        user_id=user_id,
    )

    assert result == []


def test_get_expenses() -> None:
    user_id = uuid4()
    service = create_service()

    result = service.get_expenses(user_id)

    assert result == []


def test_get_expense_not_found() -> None:
    user_id = uuid4()
    expense_id = uuid4()

    service = create_service()

    try:
        service.get_expense(
            expense_id,
            user_id,
        )
    except ExpenseNotFoundException:
        pass
    else:
        raise AssertionError(
            "Expected ExpenseNotFoundException"
        )


def test_create_expense_predicts_category_when_missing() -> None:
    user_id = uuid4()

    pipeline = PreprocessingPipeline(
        processors=[
            NormalizationProcessor(),
            MissingValueProcessor(),
            AmountNormalizationProcessor(),
            DateNormalizationProcessor(),
            DuplicateDetectionProcessor(),
        ]
    )

    service = ExpenseService(
        preprocessing_pipeline=pipeline,
        repository=FakeExpenseRepository(),
        inference_service=SuccessfulInferenceService(),
    )

    request = ExpenseCreateRequest(
        amount="250.50",
        description="Uber ride",
        expense_date="2026-09-09",
    )

    result = service.create_expense(
        request,
        user_id=user_id,
    )

    assert result.category == ExpenseCategory.TRANSPORT
    assert result.category_source == CategorySource.ML
    assert result.category_confidence == 0.92
    assert result.model_version == "v1.0.0"


def test_create_expense_rejects_low_confidence_prediction() -> None:
    service = ExpenseService(
        preprocessing_pipeline=...,
        repository=FakeExpenseRepository(),
        inference_service=LowConfidenceInferenceService(),
    )

    request = ExpenseCreateRequest(
        amount="250.00",
        description="Something unclear",
        expense_date="2026-09-09",
        category=None,
    )

    with pytest.raises(
        CategoryPredictionLowConfidenceException
    ):
        service.create_expense(
            request=request,
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
        )