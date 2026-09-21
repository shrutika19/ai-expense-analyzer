from pathlib import Path

from expense_analyzer.ml.inference.predictor import (
    CategoryPredictor,
)
from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.loader import ModelBundleLoader


class InferenceService:
    """
    Production inference service.

    Responsibilities:
    - load the requested versioned model
    - delegate prediction to CategoryPredictor

    It knows nothing about model training.
    """

    MODEL_NAME = "expense_category"

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

        self.predictor = CategoryPredictor()

    def predict(
        self,
        prediction: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
        return self.predictor.predict(
            self.model,
            prediction,
        )