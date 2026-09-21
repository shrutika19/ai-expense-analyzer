import pytest
from unittest.mock import Mock, patch

from expense_analyzer.ml.inference.service import InferenceService
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
def test_service_loads_requested_model_version(
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    loader.load.assert_called_once_with(
        "expense_category",
        "v1.0.0",
    )

    assert service.model is bundle


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_delegates_prediction(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    expected_result = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.92,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = expected_result

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result == expected_result

    predictor.predict.assert_called_once_with(
        bundle,
        prediction_input,
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_rejects_empty_description(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="   ",
        amount=25.0,
    )

    with pytest.raises(
        ValueError,
        match="description cannot be empty",
    ):
        service.predict(prediction_input)

    predictor_class.return_value.predict.assert_not_called()


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_rejects_negative_amount(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=-25.0,
    )

    with pytest.raises(
        ValueError,
        match="amount cannot be negative",
    ):
        service.predict(prediction_input)

    predictor_class.return_value.predict.assert_not_called()


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_accepts_prediction_above_confidence_threshold(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    expected_result = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.92,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = expected_result

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result == expected_result

    predictor.predict.assert_called_once_with(
        bundle,
        prediction_input,
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_rejects_prediction_below_confidence_threshold(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    low_confidence_result = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.50,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = low_confidence_result

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    with pytest.raises(
        ValueError,
        match="confidence is below",
    ):
        service.predict(prediction_input)

    predictor.predict.assert_called_once_with(
        bundle,
        prediction_input,
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_accepts_confidence_at_threshold(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    expected_result = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=InferenceService.MIN_CONFIDENCE,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = expected_result

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result == expected_result