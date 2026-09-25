from typing import Any
from uuid import UUID

from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
    CategoryPredictionLowConfidenceException,
)
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)
from expense_analyzer.ml.inference.service import (
    ConfidenceLevel,
    InferenceService,
)
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)
from expense_analyzer.domain.enums.category_source import (
    CategorySource,
)
from expense_analyzer.domain.enums.expense_category import (
    ExpenseCategory,
)

class ExpenseService:

    def __init__(
        self,
        preprocessing_pipeline: PreprocessingPipeline,
        repository: ExpenseRepository,
        inference_service: InferenceService,
    ) -> None:
        self.preprocessing_pipeline = preprocessing_pipeline
        self.repository = repository
        self.inference_service = inference_service

    def create_expense(
        self,
        request: ExpenseCreateRequest,
        user_id: UUID,
    ) -> Expense:
        category = request.category
        category_source = CategorySource.MANUAL
        # Always preserve the prediction.  A manual category is ground truth,
        # not a reason to discard the model output used for comparison.
        prediction = self.inference_service.predict(
            CategoryPredictionInput(
                description=request.description,
                amount=float(request.amount),
            )
        )
        predicted_category = ExpenseCategory(prediction.predicted_category)
        category_confidence = prediction.confidence
        model_version = self.inference_service.model_version

        if category is None:
            if (
                self.inference_service.confidence_threshold is not None
                and prediction.confidence
                < self.inference_service.confidence_threshold
            ):
                raise CategoryPredictionLowConfidenceException(
                    "Category prediction confidence is below "
                    "the configured threshold."
                )

            category = predicted_category
            category_source = CategorySource.ML
            category_confidence = prediction.confidence
            model_version = self.inference_service.model_version

        expense = Expense(
            amount=request.amount,
            description=request.description,
            category=category,
            expense_date=request.expense_date,
            user_id=user_id,
            category_source=category_source,
            predicted_category=predicted_category,
            category_confidence=category_confidence,
            model_version=model_version,
        )

        return self.repository.save(expense)

    def correct_category(
        self, expense_id: UUID, category: ExpenseCategory, user_id: UUID
    ) -> Expense:
        expense = self.repository.update_category(expense_id, user_id, category)
        if expense is None:
            raise ExpenseNotFoundException(str(expense_id))
        return expense

    def process_records(
        self,
        records: list[dict[str, Any]],
        user_id: UUID,
    ) -> list[Expense]:
        processed_records = self.preprocessing_pipeline.process(
            records
        )

        expenses: list[Expense] = []

        for record in processed_records:
            if record.get("_is_duplicate", False):
                continue

            expense_record = {
                key: value
                for key, value in record.items()
                if key != "_is_duplicate"
            }

            validated_record = ExpenseValidationModel.model_validate(
                expense_record
            )

            expense = Expense(
                user_id=user_id,
                amount=validated_record.amount,
                description=validated_record.description,
                category=validated_record.category,
                expense_date=validated_record.expense_date,
            )

            expenses.append(expense)

        return expenses

    def get_expenses(
        self,
        user_id: UUID,
    ) -> list[Expense]:
        return self.repository.find_all(user_id)

    def get_expense(
        self,
        expense_id: UUID,
        user_id: UUID,
    ) -> Expense:
        expense = self.repository.find_by_id(
            expense_id,
            user_id,
        )

        if expense is None:
            raise ExpenseNotFoundException(
                str(expense_id)
            )

        return expense
