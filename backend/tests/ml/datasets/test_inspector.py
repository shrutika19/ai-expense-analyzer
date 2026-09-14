import pandas as pd

from expense_analyzer.ml.datasets.inspector import DatasetInspector


def create_test_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description": [
                "Uber to office",
                "Lunch",
                "Amazon purchase",
                "Netflix",
            ],
            "amount": [
                350.0,
                250.0,
                1200.0,
                649.0,
            ],
            "category": [
                "TRANSPORT",
                "FOOD",
                "SHOPPING",
                "ENTERTAINMENT",
            ],
        }
    )


def test_correct_row_count():
    dataframe = create_test_dataframe()

    result = DatasetInspector().inspect(dataframe)

    assert result.row_count == 4


def test_correct_column_count():
    dataframe = create_test_dataframe()

    result = DatasetInspector().inspect(dataframe)

    assert result.column_count == 3


def test_missing_values_detected():
    dataframe = create_test_dataframe()
    dataframe.loc[1, "description"] = None
    dataframe.loc[2, "amount"] = None

    result = DatasetInspector().inspect(dataframe)

    assert result.missing_values["description"].missing_count == 1
    assert result.missing_values["description"].missing_percentage == 25.0

    assert result.missing_values["amount"].missing_count == 1
    assert result.missing_values["amount"].missing_percentage == 25.0

    assert result.missing_values["category"].missing_count == 0


def test_category_distribution_calculated():
    dataframe = create_test_dataframe()

    result = DatasetInspector().inspect(dataframe)

    assert result.category_distribution["TRANSPORT"].record_count == 1
    assert result.category_distribution["TRANSPORT"].percentage == 25.0

    assert result.category_distribution["FOOD"].record_count == 1
    assert result.category_distribution["FOOD"].percentage == 25.0

    assert result.category_distribution["SHOPPING"].record_count == 1
    assert result.category_distribution["SHOPPING"].percentage == 25.0

    assert (
        result.category_distribution["ENTERTAINMENT"].record_count == 1
    )
    assert (
        result.category_distribution["ENTERTAINMENT"].percentage == 25.0
    )


def test_duplicates_detected():
    dataframe = create_test_dataframe()

    dataframe.loc[4] = dataframe.loc[0]

    result = DatasetInspector().inspect(dataframe)

    assert result.duplicate_count == 1


def test_amount_statistics_calculated():
    dataframe = create_test_dataframe()

    result = DatasetInspector().inspect(dataframe)

    assert result.amount_statistics.min == 250.0
    assert result.amount_statistics.max == 1200.0
    assert result.amount_statistics.mean == 612.25


def test_empty_dataset_handled():
    dataframe = pd.DataFrame(
        {
            "description": pd.Series(dtype="object"),
            "amount": pd.Series(dtype="float64"),
            "category": pd.Series(dtype="object"),
        }
    )

    result = DatasetInspector().inspect(dataframe)

    assert result.row_count == 0
    assert result.column_count == 3

    assert result.missing_values["description"].missing_count == 0
    assert result.missing_values["description"].missing_percentage == 0.0

    assert result.missing_values["amount"].missing_count == 0
    assert result.missing_values["amount"].missing_percentage == 0.0

    assert result.missing_values["category"].missing_count == 0
    assert result.missing_values["category"].missing_percentage == 0.0

    assert result.category_distribution == {}
    assert result.duplicate_count == 0
    