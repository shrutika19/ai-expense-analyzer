from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class MissingValueProcessor(PreprocessingProcessor):

    MISSING_VALUES = {
        "",
        "null",
        "none",
        "n/a",
        "na",
        "nan",
    }

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        processed_records = []

        for record in records:
            processed_record = {
                key: self._normalize_missing_value(value)
                for key, value in record.items()
            }

            processed_records.append(processed_record)

        return processed_records

    @classmethod
    def _normalize_missing_value(cls, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            normalized_value = value.strip().lower()

            if normalized_value in cls.MISSING_VALUES:
                return None

        return value