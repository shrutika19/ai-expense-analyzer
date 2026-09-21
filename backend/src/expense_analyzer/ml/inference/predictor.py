import pandas as pd

from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.model_bundle import ModelBundle


class MLPredictor:
    """
    Performs inference using a persisted ModelBundle.

    The predictor never trains or modifies the model.

    Flow:

        Prediction Input
              ↓
        Feature Transformation
              ↓
        model.predict()
              ↓
        model.predict_proba()
              ↓
        Category + Confidence
    """

    def predict(
        self,
        model_bundle: ModelBundle,
        prediction_input: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:
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

        predicted_categories = model_bundle.classifier.predict(
            features
        )

        probabilities = model_bundle.classifier.predict_proba(
            features
        )

        highest_probability_index = probabilities[0].argmax()

        predicted_category = predicted_categories[0]

        confidence = float(
            probabilities[0][highest_probability_index]
        )

        return CategoryPredictionOutput(
            predicted_category=str(predicted_category),
            confidence=confidence,
        )