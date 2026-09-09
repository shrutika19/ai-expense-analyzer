from pathlib import Path

from expense_analyzer.ingestion.strategies.json_strategy import (
    JSONIngestionStrategy,
)


def test_json_strategy_reads_expenses() -> None:
    strategy = JSONIngestionStrategy()

    path = Path("tests/fixtures/expenses.json")

    result = strategy.read(path)

    assert len(result) == 2
    assert result[0]["description"] == "Lunch"
    assert result[1]["category"] == "Travel"