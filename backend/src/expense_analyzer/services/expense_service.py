from typing import Any

from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)


class ExpenseService:

    def __init__(
        self,
        preprocessing_pipeline: PreprocessingPipeline,
    ) -> None:
        self.preprocessing_pipeline = preprocessing_pipeline

    def create_expense(
        self,
        request: ExpenseCreateRequest,
    ) -> Expense:
        return Expense(
            amount=request.amount,
            description=request.description,
            category=request.category,
            expense_date=request.expense_date,
        )

    def process_records(
        self,
        records: list[dict[str, Any]],
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
                amount=validated_record.amount,
                description=validated_record.description,
                category=validated_record.category,
                expense_date=validated_record.expense_date,
            )

            expenses.append(expense)

        return expenses