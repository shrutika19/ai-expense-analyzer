from enum import Enum
from pathlib import Path

from expense_analyzer.ml.exceptions import (
    MLInferenceError,
    PredictorUnavailableError,
)
from expense_analyzer.ml.inference.predictor import MLPredictor
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader


class ConfidenceLevel(str, Enum):
    """
    Internal classification of prediction confidence.
    """

    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class InferenceService:
    """
    Production inference service.

    Responsibilities:
        - Validate prediction input.
        - Load the server-selected model version.
        - Keep the loaded model in memory.
        - Delegate prediction to MLPredictor.
        - Validate model output.
        - Classify confidence.
        - Translate predictor failures into ML exceptions.

    Low-confidence predictions are not rejected.
    """

    MODEL_NAME = "expense_category"

    def __init__(
        self,
        artifacts_directory: Path | str,
        model_version: str,
        confidence_threshold: float | None = None,
    ) -> None:
        self.model_loader = ModelBundleLoader(
            artifacts_directory
        )

        # Load once during service initialization.
        self.model = self.model_loader.load(
            self.MODEL_NAME,
            model_version,
        )

        self.model_version = model_version
        self.predictor = MLPredictor()
        self.confidence_threshold = confidence_threshold

    def predict(
        self,
        prediction: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
        """
        Run prediction using the already-loaded model.

        Low-confidence predictions are returned normally.
        """

        self._validate_input(prediction)

        try:
            result = self.predictor.predict(
                self.model,
                prediction,
            )

        except MLInferenceError:
            raise

        except Exception as exc:
            raise PredictorUnavailableError(
                "ML predictor is unavailable."
            ) from exc

        self._validate_confidence(result)

        self._classify_confidence(
            result.confidence
        )

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

    @staticmethod
    def _validate_confidence(
        result: CategoryPredictionOutput,
    ) -> None:
        if not 0.0 <= result.confidence <= 1.0:
            raise MLInferenceError(
                "Model returned invalid confidence."
            )

    def _classify_confidence(
        self,
        confidence: float,
    ) -> ConfidenceLevel | None:
        """
        Classify confidence without rejecting the prediction.

        Future behavior:

        confidence >= threshold
            -> HIGH_CONFIDENCE
            -> automatic category assignment

        confidence < threshold
            -> LOW_CONFIDENCE
            -> manual review / fallback workflow
        """

        if self.confidence_threshold is None:
            return None

        if confidence >= self.confidence_threshold:
            return ConfidenceLevel.HIGH_CONFIDENCE

        return ConfidenceLevel.LOW_CONFIDENCE