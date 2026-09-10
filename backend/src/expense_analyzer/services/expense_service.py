from typing import Any
from uuid import UUID
from expense_analyzer.api.v1.schemas.expense import (
    ExpenseCreateRequest,
)
from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.preprocessing.pipeline import PreprocessingPipeline
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.exceptions.api import (
    ExpenseNotFoundException,
)


class ExpenseService:

    def __init__(
        self,
        preprocessing_pipeline: PreprocessingPipeline,
        repository: ExpenseRepository,
    ) -> None:
        self.preprocessing_pipeline = preprocessing_pipeline
        self.repository = repository

    def create_expense(
        self,
        request: ExpenseCreateRequest,
    ) -> Expense:
        expense = Expense(
            amount=request.amount,
            description=request.description,
            category=request.category,
            expense_date=request.expense_date,
        )
    
        return self.repository.save(expense)

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

    def get_expenses(self) -> list[Expense]:
        return self.repository.find_all()

    def get_expense(self, expense_id: UUID) -> Expense:
        expense = self.repository.find_by_id(expense_id)

        if expense is None:
            raise ExpenseNotFoundException(str(expense_id))

        return expense
