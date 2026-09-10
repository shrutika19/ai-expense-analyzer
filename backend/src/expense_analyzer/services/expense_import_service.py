from pathlib import Path

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.ingestion.factory import (
    IngestionStrategyFactory,
)
from expense_analyzer.preprocessing.pipeline import (
    PreprocessingPipeline,
)
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)


class ExpenseImportService:

    def __init__(
        self,
        repository: ExpenseRepository,
        preprocessing_pipeline: PreprocessingPipeline,
    ) -> None:
        self.repository = repository
        self.preprocessing_pipeline = preprocessing_pipeline

    def import_expenses(
        self,
        file_path: Path,
    ) -> list[Expense]:

        strategy = IngestionStrategyFactory.get_strategy(
            file_path
        )

        raw_records = strategy.read(file_path)

        processed_records = self.preprocessing_pipeline.process(
            raw_records
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

            expenses.append(
                Expense(
                    amount=validated_record.amount,
                    description=validated_record.description,
                    category=validated_record.category,
                    expense_date=validated_record.expense_date,
                )
            )

        saved_expenses: list[Expense] = []

        for expense in expenses:
            saved_expenses.append(
                self.repository.save(expense)
            )

        return saved_expenses