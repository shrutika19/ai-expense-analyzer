from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from expense_analyzer.ml.features.numerical_features import (
    AmountFeatureTransformer,
)


def test_positive_amount():
    amounts = pd.Series([100.0])

    transformer = AmountFeatureTransformer()

    result = transformer.transform(amounts)

    assert result.shape == (1, 1)
    assert result[0, 0] == 100.0


def test_decimal_amount():
    amounts = pd.Series(
        [
            Decimal("350.50"),
            Decimal("1250.75"),
        ]
    )

    transformer = AmountFeatureTransformer()

    result = transformer.transform(amounts)

    assert result.shape == (2, 1)
    assert result[0, 0] == 350.50
    assert result[1, 0] == 1250.75


def test_multiple_records():
    amounts = pd.Series(
        [
            100.0,
            250.0,
            500.0,
            1000.0,
        ]
    )

    transformer = AmountFeatureTransformer()

    result = transformer.transform(amounts)

    assert result.shape == (4, 1)
    np.testing.assert_array_equal(
        result.flatten(),
        [100.0, 250.0, 500.0, 1000.0],
    )


def test_invalid_amount_rejected():
    amounts = pd.Series(
        [
            100.0,
            "invalid",
            500.0,
        ]
    )

    transformer = AmountFeatureTransformer()

    with pytest.raises(
        ValueError,
        match="valid numeric values",
    ):
        transformer.transform(amounts)


def test_missing_amount_rejected():
    amounts = pd.Series(
        [
            100.0,
            None,
            500.0,
        ]
    )

    transformer = AmountFeatureTransformer()

    with pytest.raises(
        ValueError,
        match="missing values",
    ):
        transformer.transform(amounts)


def test_zero_amount_rejected():
    amounts = pd.Series(
        [
            100.0,
            0.0,
            500.0,
        ]
    )

    transformer = AmountFeatureTransformer()

    with pytest.raises(
        ValueError,
        match="positive values",
    ):
        transformer.transform(amounts)


def test_negative_amount_rejected():
    amounts = pd.Series(
        [
            100.0,
            -50.0,
            500.0,
        ]
    )

    transformer = AmountFeatureTransformer()

    with pytest.raises(
        ValueError,
        match="positive values",
    ):
        transformer.transform(amounts)


def test_row_count_preserved():
    amounts = pd.Series(
        [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("300.00"),
            Decimal("400.00"),
            Decimal("500.00"),
        ]
    )

    transformer = AmountFeatureTransformer()

    result = transformer.transform(amounts)

    assert result.shape[0] == len(amounts)


def test_row_alignment_is_preserved():
    amounts = pd.Series(
        [
            Decimal("100.00"),
            Decimal("250.00"),
            Decimal("750.00"),
        ],
        index=[10, 20, 30],
    )

    transformer = AmountFeatureTransformer()

    result = transformer.transform(amounts)

    assert result.flatten().tolist() == [
        100.0,
        250.0,
        750.0,
    ]