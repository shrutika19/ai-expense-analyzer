import pandas as pd
import pytest

from expense_analyzer.core.config import get_settings
from expense_analyzer.ml.inference.predictor import MLPredictor
from expense_analyzer.ml.inference.service import InferenceService
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader


@pytest.fixture(scope="module")
def inference_service() -> InferenceService:
    """
    Create one real InferenceService for the integration tests.

    No mocks are used here.

    The service loads the deterministic test model once and
    reuses it across the integration tests.
    """
    settings = get_settings()

    try:
        return InferenceService(
            artifacts_directory=settings.model_artifacts_directory,
            model_version=settings.model_version,
        )
    except Exception as error:
        pytest.fail(
            "Could not load the real persisted model for "
            f"integration testing: {error}"
        )


@pytest.fixture(scope="module")
def model_bundle():
    """
    Load the deterministic test model bundle once.
    """
    settings = get_settings()

    try:
        return ModelBundleLoader(
            settings.model_artifacts_directory
        ).load(
            "expense_category",
            settings.model_version,
        )
    except Exception as error:
        pytest.fail(
            "Could not load the test model bundle: "
            f"{error}"
        )


@pytest.mark.parametrize(
    "description, amount",
    [
        ("Uber ride to office", 250.0),
        ("Restaurant dinner", 850.0),
        ("Netflix subscription", 649.0),
        ("Electricity bill", 1800.0),
    ],
)
def test_real_model_produces_valid_prediction(
    inference_service: InferenceService,
    description: str,
    amount: float,
) -> None:
    """
    Verify the complete real inference flow:

        Real test model
                ↓
        Real ModelBundleLoader
                ↓
        Real InferenceService
                ↓
        Real MLPredictor
                ↓
        Real prediction
    """
    prediction_input = CategoryPredictionInput(
        description=description,
        amount=amount,
    )

    result = inference_service.predict(
        prediction_input
    )

    assert result.predicted_category
    assert 0.0 <= result.confidence <= 1.0


def test_real_model_can_process_multiple_predictions(
    inference_service: InferenceService,
) -> None:
    """
    Verify that the same loaded real model can process
    multiple predictions without being reloaded.
    """
    inputs = [
        CategoryPredictionInput(
            description="Uber ride to office",
            amount=250.0,
        ),
        CategoryPredictionInput(
            description="Restaurant dinner",
            amount=850.0,
        ),
        CategoryPredictionInput(
            description="Netflix subscription",
            amount=649.0,
        ),
        CategoryPredictionInput(
            description="Electricity bill",
            amount=1800.0,
        ),
    ]

    results = [
        inference_service.predict(prediction)
        for prediction in inputs
    ]

    assert len(results) == len(inputs)

    for result in results:
        assert result.predicted_category
        assert 0.0 <= result.confidence <= 1.0


def test_prediction_confidence_matches_predicted_category_probability(
    model_bundle,
) -> None:
    prediction_input = CategoryPredictionInput(
        description="Uber ride to office",
        amount=250.0,
    )

    predictor = MLPredictor()

    result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    dataframe = pd.DataFrame(
        [
            {
                "description": prediction_input.description,
                "amount": prediction_input.amount,
            }
        ]
    )

    features = model_bundle.feature_pipeline.transform(
        dataframe
    )

    probabilities = model_bundle.classifier.predict_proba(
        features
    )

    classes = model_bundle.classifier.classes_

    predicted_category_index = list(classes).index(
        result.predicted_category
    )

    expected_confidence = float(
        probabilities[0][predicted_category_index]
    )

    assert result.confidence == pytest.approx(
        expected_confidence,
        abs=1e-6,
    )


def test_inference_is_deterministic_for_same_input(
    model_bundle,
) -> None:
    predictor = MLPredictor()

    prediction_input = CategoryPredictionInput(
        description="Uber ride to office",
        amount=250.0,
    )

    first_result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    second_result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    third_result = predictor.predict(
        model_bundle,
        prediction_input,
    )

    assert (
        first_result.predicted_category
        == second_result.predicted_category
    )

    assert (
        second_result.predicted_category
        == third_result.predicted_category
    )

    assert (
        first_result.confidence
        == second_result.confidence
    )

    assert (
        second_result.confidence
        == third_result.confidence
    )