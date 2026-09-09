from datetime import date, datetime
from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class DateNormalizationProcessor(PreprocessingProcessor):

    DATE_FORMATS = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
    )

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        processed_records: list[dict[str, Any]] = []

        for record in records:
            processed_record = record.copy()

            if "expense_date" in processed_record:
                processed_record["expense_date"] = (
                    self._normalize_date(
                        processed_record["expense_date"]
                    )
                )

            processed_records.append(processed_record)

        return processed_records

    @classmethod
    def _normalize_date(
        cls,
        value: Any,
    ) -> date | None:
        if value is None:
            return None

        if isinstance(value, date):
            return value

        if not isinstance(value, str):
            raise ValueError(
                f"Invalid expense date: {value}"
            )

        value = value.strip()

        for date_format in cls.DATE_FORMATS:
            try:
                return datetime.strptime(
                    value,
                    date_format,
                ).date()
            except ValueError:
                continue

        raise ValueError(
            f"Invalid expense date: {value}"
        )