from pathlib import Path

from expense_analyzer.ml.inference.predictor import MLPredictor
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader


class InferenceService:
    """
    Production inference service.

    Responsibilities:
        - Validate prediction input.
        - Load the requested versioned model.
        - Delegate prediction to MLPredictor.
        - Apply confidence policy.

    The service does not train models and does not perform
    feature transformation itself.
    """

    MODEL_NAME = "expense_category"
    MIN_CONFIDENCE = 0.70

    def __init__(
        self,
        artifacts_directory: Path | str = "artifacts/models",
        model_version: str | None = None,
    ) -> None:
        self.model_loader = ModelBundleLoader(
            artifacts_directory
        )

        self.model = self.model_loader.load(
            self.MODEL_NAME,
            model_version,
        )

        self.predictor = MLPredictor()

    def predict(
        self,
        prediction: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
        self._validate_input(prediction)

        result = self.predictor.predict(
            self.model,
            prediction,
        )

        self._validate_confidence(result)

        return result

    @staticmethod
    def _validate_input(
        prediction: CategoryPredictionInput,
    ) -> None:
        if not prediction.description.strip():
            raise ValueError(
                "Prediction description cannot be empty."
            )

        if prediction.amount < 0:
            raise ValueError(
                "Prediction amount cannot be negative."
            )

    @classmethod
    def _validate_confidence(
        cls,
        result: CategoryPredictionOutput,
    ) -> None:
        if result.confidence < cls.MIN_CONFIDENCE:
            raise ValueError(
                "Prediction confidence is below the "
                f"minimum threshold of {cls.MIN_CONFIDENCE:.2f}."
            )