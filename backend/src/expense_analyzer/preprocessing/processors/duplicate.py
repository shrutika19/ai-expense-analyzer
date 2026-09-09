from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class DuplicateDetectionProcessor(PreprocessingProcessor):

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seen: set[tuple[Any, ...]] = set()
        processed_records: list[dict[str, Any]] = []

        for record in records:
            fingerprint = self._create_fingerprint(record)

            if fingerprint in seen:
                duplicate_record = record.copy()
                duplicate_record["_is_duplicate"] = True
                processed_records.append(duplicate_record)
                continue

            seen.add(fingerprint)

            processed_record = record.copy()
            processed_record["_is_duplicate"] = False
            processed_records.append(processed_record)

        return processed_records

    @staticmethod
    def _create_fingerprint(
        record: dict[str, Any],
    ) -> tuple[Any, ...]:
        return (
            record.get("amount"),
            record.get("description"),
            record.get("category"),
            record.get("expense_date"),
        )