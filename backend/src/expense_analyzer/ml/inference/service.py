from enum import Enum
import logging
from pathlib import Path
from time import perf_counter

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
from expense_analyzer.ml.inference.telemetry import InferenceTelemetry

logger = logging.getLogger(__name__)


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
        model_name: str = "expense_category",
    ) -> None:
        self.model_loader = ModelBundleLoader(
            artifacts_directory
        )

        # Load once during service initialization.
        self.model_name = model_name
        self.model = self.model_loader.load(
            self.model_name,
            model_version,
        )

        self.model_version = model_version
        self.predictor = MLPredictor()
        self.confidence_threshold = confidence_threshold
        self.telemetry = InferenceTelemetry()

    def predict(
        self,
        prediction: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
        """
        Run prediction using the already-loaded model.

        Low-confidence predictions are returned normally.
        """

        self._validate_input(prediction)

        started_at = perf_counter()
        try:
            result = self.predictor.predict(
                self.model,
                prediction,
            )

        except MLInferenceError:
            self.telemetry.record_failure()
            logger.exception("ml_inference_failure model_version=%s", self.model_version)
            raise

        except Exception as exc:
            self.telemetry.record_failure()
            logger.exception("ml_inference_failure model_version=%s", self.model_version)
            raise PredictorUnavailableError(
                "ML predictor is unavailable."
            ) from exc

        self._validate_confidence(result)

        level = self._classify_confidence(result.confidence)
        latency_ms = (perf_counter() - started_at) * 1000
        self.telemetry.record_prediction(latency_ms, level == ConfidenceLevel.LOW_CONFIDENCE)
        logger.info("ml_prediction_event model_version=%s predicted_category=%s confidence=%.6f latency_ms=%.3f fallback_used=false",
                    self.model_version, result.predicted_category, result.confidence, latency_ms)

        return result

    def readiness(self) -> dict:
        return {"ready": self.model is not None and getattr(self.model, "classifier", None) is not None
                and getattr(self.model, "feature_pipeline", None) is not None,
                "model_name": self.model_name, "model_version": self.model_version}

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
