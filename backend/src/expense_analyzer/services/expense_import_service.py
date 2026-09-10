from pathlib import Path
from dataclasses import dataclass, field

from expense_analyzer.domain.entities.expense import Expense
from expense_analyzer.ingestion.factory import (
    IngestionStrategyFactory,
)
from expense_analyzer.preprocessing.pipeline import (
    PreprocessingPipeline,
)
from expense_analyzer.preprocessing.processors.duplicate import (
    DuplicateDetectionProcessor,
)
from expense_analyzer.repositories.expense_repository import (
    ExpenseRepository,
)
from expense_analyzer.validation.validators.expense_validator import (
    ExpenseValidationModel,
)
from pydantic import ValidationError


@dataclass
class ImportResult:
    expenses: list[Expense] = field(default_factory=list)
    errors: list[dict[str, int | str]] = field(default_factory=list)
    skipped_duplicates: int = 0
    skipped_rows: list[dict[str, int | str]] = field(default_factory=list)


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
        return self.import_expenses_detailed(file_path).expenses

    def import_expenses_detailed(
        self,
        file_path: Path,
    ) -> ImportResult:

        strategy = IngestionStrategyFactory.get_strategy(
            file_path
        )

        raw_records = strategy.read(file_path)

        result = ImportResult()
        valid_records: list[dict[str, object]] = []

        for fallback_row_number, raw_record in enumerate(
            raw_records,
            start=1,
        ):
            row_number = int(
                raw_record.get("_row_number", fallback_row_number)
            )

            try:
                processed_records = self._process_row(raw_record)
                if not processed_records:
                    raise ValueError("Row produced no processed record.")

                record = processed_records[0]
                expense_record = {
                    key: value
                    for key, value in record.items()
                    if key not in {"_is_duplicate", "_row_number"}
                }

                validated_record = ExpenseValidationModel.model_validate(
                    expense_record
                )
                valid_records.append(
                    {
                        **expense_record,
                        "_row_number": row_number,
                        "_validated": validated_record,
                    }
                )
            except (ValidationError, ValueError) as exc:
                result.errors.append(
                    {
                        "row_number": row_number,
                        "reason": self._format_validation_error(exc),
                    }
                )
                continue

        duplicate_processor = DuplicateDetectionProcessor()
        marked_records = duplicate_processor.process(valid_records)

        for record in marked_records:
            row_number = int(record["_row_number"])
            if record.get("_is_duplicate", False):
                result.skipped_duplicates += 1
                result.skipped_rows.append(
                    {
                        "row_number": row_number,
                        "reason": "Duplicate expense skipped.",
                    }
                )
                continue

            validated_record = record["_validated"]
            result.expenses.append(
                Expense(
                    amount=validated_record.amount,
                    description=validated_record.description,
                    category=validated_record.category,
                    expense_date=validated_record.expense_date,
                )
            )

        result.expenses = self.repository.save_many(result.expenses)

        return result

    def _process_row(
        self,
        record: dict[str, object],
    ) -> list[dict[str, object]]:
        processors = getattr(self.preprocessing_pipeline, "processors", None)
        if isinstance(processors, list):
            row_pipeline = PreprocessingPipeline(
                processors=[
                    processor
                    for processor in processors
                    if not isinstance(
                        processor,
                        DuplicateDetectionProcessor,
                    )
                ]
            )
            return row_pipeline.process([record])

        return self.preprocessing_pipeline.process([record])

    @staticmethod
    def _format_validation_error(exc: Exception) -> str:
        if isinstance(exc, ValidationError):
            return "; ".join(
                error["msg"]
                for error in exc.errors()
            )

        return str(exc)