from decimal import Decimal

import pandas as pd
import pytest

from expense_analyzer.ml.datasets.splitter import DatasetSplitter


def create_test_dataframe() -> pd.DataFrame:
    records = []

    categories = [
        "FOOD",
        "TRANSPORT",
        "SHOPPING",
        "ENTERTAINMENT",
    ]

    for category in categories:
        for index in range(25):
            records.append(
                {
                    "description": f"{category} expense {index}",
                    "amount": Decimal("100.00"),
                    "category": category,
                }
            )

    return pd.DataFrame(records)


def test_80_20_split():
    dataframe = create_test_dataframe()

    train_data, test_data = DatasetSplitter().split(dataframe)

    assert len(train_data) == 80
    assert len(test_data) == 20


def test_train_and_test_equal_original_dataset():
    dataframe = create_test_dataframe()

    train_data, test_data = DatasetSplitter().split(dataframe)

    assert len(train_data) + len(test_data) == len(dataframe)


def test_category_proportions_are_preserved():
    dataframe = create_test_dataframe()

    train_data, test_data = DatasetSplitter().split(dataframe)

    original_distribution = (
        dataframe["category"].value_counts(normalize=True)
    )

    train_distribution = (
        train_data["category"].value_counts(normalize=True)
    )

    test_distribution = (
        test_data["category"].value_counts(normalize=True)
    )

    for category in original_distribution.index:
        assert abs(
            train_distribution[category]
            - original_distribution[category]
        ) <= 0.05

        assert abs(
            test_distribution[category]
            - original_distribution[category]
        ) <= 0.05


def test_split_is_reproducible():
    dataframe = create_test_dataframe()

    splitter = DatasetSplitter()

    train_data_1, test_data_1 = splitter.split(dataframe)
    train_data_2, test_data_2 = splitter.split(dataframe)

    pd.testing.assert_frame_equal(
        train_data_1,
        train_data_2,
    )

    pd.testing.assert_frame_equal(
        test_data_1,
        test_data_2,
    )


def test_empty_dataset_rejected():
    dataframe = pd.DataFrame(
        {
            "description": pd.Series(dtype="object"),
            "amount": pd.Series(dtype="float64"),
            "category": pd.Series(dtype="object"),
        }
    )

    with pytest.raises(
        ValueError,
        match="Cannot split an empty dataset",
    ):
        DatasetSplitter().split(dataframe)


def test_missing_category_column_rejected():
    dataframe = pd.DataFrame(
        {
            "description": ["Lunch"],
            "amount": [250.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="category",
    ):
        DatasetSplitter().split(dataframe)


def test_very_small_dataset_rejected():
    dataframe = pd.DataFrame(
        {
            "description": ["Lunch"],
            "amount": [250.0],
            "category": ["FOOD"],
        }
    )

    with pytest.raises(
        ValueError,
    ):
        DatasetSplitter().split(dataframe)