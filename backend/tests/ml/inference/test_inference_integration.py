import pytest

from expense_analyzer.core.config import get_settings
from expense_analyzer.ml.inference.service import InferenceService
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
)


@pytest.fixture(scope="module")
def inference_service() -> InferenceService:
    """
    Create one real InferenceService for the integration tests.

    No mocks are used here.

    The service loads the real persisted model once and
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

        Real persisted model
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

    # Verify a category was returned.
    assert result.predicted_category

    # Verify confidence is a valid probability.
    assert 0.0 <= result.confidence <= 1.0


def test_real_model_can_process_multiple_predictions(
    inference_service: InferenceService,
) -> None:
    """
    Verify that the same loaded real model can handle
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