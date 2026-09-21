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