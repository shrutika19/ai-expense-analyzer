#Read CSV input and convert it into raw Python records.
import csv
from pathlib import Path
from typing import Any

from expense_analyzer.ingestion.strategies.base import IngestionStrategy


class CSVIngestionStrategy(IngestionStrategy):

    def read(self, source: Any) -> list[dict[str, Any]]:
        path = Path(source)

        with path.open(mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required_fields = {
                "amount",
                "description",
                "category",
                "expense_date",
            }
            fieldnames = {
                field.strip()
                for field in (reader.fieldnames or [])
                if field is not None
            }

            missing_fields = required_fields - fieldnames
            if missing_fields:
                missing = ", ".join(sorted(missing_fields))
                raise ValueError(
                    f"CSV is missing required columns: {missing}."
                )

            records: list[dict[str, Any]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"CSV row {row_number} has too many columns."
                    )

                normalized_row = {
                    key.strip() if key else key: value
                    for key, value in row.items()
                }
                normalized_row["_row_number"] = row_number
                records.append(normalized_row)

            return records