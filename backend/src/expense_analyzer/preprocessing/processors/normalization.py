#Make equivalent input representations consistent.

from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class NormalizationProcessor(PreprocessingProcessor):

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized_records = []

        for record in records:
            normalized_record = {
                key.strip(): self._normalize_value(value)
                for key, value in record.items()
            }

            normalized_records.append(normalized_record)

        return normalized_records

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()

        return value