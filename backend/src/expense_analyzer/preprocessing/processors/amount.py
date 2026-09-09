from decimal import Decimal, InvalidOperation
from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class AmountNormalizationProcessor(PreprocessingProcessor):

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        processed_records: list[dict[str, Any]] = []

        for record in records:
            processed_record = record.copy()

            if "amount" in processed_record:
                processed_record["amount"] = self._normalize_amount(
                    processed_record["amount"]
                )

            processed_records.append(processed_record)

        return processed_records

    @staticmethod
    def _normalize_amount(value: Any) -> Decimal | None:
        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        if isinstance(value, str):
            value = value.strip()
            value = value.replace(",", "")
            value = value.replace("₹", "")
            value = value.strip()

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"Invalid expense amount: {value}"
            )