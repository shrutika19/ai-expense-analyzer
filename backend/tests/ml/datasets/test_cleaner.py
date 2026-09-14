from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from expense_analyzer.domain.enums.expense_category import ExpenseCategory
from expense_analyzer.ml.datasets.cleaner import DatasetCleaner


def create_test_dataframe() -> pd.DataFrame:
    categories = list(ExpenseCategory)

    return pd.DataFrame(
        {
            "description": [
                "Uber to office",
                "Lunch",
                "Amazon purchase",
                "Netflix",
            ],
            "amount": [
                Decimal("350.00"),
                Decimal("250.00"),
                Decimal("1200.00"),
                Decimal("649.00"),
            ],
            "category": [
                categories[0].value,
                categories[1].value,
                categories[2].value,
                categories[3].value,
            ],
            "expense_date": [
                date(2026, 9, 1),
                date(2026, 9, 2),
                date(2026, 9, 3),
                date(2026, 9, 4),
            ],
        }
    )


def test_missing_description_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "description"] = None

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_empty_description_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "description"] = ""

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_whitespace_only_description_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "description"] = "   "

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_missing_category_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "category"] = None

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_invalid_amount_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "amount"] = -100

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_zero_amount_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "amount"] = 0

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_missing_amount_removed():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "amount"] = None

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 3
    assert result.removed_count == 1


def test_invalid_category_handled():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "category"] = "INVALID_CATEGORY"

    with pytest.raises(
        ValueError,
        match="Unknown expense categories",
    ):
        DatasetCleaner().clean(dataframe)


def test_whitespace_cleaned():
    dataframe = create_test_dataframe()
    dataframe.loc[0, "description"] = "  Uber to office  "

    result = DatasetCleaner().clean(dataframe)

    assert result.dataframe.iloc[0]["description"] == "Uber to office"


def test_exact_duplicates_removed():
    dataframe = create_test_dataframe()

    duplicate = dataframe.iloc[[0]].copy()

    dataframe = pd.concat(
        [dataframe, duplicate],
        ignore_index=True,
    )

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 4
    assert result.removed_count == 1


def test_records_with_different_expense_date_are_preserved():
    dataframe = create_test_dataframe()

    second_expense = dataframe.iloc[[0]].copy()

    second_expense.loc[
        second_expense.index[0],
        "expense_date",
    ] = date(2026, 9, 10)

    dataframe = pd.concat(
        [dataframe, second_expense],
        ignore_index=True,
    )

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 5
    assert result.removed_count == 0


def test_records_with_different_amount_are_preserved():
    dataframe = create_test_dataframe()

    second_expense = dataframe.iloc[[0]].copy()

    second_expense.loc[
        second_expense.index[0],
        "amount",
    ] = Decimal("500.00")

    dataframe = pd.concat(
        [dataframe, second_expense],
        ignore_index=True,
    )

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 5
    assert result.removed_count == 0


def test_records_with_different_category_are_preserved():
    dataframe = create_test_dataframe()

    categories = list(ExpenseCategory)

    # Skip if the enum has fewer than two categories.
    if len(categories) < 2:
        pytest.skip("ExpenseCategory requires at least two categories.")

    second_expense = dataframe.iloc[[0]].copy()

    second_expense.loc[
        second_expense.index[0],
        "category",
    ] = categories[1].value

    dataframe = pd.concat(
        [dataframe, second_expense],
        ignore_index=True,
    )

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 5
    assert result.removed_count == 0


def test_valid_records_preserved():
    dataframe = create_test_dataframe()

    original_count = len(dataframe)

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == original_count
    assert result.removed_count == 0


def test_cleaning_does_not_remove_valid_records():
    dataframe = create_test_dataframe()

    result = DatasetCleaner().clean(dataframe)

    assert len(result.dataframe) == 4

    assert list(result.dataframe["description"]) == [
        "Uber to office",
        "Lunch",
        "Amazon purchase",
        "Netflix",
    ]


def test_original_dataframe_is_not_mutated():
    dataframe = create_test_dataframe()
    original = dataframe.copy(deep=True)

    DatasetCleaner().clean(dataframe)

    pd.testing.assert_frame_equal(
        dataframe,
        original,
    )


def test_unknown_categories_are_reported():
    dataframe = create_test_dataframe()

    dataframe.loc[0, "category"] = "UNKNOWN"

    with pytest.raises(
        ValueError,
        match="Unknown expense categories",
    ):
        DatasetCleaner().clean(dataframe)