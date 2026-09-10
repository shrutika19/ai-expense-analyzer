from pathlib import Path

from expense_analyzer.ingestion.strategies.base import IngestionStrategy
from expense_analyzer.ingestion.strategies.csv_strategy import (
    CSVIngestionStrategy,
)
from expense_analyzer.ingestion.strategies.json_strategy import (
    JSONIngestionStrategy,
)
from expense_analyzer.exceptions.expense_import import (
    UnsupportedFileTypeException,
)


class IngestionStrategyFactory:

    @staticmethod
    def get_strategy(file_path: str | Path) -> IngestionStrategy:
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return CSVIngestionStrategy()

        if suffix == ".json":
            return JSONIngestionStrategy()

        raise UnsupportedFileTypeException(suffix)

    @staticmethod
    def create(file_path: str | Path) -> IngestionStrategy:
        return IngestionStrategyFactory.get_strategy(file_path)