import numpy as np
import pytest
from unittest.mock import Mock

from expense_analyzer.ml.inference.predictor import MLPredictor
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)


@pytest.fixture
def predictor() -> MLPredictor:
    return MLPredictor()


@pytest.fixture
def model_bundle() -> Mock:
    bundle = Mock()

    bundle.classifier.classes_ = np.array(
        [
            "Bills",
            "Entertainment",
            "Food",
            "Healthcare",
            "Other",
            "Shopping",
            "Transport",
        ]
    )

    bundle.feature_pipeline.transform.return_value = Mock()

    return bundle


def create_prediction_input(
    description: str = "restaurant lunch",
    amount: float = 25.0,
) -> CategoryPredictionInput:
    return CategoryPredictionInput(
        description=description,
        amount=amount,
    )


def configure_prediction(
    model_bundle: Mock,
    predicted_category: str = "Food",
    probabilities: list[float] | None = None,
) -> None:
    if probabilities is None:
        probabilities = [
            0.02,  # Bills
            0.03,  # Entertainment
            0.92,  # Food
            0.01,  # Healthcare
            0.01,  # Other
            0.005,  # Shopping
            0.005,  # Transport
        ]

    model_bundle.classifier.predict.return_value = np.array(
        [predicted_category]
    )

    model_bundle.classifier.predict_proba.return_value = np.array(
        [probabilities]
    )


def test_predictor_accepts_valid_description_and_amount(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input(
        description="restaurant lunch",
        amount=25.0,
    )

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"
    assert 0.0 <= result.confidence <= 1.0


def test_predictor_returns_correct_predicted_category(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(
        model_bundle,
        predicted_category="Food",
    )

    prediction_input = create_prediction_input()

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"


def test_predictor_returns_confidence(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input()

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.confidence == pytest.approx(0.92)


def test_predictor_confidence_is_between_zero_and_one(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input()

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert 0.0 <= result.confidence <= 1.0


def test_highest_probability_corresponds_to_prediction(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    probabilities = [
        0.02,   # Bills
        0.03,   # Entertainment
        0.92,   # Food
        0.01,   # Healthcare
        0.01,   # Other
        0.005,  # Shopping
        0.005,  # Transport
    ]

    configure_prediction(
        model_bundle,
        predicted_category="Food",
        probabilities=probabilities,
    )

    prediction_input = create_prediction_input()

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    highest_index = np.argmax(probabilities)
    highest_category = model_bundle.classifier.classes_[
        highest_index
    ]

    assert result.predicted_category == highest_category
    assert result.confidence == pytest.approx(
        probabilities[highest_index]
    )


def test_predictor_handles_unknown_words(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input(
        description="xyzabc qwerty unknownword",
        amount=25.0,
    )

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"
    assert 0.0 <= result.confidence <= 1.0

    model_bundle.feature_pipeline.transform.assert_called_once()


def test_predictor_handles_unusual_description(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input(
        description="!!! @@@ ### coffee ☕ ???",
        amount=12.50,
    )

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.parametrize(
    "amount",
    [
        0.0,
        1.0,
        25.50,
        999.99,
        100000.0,
    ],
)
def test_predictor_handles_different_amounts(
    predictor: MLPredictor,
    model_bundle: Mock,
    amount: float,
) -> None:
    configure_prediction(model_bundle)

    prediction_input = create_prediction_input(
        description="restaurant lunch",
        amount=amount,
    )

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert result.predicted_category == "Food"
    assert 0.0 <= result.confidence <= 1.0


def test_predictor_rejects_invalid_model_classes(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.classes_ = np.array(
        [
            "Food",
            "InvalidCategory",
        ]
    )

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="unsupported model classes",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_rejects_missing_model_classes(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    del model_bundle.classifier.classes_

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="classifier.classes_ is missing",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_rejects_empty_model_classes(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.classes_ = np.array([])

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="classifier.classes_ is empty",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_handles_model_prediction_failure(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.predict.side_effect = RuntimeError(
        "Model prediction failed"
    )

    prediction_input = create_prediction_input()

    with pytest.raises(
        RuntimeError,
        match="Model prediction failed",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_rejects_probability_count_mismatch(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.predict.return_value = np.array(
        ["Food"]
    )

    model_bundle.classifier.predict_proba.return_value = np.array(
        [[0.90, 0.10]]
    )

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="probability count does not match",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_rejects_probabilities_outside_valid_range(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.predict.return_value = np.array(
        ["Food"]
    )

    model_bundle.classifier.predict_proba.return_value = np.array(
        [[0.95, 0.10, -0.05, 0.0, 0.0, 0.0, 0.0]]
    )

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="probabilities must be between 0 and 1",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )


def test_predictor_rejects_probabilities_not_summing_to_one(
    predictor: MLPredictor,
    model_bundle: Mock,
) -> None:
    model_bundle.classifier.predict.return_value = np.array(
        ["Food"]
    )

    model_bundle.classifier.predict_proba.return_value = np.array(
        [[0.50, 0.20, 0.10, 0.05, 0.05, 0.05, 0.10]]
    )

    prediction_input = create_prediction_input()

    with pytest.raises(
        ValueError,
        match="probabilities must sum to 1",
    ):
        predictor.predict(
            model_bundle,
            prediction_input,
        )