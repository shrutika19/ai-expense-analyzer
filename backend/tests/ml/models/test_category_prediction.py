import pytest
from pydantic import ValidationError

from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)


def test_valid_description_and_amount():
    prediction = CategoryPredictionInput(
        description="Uber ride to office",
        amount=450.0,
    )

    assert prediction.description == "Uber ride to office"
    assert prediction.amount == 450.0


def test_empty_description_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionInput(
            description="",
            amount=450.0,
        )


def test_description_over_500_characters_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionInput(
            description="a" * 501,
            amount=450.0,
        )


def test_zero_amount_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionInput(
            description="Uber ride",
            amount=0,
        )


def test_negative_amount_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionInput(
            description="Uber ride",
            amount=-100,
        )


def test_valid_prediction_output():
    prediction = CategoryPredictionOutput(
        predicted_category="TRANSPORT",
        confidence=0.94,
    )

    assert prediction.predicted_category == "TRANSPORT"
    assert prediction.confidence == 0.94


def test_confidence_below_zero_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionOutput(
            predicted_category="TRANSPORT",
            confidence=-0.1,
        )


def test_confidence_above_one_rejected():
    with pytest.raises(ValidationError):
        CategoryPredictionOutput(
            predicted_category="TRANSPORT",
            confidence=1.1,
        )