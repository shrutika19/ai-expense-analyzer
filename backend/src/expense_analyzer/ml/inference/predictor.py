import pandas as pd

from expense_analyzer.ml.models.category_prediction import (
    CategoryPredictionInput,
    CategoryPredictionOutput,
)
from expense_analyzer.ml.models.model_bundle import ModelBundle


SUPPORTED_CATEGORIES = {
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Rent",
    "Travel",
    "Utilities",
    "Other",
}


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
        Validate Model Output
              ↓
        Category + Confidence
    """

    def predict(
        self,
        model_bundle: ModelBundle,
        prediction_input: CategoryPredictionInput,
    ) -> CategoryPredictionOutput:

        # ---------------------------------------------------------
        # 1. Validate model classes
        # ---------------------------------------------------------

        classes = getattr(
            model_bundle.classifier,
            "classes_",
            None,
        )

        if classes is None:
            raise ValueError(
                "Model artifact is incompatible: "
                "classifier.classes_ is missing."
            )

        if len(classes) == 0:
            raise ValueError(
                "Model artifact is incompatible: "
                "classifier.classes_ is empty."
            )

        unsupported_classes = [
            str(category)
            for category in classes
            if str(category) not in SUPPORTED_CATEGORIES
        ]

        if unsupported_classes:
            raise ValueError(
                "Model artifact is incompatible: "
                f"unsupported model classes: {unsupported_classes}"
            )

        # ---------------------------------------------------------
        # 2. Prepare input
        # ---------------------------------------------------------

        dataframe = pd.DataFrame(
            [
                {
                    "description": prediction_input.description,
                    "amount": prediction_input.amount,
                }
            ]
        )

        # ---------------------------------------------------------
        # 3. Transform features using persisted pipeline
        # ---------------------------------------------------------

        features = model_bundle.feature_pipeline.transform(
            dataframe
        )

        # ---------------------------------------------------------
        # 4. Generate prediction
        # ---------------------------------------------------------

        predicted_categories = model_bundle.classifier.predict(
            features
        )

        probabilities = model_bundle.classifier.predict_proba(
            features
        )

        # ---------------------------------------------------------
        # 5. Validate probability output
        # ---------------------------------------------------------

        if probabilities is None:
            raise ValueError(
                "Invalid model output: probability output is missing."
            )

        if len(probabilities) != 1:
            raise ValueError(
                "Invalid model output: expected probabilities "
                "for exactly one prediction."
            )

        probability_row = probabilities[0]

        if len(probability_row) != len(classes):
            raise ValueError(
                "Invalid model output: probability count does not "
                "match the number of model classes."
            )

        if not all(
            isinstance(float(probability), float)
            for probability in probability_row
        ):
            raise ValueError(
                "Invalid model output: probabilities must be numeric."
            )

        if any(
            not 0.0 <= float(probability) <= 1.0
            for probability in probability_row
        ):
            raise ValueError(
                "Invalid model output: probabilities must be "
                "between 0 and 1."
            )

        probability_sum = sum(
            float(probability)
            for probability in probability_row
        )

        if abs(probability_sum - 1.0) > 1e-6:
            raise ValueError(
                "Invalid model output: probabilities must sum to 1."
            )

        # ---------------------------------------------------------
        # 6. Validate predicted category
        # ---------------------------------------------------------

        if len(predicted_categories) != 1:
            raise ValueError(
                "Invalid model output: expected exactly "
                "one predicted category."
            )

        predicted_category = str(predicted_categories[0])

        if predicted_category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                "Invalid model output: "
                f"unsupported predicted category "
                f"'{predicted_category}'."
            )

        # ---------------------------------------------------------
        # 7. Determine confidence
        # ---------------------------------------------------------

        highest_probability_index = probability_row.argmax()

        confidence = float(
            probability_row[highest_probability_index]
        )

        # ---------------------------------------------------------
        # 8. Validate confidence
        # ---------------------------------------------------------

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Invalid model output: confidence must be "
                "between 0 and 1."
            )

        # ---------------------------------------------------------
        # 9. Return validated prediction
        # ---------------------------------------------------------

        return CategoryPredictionOutput(
            predicted_category=predicted_category,
            confidence=confidence,
        )