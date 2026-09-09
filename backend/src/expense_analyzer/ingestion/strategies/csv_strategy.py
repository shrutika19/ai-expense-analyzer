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
            return list(reader)