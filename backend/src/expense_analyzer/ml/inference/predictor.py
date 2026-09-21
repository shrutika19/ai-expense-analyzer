import pandas as pd

from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.model_bundle import ModelBundle


class CategoryPredictor:
    """
    Performs prediction using an already-loaded ModelBundle.

    The predictor does not load or persist models.
    """

    def predict(
        self,
        bundle: ModelBundle,
        prediction: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
        dataframe = pd.DataFrame(
            [
                {
                    "description": prediction.description,
                    "amount": prediction.amount,
                }
            ]
        )

        features = bundle.feature_pipeline.transform(
            dataframe
        )

        predicted_category = bundle.classifier.predict(
            features
        )[0]

        probabilities = bundle.classifier.predict_proba(
            features
        )[0]

        confidence = float(probabilities.max())

        return CategoryPredictionOutput(
            predicted_category=str(predicted_category),
            confidence=confidence,
        )