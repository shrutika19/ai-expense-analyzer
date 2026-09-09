#Given a file type, select the appropriate ingestion strategy.
from pathlib import Path

from expense_analyzer.ingestion.strategies.base import IngestionStrategy
from expense_analyzer.ingestion.strategies.csv_strategy import (
    CSVIngestionStrategy,
)
from expense_analyzer.ingestion.strategies.json_strategy import (
    JSONIngestionStrategy,
)


class IngestionStrategyFactory:

    @staticmethod
    def create(file_path: str) -> IngestionStrategy:
        extension = Path(file_path).suffix.lower()

        strategies = {
            ".csv": CSVIngestionStrategy,
            ".json": JSONIngestionStrategy,
        }

        strategy_class = strategies.get(extension)

        if strategy_class is None:
            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        return strategy_class()