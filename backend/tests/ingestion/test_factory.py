from pathlib import Path

import pytest

from expense_analyzer.ingestion.factory import IngestionStrategyFactory
from expense_analyzer.ingestion.strategies.csv_strategy import (
    CSVIngestionStrategy,
)
from expense_analyzer.ingestion.strategies.json_strategy import (
    JSONIngestionStrategy,
)

def test_factory_creates_csv_strategy() -> None:
    strategy = IngestionStrategyFactory.create("expenses.csv")

    assert isinstance(strategy, CSVIngestionStrategy)


def test_factory_creates_json_strategy() -> None:
    strategy = IngestionStrategyFactory.create("expenses.json")

    assert isinstance(strategy, JSONIngestionStrategy)


def test_unsupported_file_type() -> None:
    with pytest.raises(ValueError):
        IngestionStrategyFactory.get_strategy(
            Path("expenses.xml")
        )