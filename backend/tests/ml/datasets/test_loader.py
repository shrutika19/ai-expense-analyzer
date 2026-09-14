import pandas as pd
from unittest.mock import MagicMock, patch

from expense_analyzer.ml.datasets.loader import DatasetLoader


def test_load_returns_expenses_as_dataframe():
    mock_cursor = MagicMock()

    mock_cursor.fetchall.return_value = [
        (
            "Uber ride to office",
            450.00,
            "TRANSPORT",
            "2026-09-01",
        ),
        (
            "Lunch at restaurant",
            650.00,
            "FOOD",
            "2026-09-02",
        ),
    ]

    columns = []

    for name in (
        "description",
        "amount",
        "category",
        "expense_date",
    ):
        column = MagicMock()
        column.name = name
        columns.append(column)

    mock_cursor.description = columns

    mock_connection = MagicMock()

    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    with patch(
        "expense_analyzer.ml.datasets.loader.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            mock_connection
        )

        loader = DatasetLoader()
        dataframe = loader.load()

    assert isinstance(dataframe, pd.DataFrame)

    assert list(dataframe.columns) == [
        "description",
        "amount",
        "category",
        "expense_date",
    ]

    assert len(dataframe) == 2

    assert dataframe.iloc[0]["description"] == "Uber ride to office"
    assert dataframe.iloc[0]["amount"] == 450.00
    assert dataframe.iloc[0]["category"] == "TRANSPORT"
    assert dataframe.iloc[0]["expense_date"] == "2026-09-01"

    assert dataframe.iloc[1]["description"] == "Lunch at restaurant"
    assert dataframe.iloc[1]["amount"] == 650.00
    assert dataframe.iloc[1]["category"] == "FOOD"
    assert dataframe.iloc[1]["expense_date"] == "2026-09-02"

    mock_cursor.execute.assert_called_once()