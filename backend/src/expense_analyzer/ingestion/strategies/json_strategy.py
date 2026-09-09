import json
from pathlib import Path
from typing import Any

from expense_analyzer.ingestion.strategies.base import IngestionStrategy


class JSONIngestionStrategy(IngestionStrategy):

    def read(self, source: Any) -> list[dict[str, Any]]:
        path = Path(source)

        with path.open(mode="r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("JSON expense data must be an array.")

        return data