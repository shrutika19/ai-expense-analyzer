from dataclasses import dataclass

import pandas as pd
from sklearn.linear_model import LogisticRegression

from expense_analyzer.ml.features.feature_pipeline import (
    FeaturePipeline,
)


@dataclass(frozen=True)
class BaselinePrediction:
    predicted_categories: list[str]


@dataclass(frozen=True)
class CategoryPrediction:
    predicted_category: str
    confidence: float


class CategoryBaselineExperiment:
    """
    Baseline expense-category classification experiment.

    Pipeline:

        Description
             ↓
           TF-IDF
             ↓
      Logistic Regression
             ↓
    Category + Probability
    """

    def __init__(
        self,
        feature_pipeline: FeaturePipeline | None = None,
    ) -> None:
        self.feature_pipeline = (
            feature_pipeline
            or FeaturePipeline(include_amount=False)
        )

        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
        )

        self._is_trained = False

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> None:
        """
        Train the TF-IDF + Logistic Regression baseline.

        TF-IDF is fitted ONLY on training data.
        """

        if X_train.empty:
            raise ValueError(
                "Training data cannot be empty."
            )

        if y_train.empty:
            raise ValueError(
                "Training target cannot be empty."
            )

        if len(X_train) != len(y_train):
            raise ValueError(
                "Training features and target must have "
                "the same number of rows."
            )

        if y_train.isna().any():
            raise ValueError(
                "Training target cannot contain missing values."
            )

        X_train_features = (
            self.feature_pipeline.fit_transform(
                X_train
            )
        )

        self.classifier.fit(
            X_train_features,
            y_train,
        )

        self._is_trained = True

    def predict(
        self,
        X_test: pd.DataFrame,
    ) -> BaselinePrediction:
        """
        Predict expense categories.

        Returns one category for each input row.
        """

        self._ensure_trained()

        if X_test.empty:
            raise ValueError(
                "Prediction data cannot be empty."
            )

        X_test_features = (
            self.feature_pipeline.transform(
                X_test
            )
        )

        predictions = self.classifier.predict(
            X_test_features
        )

        return BaselinePrediction(
            predicted_categories=predictions.tolist()
        )

    def predict_proba(
        self,
        X_test: pd.DataFrame,
    ) -> list[list[float]]:
        """
        Return probability distribution for each input row.

        The probability order follows classifier.classes_.
        """

        self._ensure_trained()

        if X_test.empty:
            raise ValueError(
                "Prediction data cannot be empty."
            )

        X_test_features = (
            self.feature_pipeline.transform(
                X_test
            )
        )

        probabilities = (
            self.classifier.predict_proba(
                X_test_features
            )
        )

        return probabilities.tolist()

    def predict_with_confidence(
        self,
        X_test: pd.DataFrame,
    ) -> list[CategoryPrediction]:
        """
        Return predicted category and confidence.

        Confidence is the probability assigned to
        the predicted class.
        """

        self._ensure_trained()

        if X_test.empty:
            raise ValueError(
                "Prediction data cannot be empty."
            )

        X_test_features = (
            self.feature_pipeline.transform(
                X_test
            )
        )

        predictions = self.classifier.predict(
            X_test_features
        )

        probabilities = (
            self.classifier.predict_proba(
                X_test_features
            )
        )

        classes = list(
            self.classifier.classes_
        )

        results: list[CategoryPrediction] = []

        for prediction, probability_row in zip(
            predictions,
            probabilities,
        ):
            predicted_index = classes.index(
                prediction
            )

            confidence = float(
                probability_row[predicted_index]
            )

            results.append(
                CategoryPrediction(
                    predicted_category=str(
                        prediction
                    ),
                    confidence=confidence,
                )
            )

        return results

    def _ensure_trained(self) -> None:
        """
        Ensure the model has been trained before inference.
        """

        if not self._is_trained:
            raise RuntimeError(
                "Model must be trained before prediction."
            )