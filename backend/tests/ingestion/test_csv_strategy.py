from pathlib import Path

from expense_analyzer.ingestion.strategies.csv_strategy import (
    CSVIngestionStrategy,
)


def test_csv_strategy_reads_expenses() -> None:
    strategy = CSVIngestionStrategy()

    path = Path("tests/fixtures/expenses.csv")

    result = strategy.read(path)

    assert len(result) == 2
    assert result[0]["description"] == "Lunch"
    assert result[1]["category"] == "Travel"