from unittest.mock import Mock, patch

import pytest

from expense_analyzer.ml.exceptions import (
    ModelArtifactNotFoundError,
    ModelLoadError,
)
from expense_analyzer.ml.inference.service import (
    ConfidenceLevel,
    InferenceService,
)
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
def test_service_requests_configured_model_version(
    loader_class: Mock,
) -> None:
    """
    Verify that InferenceService requests the exact
    model version configured by the server.
    """

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
    assert service.model_version == "v1.0.0"


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_passes_correct_input_to_predictor(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    Verify that InferenceService passes the loaded model
    and prediction input to MLPredictor.
    """

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

    service.predict(prediction_input)

    predictor.predict.assert_called_once_with(
        bundle,
        prediction_input,
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_returns_predictor_result_unchanged(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    Verify that the prediction returned by MLPredictor
    is returned by InferenceService.
    """

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

    assert result is expected_result


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_returns_low_confidence_prediction(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    Low-confidence predictions are not rejected.

    The prediction is returned so that a later workflow
    can decide whether manual review is required.
    """

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
        confidence_threshold=0.70,
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result is low_confidence_result
    assert result.predicted_category == "Food"
    assert result.confidence == 0.50

    confidence_level = service._classify_confidence(
        result.confidence
    )

    assert (
        confidence_level
        == ConfidenceLevel.LOW_CONFIDENCE
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_classifies_high_confidence_prediction(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    Predictions at or above the configured threshold are
    classified as HIGH_CONFIDENCE.
    """

    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    high_confidence_result = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.90,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = high_confidence_result

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
        confidence_threshold=0.70,
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result is high_confidence_result

    confidence_level = service._classify_confidence(
        result.confidence
    )

    assert (
        confidence_level
        == ConfidenceLevel.HIGH_CONFIDENCE
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_accepts_prediction_at_confidence_threshold(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    A prediction exactly at the threshold is classified
    as HIGH_CONFIDENCE.
    """

    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    result_from_predictor = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.70,
    )

    predictor = predictor_class.return_value
    predictor.predict.return_value = result_from_predictor

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
        confidence_threshold=0.70,
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    result = service.predict(prediction_input)

    assert result is result_from_predictor

    confidence_level = service._classify_confidence(
        result.confidence
    )

    assert (
        confidence_level
        == ConfidenceLevel.HIGH_CONFIDENCE
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
def test_service_converts_model_artifact_not_found_error(
    loader_class: Mock,
) -> None:
    """
    Model artifact failures should remain domain-specific
    ML exceptions and must not expose raw filesystem errors.
    """

    loader = loader_class.return_value

    loader.load.side_effect = ModelArtifactNotFoundError(
        "Model artifact not found."
    )

    with pytest.raises(
        ModelArtifactNotFoundError,
        match="Model artifact not found",
    ):
        InferenceService(
            artifacts_directory="test-artifacts",
            model_version="v1.0.0",
        )

    loader.load.assert_called_once_with(
        "expense_category",
        "v1.0.0",
    )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
def test_service_converts_model_load_error(
    loader_class: Mock,
) -> None:
    """
    Model loading failures should propagate as the
    dedicated ModelLoadError rather than raw joblib errors.
    """

    loader = loader_class.return_value

    loader.load.side_effect = ModelLoadError(
        "Model artifact could not be loaded."
    )

    with pytest.raises(
        ModelLoadError,
        match="Model artifact could not be loaded",
    ):
        InferenceService(
            artifacts_directory="test-artifacts",
            model_version="v1.0.0",
        )


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_does_not_load_model_during_prediction(
    predictor_class: Mock,
    loader_class: Mock,
) -> None:
    """
    Verify Step 6: the model is loaded once during service
    initialization and not loaded again for each prediction.
    """

    bundle = Mock()

    loader = loader_class.return_value
    loader.load.return_value = bundle

    predictor = predictor_class.return_value

    predictor.predict.return_value = CategoryPredictionOutput(
        predicted_category="Food",
        confidence=0.90,
    )

    service = InferenceService(
        artifacts_directory="test-artifacts",
        model_version="v1.0.0",
    )

    prediction_input = CategoryPredictionInput(
        description="restaurant lunch",
        amount=25.0,
    )

    service.predict(prediction_input)
    service.predict(prediction_input)
    service.predict(prediction_input)

    loader.load.assert_called_once_with(
        "expense_category",
        "v1.0.0",
    )

    assert predictor.predict.call_count == 3


@patch("expense_analyzer.ml.inference.service.ModelBundleLoader")
@patch("expense_analyzer.ml.inference.service.MLPredictor")
def test_service_records_latency_and_low_confidence_telemetry(
    predictor_class: Mock, loader_class: Mock,
) -> None:
    loader_class.return_value.load.return_value = Mock(classifier=Mock(), feature_pipeline=Mock())
    predictor_class.return_value.predict.return_value = CategoryPredictionOutput(
        predicted_category="Food", confidence=0.4,
    )
    service = InferenceService("test-artifacts", "v1.0.0", confidence_threshold=0.7)

    service.predict(CategoryPredictionInput(description="lunch", amount=10))

    metrics = service.telemetry.snapshot("v1.0.0")
    assert metrics["prediction_count"] == 1
    assert metrics["low_confidence_count"] == 1
    assert metrics["average_inference_latency_ms"] is not None
    assert service.readiness()["ready"] is True
